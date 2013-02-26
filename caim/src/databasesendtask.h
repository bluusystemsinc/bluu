#ifndef DATABASESENDTASK_H
#define DATABASESENDTASK_H

#include "task.h"

/**
 * @brief The DatabaseSendTask class
 */
class DatabaseSendTask : public Task
{
protected:
    QDateTime   sendTime;

public:
    DatabaseSendTask();
    virtual void processTask(const QDateTime &dateTime);
    void setSendTime(const QDateTime& time);
};

#endif // DATABASESENDTASK_H
