#include "datamanager.h"
#include "datamanagerthread.h"
#include "scheduler.h"
#include "dataparser.h"
#include "debug.h"
#include "webrequest.h"
#include "databasesendtask.h"
#include "packetsendtask.h"
#include <QMutexLocker>

/**
 * @brief DataManager::DataManager TODO
 * @param parent
 */
DataManager::DataManager(QObject* parent) :
    QObject(parent)
{
    // DataManagerThread*  thread = new DataManagerThread();
    Scheduler*    scheduler = new Scheduler();
    DatabaseSendTask*   databaseSendTask = new DatabaseSendTask();
    PacketSendTask*     packetSendTask = new PacketSendTask();

    // thread->start();
    packetSendTask->moveToThread(scheduler);
    databaseSendTask->moveToThread(scheduler);
    scheduler->registerTask(packetSendTask);
    scheduler->registerTask(databaseSendTask);
    scheduler->start();
}

/**
 * @brief DataManager::processData TODO
 * @param data
 */
void DataManager::processData(QByteArray* data)
{
    debugMessage();

    if(NULL != data)
    {
        int     count = data->count();

        if(0 == count % 9)
        {
            if(9 == count)
            {
                CBluuDataParser::Instance()->parseData(data);
            }
            else
            {
                for(int i = 0; i < count % 9; i++)
                {
                    QByteArray  tmp = data->mid(i * 9, 9);

                    CBluuDataParser::Instance()->parseData(&tmp);
                }
            }
        }
        else
        {
            debugMessage() << "Some data are missing";
        }
    }
}

/**
 * @brief DataManager::getMutex
 * @return
 */
QMutex *DataManager::getMutex()
{
    debugMessage();

    return &mutex;
}

QStringList* DataManager::getPackets()
{
    debugMessage();

    return &packets;
}

/**
 * @brief DataManager::packedReadySlot TODO
 */
void DataManager::packedReadySlot(QByteArray json)
{
    debugMessage();

    QMutexLocker    locker(&mutex);

    packets.append(json);
}
