#ifndef BTSENSOR_H
#define BTSENSOR_H

#include <abstractsensor.h>
#include "btdevice.h"

class BtSensor : public AbstractSensor
{
    Q_OBJECT

protected:
    BtDevice*   device;

public:
    BtSensor(QObject* parent = 0);

public slots:
    virtual bool plug();
    virtual void serialize(QByteArray* buffer);
    virtual void serialize(QTextStream* stream);
};

#endif // BTSENSOR_H
