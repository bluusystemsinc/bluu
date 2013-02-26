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
void DatabaseSendTask::processTask(const QDateTime &dateTime)
{
}

/**
 * @brief DatabaseSendTask::setSendTime
 * @param time
 */
void DatabaseSendTask::setSendTime(const QDateTime& time)
{
    sendTime = time;
}
