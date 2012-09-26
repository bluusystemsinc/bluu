#include "senddatamanager.h"

#include <QCoreApplication>

#include "jsonrequest.h"

SendDataManager::SendDataManager(QObject *parent) :
    QObject(parent)
{
}


SendDataManager *SendDataManager::instance()
{
    static SendDataManager *instance = new SendDataManager(qApp);

    return instance;
}

void SendDataManager::sendData(const QByteArray &data)
{
    JSonRequest *request = new JSonRequest(this);

    request->send(data);
}
