#include "debug.h"
#include "debugger.h"
#include "databasesendtask.h"
#include "databasemanager.h"

#define HOURS_23 82800

/**
 * @brief DatabaseSendTask::DatabaseSendTask
 */
DatabaseSendTask::DatabaseSendTask()
                : Task()
{
    connect(this, SIGNAL(debugSignal(QString)), CBluuDebugger::Instance(), SLOT(debugSlot(QString)));
    connect(this, SIGNAL(databaseSendPacketsSignal()), CBluuDatabaseManager::Instance(), SLOT(databaseSendPacketsSlot()));
    connect(CBluuDatabaseManager::Instance(), SIGNAL(databaseSendPacketsSignal()), this, SLOT(databaseSendPacketsSlot()));
    previousDateTime = currentDateTime = QDateTime::currentDateTime();
    type = taskRepeat;
}

/**
 * @brief DatabaseSendTask::processTask
 * @param dateTime
 */
void DatabaseSendTask::processTask()
{
    valid = false;
    busy = true;
    emit databaseSendPacketsSignal();
}

/**
 * @brief DatabaseSendTask::databaseSendPacketsSlot
 */
void DatabaseSendTask::databaseSendPacketsSlot()
{
    busy = false;
    valid = false;
}

/**
 * @brief DatabaseSendTask::validateTask
 * @param dateTime
 * @return
 */
bool DatabaseSendTask::validateTask(const QDateTime& dateTime)
{
    valid = false;

    if(false == busy)
    {
        QTime       midnight(0, 0, 0, 0);

        if(dateTime.time() == midnight)
        {
            if(HOURS_23 <= previousDateTime.secsTo(dateTime))
            {
                debugMessageThread("Task validated");
                valid = true;
                previousDateTime = dateTime;
            }
        }
    }

    return valid;
}

/**
 * @brief DatabaseSendTask::setSendTime
 * @param time
 */
void DatabaseSendTask::setSendTime(const QDateTime& time)
{
    sendTime = time;
}
