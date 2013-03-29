#include "packetsendtask.h"
#include "debug.h"
#include "debugger.h"
#include "datamanager.h"
#include "webrequest.h"
#include "databasemanager.h"
#include "parser.h"

/**
 * @brief PacketSendTask::PacketSendTask
 * @param parent
 */
PacketSendTask::PacketSendTask(QObject *parent)
              : Task(parent)
{
    connect(this, SIGNAL(debugSignal(QString)), CBluuDebugger::Instance(), SLOT(debugSlot(QString)));
    connect(this, SIGNAL(sendSignal()), SLOT(sendSlot()));
    connect(this, SIGNAL(networkSendSignal(const QString, const QString)), CBluuWebRequest::Instance(), SLOT(sendDataToServer(const QString, const QString)));
    connect(CBluuWebRequest::Instance(), SIGNAL(networkReplySignal(QNetworkReply*)), this, SLOT(networkReplySlot(QNetworkReply*)));
    connect(this, SIGNAL(databaseStorePacketSignal(QString*)), CBluuDatabaseManager::Instance(), SLOT(databaseStorePacketSlot(QString*)));
    connect(CBluuDatabaseManager::Instance(), SIGNAL(databasePacketStoredSignal()), this, SLOT(databasePacketStoredSlot()));
    type = taskRepeat;
}

/**
 * @brief PacketSendTask::validateTask
 * @param dateTime
 * @return
 */
bool PacketSendTask::validateTask(const QDateTime &dateTime)
{
    if(false == busy)
    {
        if(false == initial)
        {
            // debugMessageThread(QString("%1").arg(previousDateTime.secsTo(dateTime)));

            if(5 <= previousDateTime.secsTo(dateTime))
            {
                debugMessageThread("Task validated");
                valid = true;
                previousDateTime = dateTime;
            }
            else
            {
                // debugMessageThread("Task invalidated");
                valid = false;
            }
        }
        else
        {
            initial = false;
            valid = true;
            previousDateTime = dateTime;
        }
    }

    return valid;
}

/**
 * @brief PacketSendTask::processTask
 */
void PacketSendTask::processTask()
{
    valid = false;
    busy = true;
    emit sendSignal();
}

/**
 * @brief PacketSendTask::networkReplySlot
 * @param reply
 */
void PacketSendTask::networkReplySlot(QNetworkReply* reply)
{
    debugMessageThread("");

    if(QNetworkReply::NoError == reply->error())
    {
        QStringList*  packets = CBluuDataManager::Instance()->getPackets();

        debugMessageThread("Packet send OK");
        packets->erase(it);

        if(0 < packets->size())
            emit sendSignal();
        else
            busy = false;
    }
    else
    {
        int err = reply->error();
        debugMessageThread("Packed send FAIL, store in database");
        emit databaseStorePacketSignal(&(*it));
    }
}

/**
 * @brief PacketSendTask::databasePacketStoredSlot
 */
void PacketSendTask::databasePacketStoredSlot()
{
    debugMessageThread("");

    QStringList*  packets = CBluuDataManager::Instance()->getPackets();
    QMutexLocker    locker(CBluuDataManager::Instance()->getMutex());

    packets->erase(it);

    if(0 < packets->size())
        emit sendSignal();
    else
        busy = false;
}

/**
 * @brief PacketSendTask::sendSlot
 */
void PacketSendTask::sendSlot()
{
    debugMessageThread("");

    QStringList*  packets = CBluuDataManager::Instance()->getPackets();

    if(0 < packets->size())
    {
        QJson::Parser   parser;
        QVariantMap     map;

        debugMessageThread("Packets > 0");
        it = packets->begin();
        map = parser.parse((*it).toUtf8()).toMap();
        emit networkSendSignal((*it), map["serial"].toString());
    }
    else
    {
        debugMessageThread("Packets = 0");
        busy = false;
    }
}
