#include "webrequest.h"
#include "debug.h"
#include "settingsmanager.h"
#include <QNetworkReply>
#include <QNetworkAccessManager>
#include <QStringList>
#include <QTextStream>
#include <QFile>
#include <QDir>
#include <QDebug>
// #include <QMessageBox>
#include <QString>
#include <QtCore>
// #include <QtGui>

#define USER ""
#define PASSWORD ""

/**
 * @brief WebRequest::WebRequest TODO
 */
WebRequest::WebRequest()
{
    m_currentState = stateNormal;
    whoSend = NULL;
    manager = new QNetworkAccessManager();
    // connect(manager, SIGNAL(finished(QNetworkReply*)), CBluuDataManagerWorker::Instance(), SLOT(networkReplySlot(QNetworkReply*)));

    QObject::connect(manager, SIGNAL(finished(QNetworkReply* )), this, SLOT(finishedSlot(QNetworkReply*)));
}

WebRequest::WebRequest(QObject *parent) :
    QObject(parent)
{

    m_currentState = stateNormal;
    whoSend = NULL;
    manager = new QNetworkAccessManager(this);
    // QObject::connect(manager, SIGNAL(finished(QNetworkReply* )), this, SLOT(finishedSlot(QNetworkReply*)));

}

WebRequest::WebRequest(QObject *parent, const QString url) :
    QObject(parent),
    m_url(url)
{
    m_currentState = stateNormal;
    whoSend = NULL;
    manager = new QNetworkAccessManager(this);
    // QObject::connect(manager,     SIGNAL(finished(QNetworkReply* )), this, SLOT(finishedSlot(QNetworkReply*)));
}

WebRequest::~WebRequest()
{
    //delete manager;
}

void WebRequest::sendRequest()
{
       QUrl url(m_url);
       /*QNetworkReply* reply = */manager->get(QNetworkRequest(url));
//       request.setUrl(url);
       // NOTE: Store QNetworkReply pointer (maybe into caller).

       // When this HTTP request is finished you will receive this same
       // QNetworkReply as response parameter.
       // By the QNetworkReply pointer you can identify request and response.
}

void WebRequest::setUrl(const QUrl& u)
{
    url = u;
    // m_url = url;
}

/**
 * @brief WebRequest::getManager
 * @return
 */
QNetworkAccessManager* WebRequest::getManager()
{
    return manager;
}

void WebRequest::finishedSlot(QNetworkReply* reply)
{
    /*
    // Reading attributes of the reply
    // e.g. the HTTP status code
    QVariant statusCodeV =    reply->attribute(QNetworkRequest::HttpStatusCodeAttribute);

    // no error received?
    if (reply->error() == QNetworkReply::NoError)
    {
        // read data from QNetworkReply here
        qDebug() << "OK"<< endl;

        QByteArray bytes = reply->readAll(); // bytes
        QString str(bytes); // string
        qDebug() << str<< endl;
    }
    else
    {
        // QMessageBox::warning(this ,"Server Status","Server error!\n"+reply->errorString());
        qDebug() << "NOT OK!"<< reply->errorString() << reply->error() << endl;
        // handle errors here
    }
    */

    if(NULL != whoSend)
    {
        QString     className = whoSend->metaObject()->className();

        if("DatabaseManager" == className)
            emit networkReplyDatabaseSendSignal(reply);

        if("PacketSendTask" == className)
            emit networkReplySignal(reply);

        if("ControlerLiveTask" == className)
            emit networkReplyControlerSignal(reply);
    }
}


void WebRequest::sendDataToServer(const QVariantMap &info)
{
    debugMessage();

    Q_UNUSED(info);

    QVariantList infoData;
    QNetworkRequest request;
    QUrl tmpUrl;

    request.setUrl(m_url);
    request.setHeader(QNetworkRequest::ContentTypeHeader, "application/json");
    request.setRawHeader("Authorization", "Basic" + QByteArray(QString("%1:%2").arg(USER).arg(PASSWORD).toAscii()).toBase64());

    QByteArray json;    //   = s.serialize(info);
    qDebug() << json;
    manager->post(request, json);

}

/**
 * @brief WebRequest::sendDataToServer TODO
 * @param info
 */
void WebRequest::sendDataToServer(QString* msg)
{
    debugMessage();

    QNetworkRequest request;
    QByteArray  temp = msg->toUtf8();
    QString     webRequest = CBluuSettingsManager::Instance()->getWebRequestAddress();
    QString     siteId = CBluuSettingsManager::Instance()->getSiteId();
    QString     userId = CBluuSettingsManager::Instance()->getUserId();
    QString     userPassword = CBluuSettingsManager::Instance()->getUserPassword();
    QString     urlStr;
    QUrl        url;

    whoSend = sender();
    urlStr = QString("%1%2/").arg(webRequest).arg(siteId);
    url = QUrl(urlStr);
    request.setUrl(url);
    request.setHeader(QNetworkRequest::ContentTypeHeader, "application/json");
    request.setRawHeader("Authorization", "Basic " + QByteArray(QString("%1:%2").arg(userId).arg(userPassword).toAscii()).toBase64());

    manager->put(request, temp);
}

/**
 * @brief WebRequest::sendDataToServer
 * @param msg
 * @param serial
 */
void WebRequest::sendDataToServer(const QString msg, const QString serial)
{
    debugMessage();

    QNetworkRequest request;
    QByteArray  temp = msg.toUtf8();
    QString     webRequest = CBluuSettingsManager::Instance()->getWebRequestAddress();
    QString     siteId = CBluuSettingsManager::Instance()->getSiteId();
    QString     userId = CBluuSettingsManager::Instance()->getUserId();
    QString     userPassword = CBluuSettingsManager::Instance()->getUserPassword();
    QString     urlStr;
    QUrl        url;

    whoSend = sender();
    urlStr = QString("%1%2/devices/%3/statuses/").arg(webRequest).arg(siteId).arg(serial);
    url = QUrl(urlStr);
    request.setUrl(url);
    request.setHeader(QNetworkRequest::ContentTypeHeader, "application/json");
    request.setRawHeader("Authorization", "Basic " + QByteArray(QString("%1:%2").arg(userId).arg(userPassword).toAscii()).toBase64());
    manager->post(request, temp);
}
