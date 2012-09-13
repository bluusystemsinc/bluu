#ifndef WEBLOGGER_H
#define WEBLOGGER_H

#include <QObject>
#include <QVariantMap>
#include <QMap>
#include <QTimer>

class QNetworkAccessManager;
class QNetworkReply;

/*
struct Cache {
    QNetworkReply * reply;
    QString Json;
};
*/

//safeLevel {slLow, slMedium, slHigh}

class webRequest : public QObject
{
    Q_OBJECT
public:
    enum State {stateNormal, stateNetworkDown, stateRestoring};
    explicit webRequest(QObject *parent);
    explicit webRequest(QObject *parent, QString url);
    ~webRequest();
    void sendRequest();
//    QString convertToJson(QVariantMap &fields);

    
signals:
    void logMessage(int, QString message);

public slots:
//    void send(Log::LogLevel logLevel, QVariantMap &fields);
//    void send(int logLevel, const QString &message, const QString &subject, const QString &category);
//    void sendHeartbeat(QVariantMap &fields);
//    void replyFinished(QNetworkReply *);
//    void restoreState();
    void sendFromFile(QString &filename);
    void finishedSlot(QNetworkReply* reply);
    
private:
//    void queryToFile(QString json);
//    void getContext();

//protected:
//    virtual void run();

private:
    QNetworkAccessManager *manager;
    State m_currentState;
    QMap <QNetworkReply *, QString> queries;
//    int m_retryInterval;
    QTimer * stateTimer;
    QString m_url;
};

#endif // WEBLOGGER_H
