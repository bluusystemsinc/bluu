#include "log.h"
#include "weblogger.h"
#include "errorreport.h"
#include "core.h"
#include <QtGui>
#include "webstorage.h"
#include "weblogger.h"
#include "logmousehandler.h"
#include <iostream>
#include "logprocessor.h"

#ifdef USE_SNAPPY
#include "snappy.h"
#endif

#define QTHANDLER_IDENTIFIER  "qt"
#define LOGFILENAME "log.txt"


Log *Log::pInstance = 0;
QHash<int, QString> Log::LogLevelNames;

Log * Log::instance()
{
    if (!Log::pInstance)
        createInstance();
    return Log::pInstance;
}


Log * Log::createInstance()
{
    if (!Log::pInstance)
        Log::pInstance = new Log();
    return Log::pInstance;
}


Log::Log(QObject *parent) :
    QObject(parent)
  , m_mouseHandler(0)
  , m_isInited (false)
  , m_sync(false)
//  , m_useFilters (false)
  , m_processorThread (0)
{
    qDebug("Log CONSTRUCTOR");

    LogLevelNames.insert(Log::logError, "error");
    LogLevelNames.insert(Log::logWarning, "warning");
    LogLevelNames.insert(Log::logInfo, "info");
    LogLevelNames.insert(Log::logDebug, "debug");
    LogLevelNames.insert(Log::logCritical, "critical");
    LogLevelNames.insert(Log::logMetric, "metric");
    LogLevelNames.insert(Log::logVerbose, "debug1");

    QTimer::singleShot(0, this, SLOT(initMe()));
}


Log::~Log()
{
    stopCustomHandler();
    if (m_mouseHandler)
        delete m_mouseHandler;

    if (m_logProcessor)
        delete m_logProcessor;
}


void Log::initMe()
{
    setDefaultConfig();

    m_interceptMouseEvents = gCore->settingValue("Log/mouseEvents", false).toBool();
    m_interceptQtMessages = gCore->settingValue("Log/messagesQt", false).toBool();
    m_logRotateCounter = gCore->settingValue("Log/logRotateCounter").toLongLong();
    QString logRotateFileSize = gCore->settingValue("Log/logRotateFileSize").toString();
    if (logRotateFileSize.contains("kb", Qt::CaseInsensitive))
        m_logRotateFileSize = logRotateFileSize.remove("kb", Qt::CaseInsensitive).toInt() * 1024;
    else if (logRotateFileSize.contains("mb", Qt::CaseInsensitive))
        m_logRotateFileSize = logRotateFileSize.remove("mb", Qt::CaseInsensitive).toInt() * 1024000;
    else
        m_logRotateFileSize = logRotateFileSize.toInt();

    m_sync = gCore->settingValue("Log/synchronously", false).toBool();

    m_isInited = true;

    /// do logrotate if needed
    logRotate();

    /// process it after exit from Core::init because gCore->scene() is not inited yet
    if (m_interceptMouseEvents)
        QTimer::singleShot(0, this, SLOT(initMouseHandler()));


    /// Setting up the qDebug handler only after m_isInited = true ensures that
    /// qDebug statements within the logger initialization don't cause stack (as
    /// warnings need to be logged if a log call is made during logger init.)
    if (m_interceptQtMessages)
            startCustomHandler();

    if (gCore->settingValue("Log/enabled", true).toBool()) {
        QString context_size = gCore->settingValue("Log/contextMaxSize").toString();
        int s = 0;
        if (context_size.contains("kb", Qt::CaseInsensitive))
            s = context_size.remove("kb", Qt::CaseInsensitive).toInt() * 1024;
        else if (context_size.contains("mb", Qt::CaseInsensitive))
            s = context_size.remove("mb", Qt::CaseInsensitive).toInt() * 1024000;
        else
            s = logRotateFileSize.toInt();

        m_logProcessor = new LogProcessor();
        m_logProcessor->setContextSize(s);
        m_logProcessor->setMouseEventFile(gCore->settingValue("Log/mouseLogFilename", "").toString());
        m_logProcessor->setFilters(this->getFilters());
        m_logProcessor->setGeneralMatrix( this->getGeneralLevelsSettings());
        m_logProcessor->setModulesMatrix( this->getModulesLevelsSettings());

        /// synchronous or asynchronous
        ///
        if (!m_sync) {
            log_console("Log is asynchronous");
            m_processorThread = new QThread(this);
            m_logProcessor->moveToThread(m_processorThread);
            connect(this, SIGNAL(logMessage(int,QString,QString,QString)), m_logProcessor, SLOT(put(int,QString,QString,QString)), Qt::QueuedConnection);
            m_processorThread->start(QThread::LowestPriority);

            log_console(QString("Log current thread pointer is %1").arg(qint64(this->thread())));
            log_console(QString("Log processor thread pointer is %1").arg(qint64(m_logProcessor->thread())));
        } else {
            log_console("Log is synchronous");
            connect(this, SIGNAL(logMessage(int,QString,QString,QString)), m_logProcessor, SLOT(put(int,QString,QString,QString)), Qt::DirectConnection);
        }
    }


    /// previous run crash detection
    crashCheck();
}


void Log::put(int logLevel, const QString &message, const QString &module, const QString &submodule)
{
    emit logMessage(logLevel, message, module, submodule);
}


void Log::log_console(QString message)
{
    std::cout <<  message.toStdString() << std::endl;
}


void Log::startCustomHandler()
{
    qInstallMsgHandler(customMessageHandler);
}


void Log::stopCustomHandler()
{
    qInstallMsgHandler(0);
}


void Log::setDefaultConfig()
{
    if (gCore->settingValue("Log/logFileTimestampFor").toString().isEmpty())
        gCore->setSettingValue("Log/logFileTimestampFor","debug|warning|error|critical|info|metric");
}


Log::Destination Log::settingLineToDestination(QString level, QString line, bool listExists, QStringList allowedDestinations )
{
    QString valueStr = gCore->settingValue(line).toString();
    QStringList values = valueStr.split("|", QString::SkipEmptyParts);

    Destination dest;
    dest.needContext = gCore->settingValue("Log/contextFor").toString().contains(level, Qt::CaseInsensitive) ? true : false;
    dest.needLogfileTimestamp = gCore->settingValue("Log/logFileTimestampFor").toString().contains(level, Qt::CaseInsensitive) ? true : false;

    foreach (QString value, values) {
        QString str = value.trimmed();
        if (str == "console")
            if (listExists && !allowedDestinations.contains(str))
                continue;
            else
                dest.console = true;
        if (str == "file")
            if (listExists && !allowedDestinations.contains(str))
                continue;
            else
                dest.file = true;
        if (str == "mail")
            if (listExists && !allowedDestinations.contains(str))
                continue;
            else
                dest.mail = true;
        if (str == "storage")
            if (listExists && !allowedDestinations.contains(str))
                continue;
            else
                dest.storage = true;
        if (str == "web")
            if (listExists && !allowedDestinations.contains(str))
                continue;
            else
                dest.web = true;
        if (str == "box")
            if (listExists && !allowedDestinations.contains(str))
                continue;
            else
                dest.box = true;
    }

    return dest;
}


Log::Module Log::getGeneralLevelsSettings()
{
    Log::Module module;
    for (int i=logError; i<LOGLEVELMAXVALUE; ++i) {
        QString param = QString("Log/%1To").arg(LogLevelNames.value(i));
        QString value = gCore->settingValue(param).toString();
        Destination dest = settingLineToDestination(LogLevelNames.value(i), param);
        module.destinations.insert(i, dest);
        if (!value.isEmpty()) {
//            log_console(QString("value \'%1\'").arg(value));
            module.levels.append(i);
        }
    }

    //debug
    log_console("======= Log general settings =========");
    foreach (int id, module.levels) {
        log_console(QString("level \'%1\'(%2)").arg(LogLevelNames.value(id)).arg(id));
    }
    for (int i=logError; i<LOGLEVELMAXVALUE; ++i) {
        Destination dest = module.destinations.value(i);
        log_console(QString("Log level \'%1\'(%2):").arg(LogLevelNames.value(i)).arg(i));
        log_console(QString("     console: %1").arg(dest.console));
        log_console(QString("     file: %1").arg(dest.file));
        log_console(QString("     web: %1").arg(dest.web));
        log_console(QString("     mail: %1").arg(dest.mail));
    }


    return module;
}


int Log::levelNameToEnum(QString name)
{
    for (int i=logError; i<LOGLEVELMAXVALUE; ++i) {
        if (LogLevelNames.value(i) == name)
            return i;
    }
    return -1;
}


QHash<QString, Log::Module> Log::getModulesLevelsSettings()
{
    QHash<QString, Log::Module> modules;
    gCore->settings()->beginGroup("Log");
    QStringList keys = gCore->settings()->allKeys();
    gCore->settings()->endGroup();

    /// detecting defined modules name

    QStringList modulesNames;
    QStringList submodulesNames;

    foreach (QString key, keys) {
        QString moduleName;
        if (key.leftRef(13) == QString("moduleLevels_"))
            moduleName = key.midRef(13).toString();
        else if (key.leftRef(11) == QString("moduleDest_")) {
            /// detecting subkey moduleDest_debuglevel
            for (int i=logError; i<LOGLEVELMAXVALUE; ++i) {
                QString searchKey =  QString("moduleDest_%1").arg(LogLevelNames.value(i));
                if (key.leftRef(searchKey.size()) == searchKey) {
                    moduleName = key.midRef(searchKey.size()+1).toString();
                    break;
                }
            }

            if (moduleName.isEmpty()) {
                /// continue without specific debug level
                moduleName = key.midRef(11).toString();
            }
        }

        if (!moduleName.isEmpty()) {
            if (moduleName.contains("_")) {
                /// submodule
                if ((!moduleName.isEmpty()) && !submodulesNames.contains(moduleName))
                    submodulesNames.append(moduleName);
            } else {
                /// module
                if ((!moduleName.isEmpty()) && !modulesNames.contains(moduleName))
                    modulesNames.append(moduleName);
            }
        }
    }

    /// reading specific settings for defined modules
    foreach (QString moduleName, modulesNames) {
        Log::Module module;
        QStringList allowedDestinations;
        bool listExists = keys.contains(QString("moduleDest_%1").arg(moduleName));
        if (listExists) {
            allowedDestinations = gCore->settingValue(QString("Log/moduleDest_%1")
                                                      .arg(moduleName)).toString()
                                                      .split("|", QString::SkipEmptyParts);
        }

        /// parsing levels information
        if (keys.contains(QString("moduleLevels_%1").arg(moduleName))) {
//            module.levelsDefined = true;
            QStringList moduleLevels = gCore->settingValue(QString("Log/moduleLevels_%1")
                                                          .arg(moduleName)).toString()
                                                          .split("|", QString::SkipEmptyParts);
            foreach (QString level, moduleLevels) {
                int levelID = levelNameToEnum(level);
                if (levelID != -1)
                    module.levels.append(levelID);
                else
                    log_console(QString("Wrong level \'%1\' defined for module \'%2\'").arg(level).arg(moduleName));
            }
        } else {
            /// not defined, so will take general
            for (int i=logError; i<LOGLEVELMAXVALUE; ++i) {
                if (!gCore->settingValue(QString("%1To").arg(LogLevelNames.value(i))).toString().isEmpty())
                    module.levels.append(i);
            }
        }


        /// checking special destinations for defined loglevels
        for (int i=logError; i<LOGLEVELMAXVALUE; ++i) {
            QString levelKey = QString("moduleDest_%1_%2").arg(LogLevelNames.value(i)).arg(moduleName);

            if (keys.contains(levelKey)) {
                QString destForCurrentLevel = QString("Log/"+levelKey);
                Destination dest = settingLineToDestination(LogLevelNames.value(i), destForCurrentLevel, listExists, allowedDestinations);
                module.destinations.insert(i, dest);
            } else {
                /// not defined - use general
                QString param = QString("Log/%1To").arg(LogLevelNames.value(i));
                Destination dest = settingLineToDestination(LogLevelNames.value(i), param, listExists, allowedDestinations);
                module.destinations.insert(i, dest);
            }
        }

        modules.insert(moduleName, module);

        /// debug
        log_console("Module name = " + moduleName);
        foreach (int id, module.levels) {
            log_console(QString("level \'%1\'(%2)").arg(LogLevelNames.value(id)).arg(id));
        }
        for (int i=logError; i<LOGLEVELMAXVALUE; ++i) {
            Destination dest = module.destinations.value(i);
            log_console(QString("Log level \'%1\'(%2):").arg(LogLevelNames.value(i)).arg(i));
            log_console(QString("     console: %1").arg(dest.console));
            log_console(QString("     file: %1").arg(dest.file));
            log_console(QString("     web: %1").arg(dest.web));
            log_console(QString("     mail: %1").arg(dest.mail));
        }
    }

    /// reading specific settings for defined submodules
    foreach (QString moduleName, submodulesNames) {
        Log::Module module;
        QString parentModuleName = moduleName.section("_",0,0);
        QStringList allowedDestinations;
        bool listExists = keys.contains(QString("moduleDest_%1").arg(moduleName));
        if (listExists) {
            allowedDestinations = gCore->settingValue(QString("Log/moduleDest_%1")
                                                      .arg(moduleName)).toString()
                    .split("|", QString::SkipEmptyParts);
        } else {
            listExists = keys.contains(QString("moduleDest_%1").arg(parentModuleName));
            if (listExists) {
                allowedDestinations = gCore->settingValue(QString("Log/moduleDest_%1")
                                                          .arg(parentModuleName)).toString()
                        .split("|", QString::SkipEmptyParts);
            }
        }

        /// parsing levels information
        if (keys.contains(QString("moduleLevels_%1").arg(moduleName))) {
            QStringList moduleLevels = gCore->settingValue(QString("Log/moduleLevels_%1")
                                                          .arg(moduleName)).toString()
                                                          .split("|", QString::SkipEmptyParts);
            foreach (QString level, moduleLevels) {
                int levelID = levelNameToEnum(level);
                if (levelID != -1)
                    module.levels.append(levelID);
                else
                    log_console(QString("Wrong level \'%1\' defined for module \'%2\'").arg(level).arg(moduleName));
            }
        } else {
            /// not defined, so will try parent
            if (modules.contains(parentModuleName)) {
                module.levels = modules.value(parentModuleName).levels;
            } else {
                /// then use general
                for (int i=logError; i<LOGLEVELMAXVALUE; ++i) {
                    if (!gCore->settingValue(QString("%1To").arg(LogLevelNames.value(i))).toString().isEmpty())
                        module.levels.append(i);
                }
            }
        }

        /// checking special destinations for defined loglevels
        for (int i=logError; i<LOGLEVELMAXVALUE; ++i) {
            QString levelKey = QString("moduleDest_%1_%2").arg(LogLevelNames.value(i)).arg(moduleName);

            if (keys.contains(levelKey)) {
                QString destForCurrentLevel = QString("Log/"+levelKey);
                Destination dest = settingLineToDestination(LogLevelNames.value(i), destForCurrentLevel, listExists, allowedDestinations);
                module.destinations.insert(i, dest);
            } else {
                /// not defined - try parent
                if (modules.contains(parentModuleName)) {
                    module.destinations.insert(i, modules.value(parentModuleName).destinations.value(i));
                } else {
                    // then use general
                    QString param = QString("Log/%1To").arg(LogLevelNames.value(i));
                    Destination dest = settingLineToDestination(LogLevelNames.value(i), param, listExists, allowedDestinations);
                    module.destinations.insert(i, dest);
                }
            }
        }

        modules.insert(moduleName, module);

        /// debug

        log_console("subModule name = " + moduleName);
        foreach (int id, module.levels) {
            log_console(QString("level \'%1\'(%2)").arg(LogLevelNames.value(id)).arg(id));
        }
        for (int i=logError; i<LOGLEVELMAXVALUE; ++i) {
            Destination dest = module.destinations.value(i);
            log_console(QString("Log level \'%1\'(%2):").arg(LogLevelNames.value(i)).arg(i));
            log_console(QString("     console: %1").arg(dest.console));
            log_console(QString("     file: %1").arg(dest.file));
            log_console(QString("     web: %1").arg(dest.web));
            log_console(QString("     mail: %1").arg(dest.mail));
        }
    }

    return modules;
}


void Log::crashCheck()
{
    put(Log::logDebug, "crashCheck", LOGMODULE);
    QDir dir(CRASHDUMP_DIR);
    QStringList filters;
    filters << "*.dmp";
    QStringList files = dir.entryList(filters, QDir::Files|QDir::NoSymLinks|QDir::NoDotAndDotDot);
    if (files.isEmpty()) {
        put(Log::logDebug, "crashdump's directory is empty", LOGMODULE);
    } else {
        for (int i=0; i<files.count(); ++i) {
            // crashdump will be assigned to web only
            put(Log::logCritical, "crash detected", LOGMODULE);
        }
    }
}


void Log::logRotate(QString filename)
{
    QFile log( filename.isEmpty() ? LOGFILENAME : filename);
    if (filename.isEmpty()) {     // default filec - first iteration
        if (log.size() > m_logRotateFileSize)
            logRotate(log.fileName());
    } else {                        // just renaming file
        QFileInfo fileinfo(log.fileName());
        QString suffix = fileinfo.suffix();
        int newsuffix = suffix.toInt() + 1;
        if (newsuffix <= m_logRotateCounter) {
            QString newfilename;
            if (suffix.toInt() == 0)        // still have no numeric additional suffix
                newfilename = fileinfo.dir().dirName() + "/" + fileinfo.fileName() + "." + QString::number(newsuffix);
            else
                newfilename = fileinfo.dir().dirName() + "/" + fileinfo.completeBaseName() + "." + QString::number(newsuffix);
            if (QFile::exists(newfilename))
                logRotate(newfilename);
            QFile::rename(log.fileName(), newfilename);
        } else {
            QFile::remove(log.fileName());
        }
    }
}


void Log::customMessageHandler(QtMsgType type, const char *msg)
{
    switch (type) {
    case QtDebugMsg:
        Log::instance()->put(Log::logVerbose, QString(msg), "Unknown", QTHANDLER_IDENTIFIER);
        break;
    case QtWarningMsg:
        Log::instance()->put(Log::logVerbose, QString(msg), "Unknown", QTHANDLER_IDENTIFIER);
        break;
    case QtCriticalMsg:
        Log::instance()->put(Log::logVerbose, QString(msg), "Unknown", QTHANDLER_IDENTIFIER);
        break;
    case QtFatalMsg:
        Log::instance()->put(Log::logVerbose, QString(msg), "Unknown", QTHANDLER_IDENTIFIER);
        break;
    default:
        Log::instance()->put(Log::logVerbose, QString(msg), "Unknown", QTHANDLER_IDENTIFIER);
        break;
    }
}


void Log::initMouseHandler()
{
    m_mouseHandler = new LogMouseHandler(this);
    gCore->scene()->installEventFilter(m_mouseHandler);
}


QList <Log::Filter> Log::getFilters()
{
    QList <Filter> filters;
//    m_filters.clear();
    gCore->settings()->beginGroup("Log");
    QStringList keys = gCore->settings()->allKeys();
    gCore->settings()->endGroup();

    foreach (QString key, keys) {
        if (key.leftRef(13) == QString("filterRegexp_")) {
            Filter f;
            QString filterName = key.midRef(13).toString();
            qDebug() << key;
            QString regExp = gCore->settingValue("Log/"+key).toString();
            QString replace = gCore->settingValue(QString("Log/filterAction_%1").arg(filterName)).toString();
            f.re = QRegExp(regExp);
            f.replace = replace;
            filters.append(f);
        }
    }
    return filters;
}
