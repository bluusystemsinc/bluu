#ifndef DATABASESENDTASK_H
#define DATABASESENDTASK_H

#include "task.h"

/**
 * @brief The DatabaseSendTask class
 */
class DatabaseSendTask : public Task
{
    Q_OBJECT

protected:
    QDateTime   sendTime;

public:
    DatabaseSendTask();
    virtual bool validateTask(const QDateTime& dateTime);
    void setSendTime(const QDateTime& time);

signals:
    void debugSignal(QString debugMessage);

public slots:
    virtual void processTask();
};

#endif // DATABASESENDTASK_H
