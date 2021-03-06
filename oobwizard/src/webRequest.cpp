#include "webRequest.h"

#include <QNetworkReply>
#include <QNetworkAccessManager>
#include <QStringList>
#include <QTextStream>
#include <QFile>
#include <QDir>
#include <QDebug>
#include <QMessageBox>
#include <QString>
#include <QtCore>
#include <QtGui>

#define USER ""
#define PASSWORD ""


webRequest::webRequest(QWidget *parent) :
    QWidget(parent)
{

    m_currentState = stateNormal;

    manager = new QNetworkAccessManager(this);
    QObject::connect(manager, SIGNAL(finished(QNetworkReply* )), this, SLOT(finishedSlot(QNetworkReply*)));

}

webRequest::webRequest(QWidget *parent,const QString url) :
    QWidget(parent),
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
       /*QNetworkReply* reply = */manager->get(QNetworkRequest(url));
//       request.setUrl(url);
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
        QMessageBox::warning(this ,"Server Status","Server error!\n"+reply->errorString());
        qDebug() << "NOT OK!"<< reply->errorString() << reply->error() << endl;
        // handle errors here
    }
}


void webRequest::sendDataToServer(const QVariantMap &info)
{
    QVariantList infoData;
    QNetworkRequest request;
    QUrl tmpUrl;
    request.setUrl(m_url);

    request.setHeader(QNetworkRequest::ContentTypeHeader, "application/json");
    request.setRawHeader("Authorization", "Basic" + QByteArray(QString("%1:%2").arg(USER).arg(PASSWORD).toAscii()).toBase64());

    QByteArray json = s.serialize(info);
    qDebug() << json;
    manager->post(request, json);

}
