#ifndef BTDEVICETHREAD_H
#define BTDEVICETHREAD_H

#include <QThread>

/**
 * @brief The BtDeviceThread class
 */
class BtDeviceThread : public QThread
{
    Q_OBJECT

protected:
    virtual void run();

public:
    explicit BtDeviceThread(QObject* parent = 0);
    
signals:
    
public slots:
    
};

#endif // BTDEVICETHREAD_H
