#include "webRequest.h"

#include <QNetworkReply>
#include <QNetworkAccessManager>
#include <QStringList>
#include <QTextStream>
#include <QFile>
#include <QDir>

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
    QObject::connect(manager,     SIGNAL(finished(QNetworkReply* )), this, SLOT(finishedSlot(QNetworkReply*)));
}

webRequest::~webRequest()
{
    //delete manager;
}

void webRequest::sendRequest()
{
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
        qDebug() << "NOT OK!"<< reply->errorString() << endl;
        // handle errors here
    }
}


void webRequest::sendFromFile(QString &filename)
{

    QNetworkRequest request;
    request.setUrl(m_url);

    request.setHeader(QNetworkRequest::ContentTypeHeader, "application/json");

    request.setRawHeader("Authorization", "Basic " + QByteArray(QString("%1:%2").arg(USER).arg(PASSWORD).toAscii()).toBase64());

    QFile file(filename);
    if (!file.open(QIODevice::ReadOnly | QIODevice::Text))
        return;

    QString list;

    QTextStream in(&file);
    list.append("[{");
    while (!in.atEnd()) {
        QString line = in.readLine();
        list.append(line);
    }
    list.append("}]");

    QByteArray ba = list.toAscii();
    QNetworkReply * reply = manager->post(request, ba);

    file.close();
}
