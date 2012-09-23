#ifndef ABSTRACTSENSOR_H
#define ABSTRACTSENSOR_H

#include <QObject>

class AbstractSensor : public QObject
{
    Q_OBJECT

public:
    AbstractSensor(QObject *parent = 0);
};

#endif // ABSTRACTSENSOR_H
