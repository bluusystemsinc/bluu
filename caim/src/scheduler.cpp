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
void Scheduler::registerTask(Task *task)
{
    tasks.append(task);
}

/**
 * @brief DataManagerWorkerThread::run
 */
void Scheduler::run()
{
    /*
    // QDateTime   init = QDateTime::currentDateTime();
    */
    QDateTime   checkpoint;
    QTime       midnight(0, 0, 0, 0);

    checkpoint.setTime(midnight);  // initially check

    while(1)
    {
        QDateTime   current = QDateTime::currentDateTime();
        QTime       time = current.time();

        if(0 == time.second())
            debugMessageThread("I'm here!");

        /*
        if((time.addSecs(-30) < midnight) && (time.addSecs(30) > midnight))
        {
            debugMessageThread("I'm here!");
        }
        */
    }
}
