#ifndef LOG_H
#define LOG_H

#include <QObject>
#include <QHash>
#include <QMap>
#include <QRegExp>
#include <QStringList>

#define gLog Log::instance()

class Core;
class WebLogger;
class LogMouseHandler;
class QTimer;
class LogThread;
class LogProcessor;

/** \defgroup LogSystem Log System
* @{
*/

/** \class Log
* \brief General class for event/message logging
*
* This is general class for event/message logging to some destinations
* with some log levels
*/

class Log : public QObject
{
    Q_OBJECT
public:
    /** \struct Destination
     * @brief The Destination struct (internal usage)
     *
     *  console - shows is events destination "console" enabled or no.
     *  file - grant access to save events to the file log.txt
     *  web - sends event to web storage
     *  mail - deprecated (?)
     *  box - reserved for show events in dialog window for user
     *  needContext - defines do we need context for this log level
     *  needLogfileTimestamp - defines do we need to add timestamp for this log level
     */
    struct Destination {
        bool console;
        bool file;
        bool web;
        bool storage;
        bool mail;
        bool box;
        bool needContext;
        bool needLogfileTimestamp;
        Destination() {
            console = file = web = storage = mail = box = needContext = needLogfileTimestamp = false;
        }
    };
    /** \struct Filter
     * @brief The Filter struct (internal usage)
     */
    struct Filter {
        QRegExp re;
        QString replace;
    };

    /** \enum LogLevel
     * @brief The LogLevel enum
     *
     *  Used for log levels and should be synced with Core log levels
     *  for prevent export Log interface to all classed which uses Core
     *
     *  LogMetric - used for sending metic events: mouse, keyboard, stages and can be processed on server for make some reports
     *              building graphs, etc.
     *  LogWarning - used for sending warning events that don't cause critical problems, but still make negative influence to
     *              application work or user experience.
     *  LogError    - used for sending non critical errors from modules, network services, etc. These events should be processed and
     *              analyzed and possibly fixed.
     *  LogCritical - used for sending critical events that caused application stop. There is no much cases to use it except crash or
     *              missed appication's parts.
     *  LogDebug    - developer debug messages that can help to figure our problems or look context of other important events
     *  LogVerbose  - used for debug some well defined parts in development and production. Usualy should ve used by developer for his own
     *                cases. Must be removed after feature bacame more less stable.
     *  LogInfo     - used for sending events to server that have to be shared with some beholders groups - marketing, ops, etc. While
     *                LogMerics should be well formatted for parse, LogInfo can include information in human readable format and posible with
     *                some case explaintation.
     */
    enum LogLevel {
        logError = 0,
        logWarning = 1,
        logInfo = 2,
        logDebug = 3,
        logCritical = 4,
        logMetric = 5,
        logVerbose = 6,
        LOGLEVELMAXVALUE = 7
    };

    /** \var LogLevelNames
     * @brief LogLevelNames
     *  transformation from loglevel int to string.
     *  Inited in Log::Log()
     */
    static QHash<int, QString> LogLevelNames;

    /** \struct Module
     * @brief The Module struct
     *  Keeps imformation for log levels and destinations rules
     */
    struct Module {
        QList <int> levels;
        QMap <int, Destination> destinations;
    };
    /** \fn instance
     * @brief instance of log class
     * @return Log instance
     */
    static Log *instance();
    /** \fn createInstance
     * @brief createInstance
     * @return created instance of Log class
     */
    static Log *createInstance();
    /** \fn Log
     * @brief Log constructor
     * @param parent object
     */
    explicit Log(QObject *parent = 0);
    ~Log();
    /** \fn put
     * @brief put - general method for pushing info to Log
     * @param logLevel defines logLevel for pushed message
     * @param message message for push to log system
     * @param module defines module from which message was pushed
     * @param submodule defines submodule from which message was pushed
     */
    void put(int logLevel, const QString &message, const QString &module, const QString &submodule = "");

signals:
    /** \fn logMessage
     * @brief logMessage
     * @param logLevel
     * @param message
     * @param module
     * @param submodule
     *  Internal sugnal to internal thread for use acynchronous
     */
    void logMessage(int logLevel, const QString &message, const QString &module, const QString &submodule);

private slots:
    void initMe();
    void initMouseHandler();
    void crashCheck();

private:
    static void customMessageHandler(QtMsgType type, const char *msg);

    void log_console(QString message);
    void setDefaultConfig();
    void startCustomHandler();
    void stopCustomHandler();
    void logRotate(QString filename = QString());
    QString infoPreprocess(QString str);
    QList<Filter> getFilters();
    int levelNameToEnum(QString name);

    Destination settingLineToDestination(QString level, QString line, bool listExists = false, QStringList allowedDestinations = QStringList());
    Module getGeneralLevelsSettings();
    QHash<QString, Log::Module> getModulesLevelsSettings();

private:
    static Log *pInstance;
    bool m_isInited;

    QThread * m_processorThread;
    LogProcessor * m_logProcessor;

    LogMouseHandler * m_mouseHandler;

    bool m_interceptQtMessages;
    bool m_interceptMouseEvents;
    qint64 m_logRotateFileSize;
    int m_logRotateCounter;
    bool m_sync;

};

/**
* @}
*/


#endif // LOG_H
