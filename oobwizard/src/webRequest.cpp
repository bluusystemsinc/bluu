#include "webRequest.h"

#include <QNetworkReply>
#include <QNetworkAccessManager>
#include <QStringList>
#include <QTextStream>
#include <QFile>
#include <QDir>
//#include <QJson/Serializer>
//#include <QJson/Parser>

#include <QDebug>

#define USER ""
#define PASSWORD ""


webRequest::webRequest(QObject *parent) :
    QObject(parent)
{
    m_currentState = stateNormal;

    manager = new QNetworkAccessManager(this);
    QObject::connect(manager,     SIGNAL(finished(QNetworkReply* )), this, SLOT(finishedSlot(QNetworkReply*)));
}

webRequest::webRequest(QObject *parent, QString url) :
    QObject(parent),
    m_url(url)
{
    m_currentState = stateNormal;

    manager = new QNetworkAccessManager(this);
}

webRequest::~webRequest()
{
    //delete manager;
}

void webRequest::sendRequest()
{
       QObject::connect(manager,     SIGNAL(finished(QNetworkReply* )), this, SLOT(finishedSlot(QNetworkReply*)));

       QUrl url(m_url);
       QNetworkReply* reply = manager->get(QNetworkRequest(url));
       // NOTE: Store QNetworkReply pointer (maybe into caller).
       // When this HTTP request is finished you will receive this same
       // QNetworkReply as response parameter.
       // By the QNetworkReply pointer you can identify request and response.
}


void webRequest::finishedSlot(QNetworkReply* reply)
{
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
        qDebug() << "NOT OK!"<< endl;
        // handle errors here
    }
}

//void WebLogger::send(Log::LogLevel logLevel, QVariantMap &fields)
//{
//    if (m_currentState == stateNormal || m_currentState == stateRestoring) {

//        QNetworkRequest request;
//        request.setUrl(m_url + LOGPOINT);
//        request.setHeader(QNetworkRequest::ContentTypeHeader, "application/json");

//        request.setRawHeader("Authorization", "Basic " + QByteArray(QString("%1:%2").arg(USER).arg(PASSWORD).toAscii()).toBase64());

//        QJson::Serializer serializer;
//        QByteArray json = serializer.serialize(fields);
//        QNetworkReply * reply = manager->post(request, json);

//        queries.insert(reply, json);
//        emit logMessage(Log::logDebug, QString("add reply to array: %1").arg(qint64(reply)));
//    } else {
//        QJson::Serializer serializer;
//        QByteArray json = serializer.serialize(fields);
//        queryToFile(json);
//        if (!stateTimer->isActive())
//            stateTimer->start();
//    }

//    return;
//}


//void WebLogger::replyFinished(QNetworkReply * reply)
//{
//    State prevState = m_currentState;
//    if (reply->error() != QNetworkReply::NoError) {
//        QString errorStr = "It's impossible to send log to Web Logger \n";
//        errorStr += "Error code " + QString::number(reply->error()) + " - " + reply->errorString();
//        //errorStr += "Request: \n" + reply->request ();

//        if (queries.keys().contains(reply))
//            queryToFile(queries.value(reply));

//        // not network critical errors
//        if (reply->error() != QNetworkReply::UnknownContentError)
//            m_currentState = stateNetworkDown;

//        if (m_currentState != prevState)
//            emit logMessage(Log::logDebug, "Log network state is: NetworkDown");

//        emit logMessage(Log::logError,  errorStr );
//    } else {
//        m_currentState = stateNormal;
//        if (m_currentState != prevState) {
//            emit logMessage(Log::logDebug, "Log network state is: Normal");
//            sendFromCache();
//        }
//    }

//    emit logMessage(Log::logVerbose, QString("    current reply = %1").arg(qint64(reply)));
//    foreach (QNetworkReply * r, queries.keys())
//        emit logMessage(Log::logVerbose, QString("    item:= %1").arg(qint64(r)));

//    if (queries.keys().contains(reply))
//        queries.remove(reply);

//    reply->deleteLater();
//}


//void WebLogger::queryToFile(QString json)
//{
//    QFile log(CACHEFILE);
//    if (log.open(QFile::WriteOnly| QFile::Append)) {
//        QTextStream out(&log);
//        out << json << "\n";
//        log.close();
//    }
//}


//void WebLogger::restoreState()
//{
//    State prevState = m_currentState;
//    m_currentState = stateRestoring;
//    if (m_currentState != prevState)
//        emit logMessage(Log::logDebug, "Log network state is: Restoring");
//}


void webRequest::sendFromFile(QString &filename)
{

    QNetworkRequest request;
    request.setUrl(m_url);

    request.setHeader(QNetworkRequest::ContentTypeHeader, "application/json");

    request.setRawHeader("Authorization", "Basic " + QByteArray(QString("%1:%2").arg(USER).arg(PASSWORD).toAscii()).toBase64());

    QFile file(filename);
    if (!file.open(QIODevice::ReadOnly | QIODevice::Text))
        return;

    QStringList list;

    QTextStream in(&file);

    while (!in.atEnd()) {
        QString line = in.readLine();
        list.append("{" + line + "}");
    }

    QString json = "[" + list.join(",") + "]";
    QNetworkReply * reply = manager->post(request, json.toAscii());

    if(reply->error() == QNetworkReply::NoError)
    {
        qDebug()<< "send from file NO Error\n";
    }
    else
    {
        qDebug()<< "Error sendin from file\n";
    }
    file.close();
}

