#ifndef BTDEVICE_H
#define BTDEVICE_H

#include "btdevicethread.h"
#include <QObject>

/**
 * @brief The BtDevice class
 */
class BtDevice : public QObject
{
    Q_OBJECT

protected:
    BtDeviceThread  thread;

public:
    explicit BtDevice(QObject *parent = 0);
    
signals:
    
public slots:
    
};

#endif // BTDEVICE_H
