#include "datamanagerthread.h"
#include "datamanager.h"
#include "webrequest.h"
#include "databasemanager.h"
#include "debugger.h"
#include "debug.h"
#include <QTimer>
#include <QDebug>
#include <QFile>

/**
 * @brief DataManagerThread::DataManagerThread
 * @param parent
 */
DataManagerThread::DataManagerThread(QObject *parent)
    : QThread(parent)
{
    connect(this, SIGNAL(debugSignal(QString)), CBluuDebugger::Instance(), SLOT(debugSlot(QString)));
    debugMessageThread("");
}

/**
 * @brief DataManagerThread::timeOutSlot
 */
void DataManagerThread::timeOutSlot()
{
    debugMessageThread("");

    emit sendSignal();
}

/**
 * @brief DataManagerThread::sendSlot
 */
void DataManagerThread::sendSlot()
{
    debugMessageThread("");

    QStringList*  packets = CBluuDataManager::Instance()->getPackets();

    if(0 < packets->size())
    {
        debugMessageThread("Packets > 0");

        if(true == timerPackets->isActive())
            timerPackets->stop();

         it = packets->begin();
         emit networkSendSignal(*it);
    }
    else
    {
        debugMessageThread("Packets = 0");

        if(false == timerPackets->isActive())
            timerPackets->start(1000);
    }
}

/**
 * @brief DataManagerThread::sendDatabaseSlot
 */
void DataManagerThread::sendDatabaseSlot()
{
    emit databaseSendPacketSignal();
}

/**
 * @brief DataManagerThread::networkReplySlot
 * @param reply
 */
void DataManagerThread::networkReplySlot(QNetworkReply *reply)
{
    debugMessageThread("");

    bool    result = false;

    if(QNetworkReply::NoError == reply->error())
    {
        debugMessageThread("Packet send OK");
        result = true;
        // emit sendSignal();
    }
    else
    {
        debugMessageThread("Packed send FAIL, store in database");
        emit databaseStorePacketSignal(&*it);
        // result = CBluuDatabaseManager::Instance()->writePacket(&*it);
    }

    // if(true == result)
    {
        QStringList*  packets = CBluuDataManager::Instance()->getPackets();
        QMutexLocker    locker(CBluuDataManager::Instance()->getMutex());

        packets->erase(it);

        if(0 < packets->size())
            emit sendSignal();
    }
}

/**
 * @brief DataManagerThread::run
 */
void DataManagerThread::run()
{
    debugMessageThread("");

    timerPackets = new QTimer();
    timerDatabase = new QTimer();
    connect(timerPackets, SIGNAL(timeout()), this, SLOT(sendSlot()));
    connect(timerDatabase, SIGNAL(timeout()), this, SLOT(sendDatabaseSlot()));
    connect(this, SIGNAL(sendSignal()), SLOT(sendSlot()));
    connect(CBluuWebRequest::Instance(), SIGNAL(networkReplySignal(QNetworkReply*)), this, SLOT(networkReplySlot(QNetworkReply*)));
    connect(this, SIGNAL(networkSendSignal(QString)), CBluuWebRequest::Instance(), SLOT(sendDataToServer(QString)));
    connect(this, SIGNAL(databaseStorePacketSignal(QString*)), CBluuDatabaseManager::Instance(), SLOT(databaseStorePacketSlot(QString*)));
    connect(this, SIGNAL(databaseSendPacketSignal()), CBluuDatabaseManager::Instance(), SLOT(databaseSendPacketSlot()));
    emit sendSignal();
    timerPackets->start(5000);
    exec();
}
