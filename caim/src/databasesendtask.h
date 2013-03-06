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
    void databaseSendPacketsSignal(QDateTime time);

public slots:
    virtual void processTask();
    void databaseSendPacketsSlot();
};

#endif // DATABASESENDTASK_H
