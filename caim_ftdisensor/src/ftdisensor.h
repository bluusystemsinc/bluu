#ifndef FTDISENSOR_H
#define FTDISENSOR_H

#include <abstractsensor.h>

class FtdiSensor : public AbstractSensor
{
    Q_OBJECT
public:
    explicit FtdiSensor(QObject *parent = 0);

    Q_INVOKABLE virtual void plug();

    virtual void serialize(QTextStream *stream);
};

#endif // FTDISENSOR_H
