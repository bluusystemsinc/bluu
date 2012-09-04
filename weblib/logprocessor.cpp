#include "logprocessor.h"
#include "log.h"
#include "errorreport.h"
#include "core.h"
#include <QtGui>
#include "weblogger.h"
#include "logmousehandler.h"
#include <iostream>

#define QTHANDLER_IDENTIFIER  "qt"
#define LOGFILENAME "log.txt"

LogProcessor::LogProcessor(QObject *parent) :
    QObject(parent)
  ,m_weblogger(0)
  ,m_heartbeat(0)
  ,m_useFilters(false)
{
    initServices();
    connect (this, SIGNAL(internalMessage(int,QString)), this, SLOT(internalMessageSlot(int,QString)), Qt::QueuedConnection);
}


LogProcessor::~LogProcessor()
{
}


void LogProcessor::setContextSize(int size)
{
    m_context_size = size;
}


void LogProcessor::setMouseEventFile(QString file)
{
    if (!file.isEmpty()) {
        m_mouseEventFile = file;
        m_mouseEventSeparated = true;
    } else {
        m_mouseEventSeparated = false;
    }
}


void LogProcessor::setHeartbeatInterval(int heartbeatDelay)
{
    m_heartbeatDelay = heartbeatDelay;
}


void LogProcessor::initServices()
{
    if (!m_weblogger) {
        QString url = gCore->settingValue("Log/webServiceURL", "https://*******.com/").toString();
        m_weblogger = new WebLogger(this, url);
        connect (m_weblogger, SIGNAL(logMessage(int,QString)), this, SLOT(webLoggerMessage(int,QString)), Qt::QueuedConnection);
    }

    int m_heartbeatDelay = gCore->settingValue("Log/heartbeatDelay", 15).toInt() * 1000;
    if (!m_heartbeat && m_heartbeatDelay > 0 ) {
        m_heartbeat = new QTimer(this);
        connect(m_heartbeat, SIGNAL(timeout()), this, SLOT(heartbeatProcessing()));
        m_heartbeat->start(m_heartbeatDelay);
        heartbeatProcessing();
    }
}


void LogProcessor::log_console(QString message)
{
    std::cout <<  message.toStdString() << std::endl;
}

void LogProcessor::put(int logLevel, const QString &message, const QString &_module, const QString &_submodule)
{
    QString _message(message);

    if (m_useFilters) {
        foreach (Log::Filter filter, m_filters)
            _message.replace(filter.re, filter.replace);
    }

    Log::Destination dest;

    if (m_modulesSettings.contains(_module+"_"+_submodule)) {
        if (m_modulesSettings.value(_module+"_"+_submodule).levels.contains(logLevel))
            dest = m_modulesSettings.value(_module).destinations.value(logLevel);
        else
            return;
    }
    else if (m_modulesSettings.contains(_module)) {
        if (m_modulesSettings.value(_module).levels.contains(logLevel))
            dest = m_modulesSettings.value(_module).destinations.value(logLevel);
        else
            return;
    } else {
        if (m_generalSettings.levels.contains(logLevel))
            dest = m_generalSettings.destinations.value(logLevel);
        else
            return;
    }

    QString strLevel = Log::LogLevelNames.value(logLevel);

    if (dest.console) {
        log_console(QTime::currentTime().toString("HH:mm:ss \t") + _module + "::" + _submodule + " \t" + message );
    }

    if (dest.mail) {
        ErrorReport::SendEmail(QString("%1|%2|%3").arg(_submodule).arg(_module).arg(_message), gCore);
    }

    if (dest.file) {
        /// write mouse metric to separated file if needed
        QFile log(m_mouseEventSeparated && logLevel == Log::logMetric ? m_mouseEventFile : LOGFILENAME);
        if (log.open(QFile::WriteOnly| QFile::Append)) {
            QTextStream out(&log);
            QString date = dest.needLogfileTimestamp ? QDateTime::currentDateTime().toString("yyyy-MM-dd hh:mm:ss") : "";
            out << QString("%1 | %2 | %3 | %4").arg(date).arg(_submodule).arg(_module).arg(_message) << '\n';
            log.close();
        }
    }

    if (dest.web) {
        QVariantMap values;
        values.insert("module", _module);
        values.insert("message", _message);
        values.insert("submodule", _submodule);
        values.insert("device_mac", gCore->deviceID());
        values.insert("restaurant_code", gCore->settingValue("RestaurantId").toString());
        values.insert("table", gCore->settingValue("TableNum/Value", "N/A").toString());
        values.insert("waiter",gCore->settingValue("ServerNum/Value", "N/A").toString());
        values.insert("operating_system", gCore->osInfo());
        values.insert("device_local_ip",gCore->IPaddresses().join(";"));
        values.insert("client_timestamp",QDateTime::currentDateTime().toString("yyyy-MM-dd hh:mm:ss"));
        values.insert("loglevel", strLevel);
        values.insert("software_version", gCore->version());
        values.insert("pos_check_number", gCore->settingValue("CheckNum/Value").toString());

        if (dest.needContext) {
            QByteArray ba;
            ba.append(getContext());
            values.insert("context", ba.toBase64());
        }

        if (logLevel == Log::logCritical && _message == QString("crash detected")) {
            QByteArray ba = getCrashdump();
            values.insert("stackdump", ba.toBase64());
        }

        m_weblogger->send(Log::LogLevel(logLevel), values);

        /// removing long fields for lof to console
        values.insert("context", "");
        values.insert("stackdump","");

        emit internalMessage(Log::logDebug, QString("json query: %1").arg(m_weblogger->convertToJson(values)));
    }
}


void LogProcessor::setFilters(QList <Log::Filter> filters)
{
    m_filters = filters;
    m_useFilters = m_filters.isEmpty() ? false : true;
}


void LogProcessor::setGeneralMatrix(Log::Module settings)
{
    m_generalSettings = settings;
}


void LogProcessor::setModulesMatrix(QHash<QString, Log::Module> matrix)
{
    m_modulesSettings = matrix;
}


QString LogProcessor::getContext()
{
    QString result;
    QFile log(LOGFILENAME);

    if (!log.exists())
        return "--Log file doesn't exist...--";

    if (log.open(QIODevice::ReadOnly)) {
        qint64 filesize = log.size();
        qint64 seekpos = filesize > m_context_size ? filesize - m_context_size: 0;
        bool seekresult;
        if (seekpos > 0)
            seekresult = log.seek(seekpos);
        if (seekresult) {       // in some cases file can't be seeked. we need to prevent from uploading too big pieace of file
            result = log.readAll();
        } else {
            result = QString("#### file can't be seeked -- filesize is %1 ###").arg(filesize);
        }

        log.close();
    }
    return result;
}


QByteArray LogProcessor::getCrashdump(bool* repeat)
{
    std::cout << "Log::getCrashdump()" << std::endl;
    QByteArray result;

    QDir dir(CRASHDUMP_DIR);
    QStringList filters;
    filters << "*.dmp";
    QStringList files = dir.entryList(filters, QDir::Files|QDir::NoSymLinks|QDir::NoDotAndDotDot);

    if (files.count() > 1 && repeat != 0)
        *repeat = true;

    if (files.count() == 0)
        return result;

    QFile crashfile(QString(CRASHDUMP_DIR) + "/" + files.first());

    std::cout <<  "############################################################################################" << std::endl;
    std::cout <<  crashfile.fileName().toStdString() << std::endl;

    if (!crashfile.exists())
        return result;

    if (crashfile.open(QIODevice::ReadOnly)) {
        result = crashfile.readAll();
        crashfile.close();
    }

    crashfile.remove();

    return result;
}


void LogProcessor::heartbeatProcessing()
{
    put(Log::logVerbose, "==Heartbeat", LOGMODULE, "logProcessor");

    QVariantMap values;
    values.insert("device_mac", gCore->deviceID());
    values.insert("restaurant_code", gCore->settingValue("RestaurantId").toString());
    values.insert("client_timestamp",QDateTime::currentDateTime().toString("yyyy-MM-dd hh:mm:ss"));
    m_weblogger->sendHeartbeat(values);

    put(Log::logVerbose, QString("json query: %1").arg(m_weblogger->convertToJson(values)), LOGMODULE, "logProcessor");
}


void LogProcessor::webLoggerMessage(int level, QString message)
{
    this->put(level, message, LOGMODULE, "WebLogger");
}


void LogProcessor::internalMessageSlot(int level, QString message)
{
    this->put(level, message, LOGMODULE, "LogProcessor");
}
