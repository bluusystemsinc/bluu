#include "datamanager.h"
#include "datamanagerthread.h"
#include "scheduler.h"
#include "dataparser.h"
#include "debug.h"
#include "webrequest.h"
#include "databasesendtask.h"
#include <QMutexLocker>

/**
 * @brief DataManager::DataManager TODO
 * @param parent
 */
DataManager::DataManager(QObject* parent) :
    QObject(parent)
{
    DataManagerThread*  thread = new DataManagerThread();
    Scheduler*    scheduler =new Scheduler();
    DatabaseSendTask*   databaseSendTask = new DatabaseSendTask();

    thread->start();
    scheduler->registerTask(databaseSendTask);
    scheduler->start();

    /*
    QThread*    workerThread = new QThread(this);

    packets.clear();
    connect(workerThread, SIGNAL(started()), CBluuDataManagerWorker::Instance(), SLOT(workSlot()));
    connect(workerThread, SIGNAL(finished()), CBluuDataManagerWorker::Instance(), SLOT(deleteLater()));
    CBluuDataManagerWorker::Instance()->moveToThread(workerThread);
    workerThread->start();
    */
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
