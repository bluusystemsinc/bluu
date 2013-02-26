#include "datamanagerworkerthread.h"
#include "debug.h"
#include <QDateTime>

/**
 * @brief DataManagerWorkerThread::DataManagerWorkerThread
 * @param parent
 */
DataManagerWorkerThread::DataManagerWorkerThread(QObject* parent)
                       : QThread(parent)
{
}

/**
 * @brief DataManagerWorkerThread::run
 */
void DataManagerWorkerThread::run()
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

        //if((time.addSecs(-30) < midnight) && (time.addSecs(30) > midnight))
        {
            debugMessageThread("I'm here!");
        }
    }
}
