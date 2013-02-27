#include "debug.h"
#include "databasesendtask.h"

/**
 * @brief DatabaseSendTask::DatabaseSendTask
 */
DatabaseSendTask::DatabaseSendTask()
                : Task()
{
    QTime       midnight(0, 0, 0, 0);

    type = taskRepeat;
    sendTime = QDateTime::currentDateTime();
    sendTime.setTime(midnight);
}

/**
 * @brief DatabaseSendTask::processTask
 * @param dateTime
 */
void DatabaseSendTask::processTask()
{
    valid = false;
    busy = true;
}

/**
 * @brief DatabaseSendTask::validateTask
 * @param dateTime
 * @return
 */
bool DatabaseSendTask::validateTask(const QDateTime& dateTime)
{
    Task::validateTask(dateTime);

    if(false == busy)
    {
        if(false == initial)
        {
            if(5 <= previousDateTime.secsTo(dateTime))
            {

            }
        }
        else
        {
            initial = false;
            valid = true;
            previousDateTime = dateTime;
        }
    }

    /*
    if(false == busy)
    {
        QTime   currentTm = dateTime.time();
        QTime   sendTm = sendTime.time();

        if((currentTm.addSecs(-1) < sendTm) && (currentTm.addSecs(1) > sendTm))
        {
            valid = true;
            debugMessageThread("Task validated");
        }
        else
        {
            valid = false;
            debugMessageThread("Task invalidated");
        }
    }
    else
        valid = false;
        */

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
