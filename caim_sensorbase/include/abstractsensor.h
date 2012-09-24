#ifndef ABSTRACTSENSOR_H
#define ABSTRACTSENSOR_H

#include <QObject>

class QTextStream;

class AbstractSensor : public QObject
{
    Q_OBJECT

public slots:
    virtual void serialize(QTextStream *stream) = 0;

signals:
    void dataAvailable();
};

typedef QList<AbstractSensor*> AbstractSensorList;

AbstractSensorList instances();

#endif // ABSTRACTSENSOR_H
