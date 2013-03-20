#ifndef BTSENSOR_H
#define BTSENSOR_H

#include <abstractsensor.h>

class BtSensor : public AbstractSensor
{
    Q_OBJECT

public:
    BtSensor(QObject* parent);

public slots:
    virtual bool plug();
    virtual void serialize(QByteArray* buffer);
    virtual void serialize(QTextStream* stream);
};

#endif // BTSENSOR_H
