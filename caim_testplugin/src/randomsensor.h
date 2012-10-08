#ifndef RANDOMSENSOR_H
#define RANDOMSENSOR_H

#include <abstractsensor.h>

class QFile;

class RandomSensor : public AbstractSensor
{
    Q_OBJECT

public:
    explicit RandomSensor(QObject *parent = 0);

public slots:
    virtual bool plug();
    virtual void serialize(QTextStream *stream);

protected:
    void timerEvent(QTimerEvent *);
};

#endif // RANDOMSENSOR_H
