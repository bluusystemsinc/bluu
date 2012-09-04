#ifndef LOGPROCESSOR_H
#define LOGPROCESSOR_H

#include <QObject>
#include "log.h"

class LogProcessor : public QObject
{
    Q_OBJECT
public:
    enum MatrixResult {MatrixResultOk, MatrixResultNotFound, MarixResultDIsabled };
    explicit LogProcessor(QObject *parent = 0);
    ~LogProcessor();
    void initServices();
    void setMouseEventFile(QString file);
    void setContextSize(int size);
    void setHeartbeatInterval(int heartbeatDelay);
    void setFilters(QList <Log::Filter> filters);
    void setGeneralMatrix(Log::Module settings);
    void setModulesMatrix(QHash<QString, Log::Module> matrix);
    
signals:
    void internalMessage(int logLevel, const QString &_message);
    
public slots:
    void put(int logLevel, const QString &_message, const QString &_module, const QString &_submodule);

private slots:
    void heartbeatProcessing();
    void webLoggerMessage(int level, QString message);
    void internalMessageSlot(int level, QString message);
    void log_console(QString message);

private:
    QString getContext();
    QByteArray getCrashdump(bool *repeat = 0);
    MatrixResult checkMatrixFor(int logLevel, QString module, Log::Destination * dest);

private:
    WebLogger * m_weblogger;

    Log::Destination debug;
    Log::Destination info;
    Log::Destination warning;
    Log::Destination error;
    Log::Destination critical;
    Log::Destination metric;

    qint64 m_context_size;
    QTimer * m_heartbeat;

    QString m_mouseEventFile;
    bool m_mouseEventSeparated;
    int m_heartbeatDelay;
    QList <Log::Filter> m_filters;
    bool m_useFilters;

    Log::Module m_generalSettings;
    QHash<QString, Log::Module> m_modulesSettings;
};

#endif // LOGPROCESSOR_H
