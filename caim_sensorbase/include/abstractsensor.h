#ifndef ABSTRACTSENSOR_H
#define ABSTRACTSENSOR_H

#include <QObject>

class AbstractSensor : public QObject
{
    Q_OBJECT

public slots:
signals:
    void dataAvailable();
};

#endif // ABSTRACTSENSOR_H
