#ifndef DATAMANAGERWORKERTHREAD_H
#define DATAMANAGERWORKERTHREAD_H

#include "task.h"
#include <QThread>
#include <QDateTime>
#include <QList>

/**
 * @brief The DataManagerWorkerThread class
 */
class Scheduler : public QThread
{
    Q_OBJECT

private:
    QDateTime   previous;

protected:
    QList<Task*>    tasks;

protected:
    virtual void run();

public:
    explicit Scheduler(QObject *parent = 0);
    void registerTask(Task* task);
    
signals:
    void debugSignal(QString debugMessage);
    
public slots:
    
};

#endif // DATAMANAGERWORKERTHREAD_H
