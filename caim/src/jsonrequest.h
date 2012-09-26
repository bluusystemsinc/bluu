#ifndef JSONREQUEST_H
#define JSONREQUEST_H

#include <QObject>

class QNetworkReply;

class JSonRequest : public QObject
{
    Q_OBJECT
public:
    explicit JSonRequest(QObject *parent = 0);

public slots:
    void send(const QByteArray &data);

signals:
    void finished(QNetworkReply *reply);
};

#endif // JSONREQUEST_H
