#ifndef WEBREQUEST_H
#define WEBREQUEST_H

//#include <QObject>
// #include <QWidget>
#include <QVariantMap>
#include <QMap>
#include <QTimer>
#include <QNetworkReply>
#include "singleton.h"

// #include "qjson/parser.h"
// #include "qjson/serializer.h"

class QNetworkAccessManager;
//class QNetworkReply;
//class QNetworkRequest;

/*
struct Cache {
    QNetworkReply * reply;
    QString Json;
};
*/

//safeLevel {slLow, slMedium, slHigh}

class WebRequest : public QObject
{
    Q_OBJECT
public:
    enum State {stateNormal, stateNetworkDown, stateRestoring};
    explicit WebRequest();
    explicit WebRequest(QObject* parent);
    explicit WebRequest(QObject* parent,const QString url);
    ~WebRequest();
    void sendRequest();
    void setUrl(const QUrl& u);
//    QString convertToJson(QVariantMap &fields);

signals:
    void logMessage(int, QString message);

public slots:
//    void send(Log::LogLevel logLevel, QVariantMap &fields);
//    void send(int logLevel, const QString &message, const QString &subject, const QString &category);
//    void sendHeartbeat(QVariantMap &fields);
//    void replyFinished(QNetworkReply *);
//    void restoreState();
    void sendDataToServer(const QVariantMap &info);
    void sendDataToServer(const QByteArray& msg);
    void finishedSlot(QNetworkReply* reply);
    
private:
//    void queryToFile(QString json);
//    void getContext();

//protected:
//    virtual void run();

private:
    QUrl    url;
    QNetworkAccessManager *manager;
    State m_currentState;
    QMap <QNetworkReply *, QString> queries;
//    int m_retryInterval;
    QTimer * stateTimer;
    QString m_url;
    // QJson::Serializer s;
};

typedef CBluuSingleton<WebRequest>      CBluuWebRequest;

#endif // WEBREQUEST_H
