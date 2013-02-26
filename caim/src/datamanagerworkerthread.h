#ifndef DATAMANAGERWORKERTHREAD_H
#define DATAMANAGERWORKERTHREAD_H

#include <QThread>
#include <QDateTime>

/**
 * @brief The DataManagerWorkerThread class
 */
class DataManagerWorkerThread : public QThread
{
    Q_OBJECT

private:
    QDateTime   previous;

protected:
    virtual void run();

public:
    explicit DataManagerWorkerThread(QObject *parent = 0);
    
signals:
    void debugSignal(QString debugMessage);
    
public slots:
    
};

#endif // DATAMANAGERWORKERTHREAD_H
