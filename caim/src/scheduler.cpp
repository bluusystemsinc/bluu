#include "scheduler.h"
#include "debug.h"
#include "debugger.h"
#include <QDateTime>

/**
 * @brief DataManagerWorkerThread::DataManagerWorkerThread
 * @param parent
 */
Scheduler::Scheduler(QObject* parent)
         : QThread(parent)
{
    connect(this, SIGNAL(debugSignal(QString)), CBluuDebugger::Instance(), SLOT(debugSlot(QString)));
}

/**
 * @brief Scheduler::registerTask
 * @param task
 */
void Scheduler::registerTask(Task* task)
{
    task->moveToThread(this);
    tasks.append(task);
}

/**
 * @brief DataManagerWorkerThread::run
 */
void Scheduler::run()
{
    QDateTime   checkpoint;
    QTime       midnight(0, 0, 0, 0);
    QList<Task*>::iterator  it;

    checkpoint.setTime(midnight);  // initially check

    for(it = tasks.begin(); it != tasks.end(); it++)
    {
        QThread*    thread = new QThread(parent());

        (*it)->moveToThread(thread);
        thread->start();
    }

    while(1)
    {
        QList<Task*>::iterator  it;

        QDateTime   current = QDateTime::currentDateTime();

        for(it = tasks.begin(); it != tasks.end(); it++)
        {
            if(true == (*it)->validateTask(current))
                (*it)->processTask();
        }
    }
}
