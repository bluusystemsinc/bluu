#include "randomsensor.h"

#include <QTime>
#include <QDebug>

addVersionInfo()

extern "C" AbstractSensorList instances()
{
    AbstractSensorList list;

    list.append(new RandomSensor);
    return list;
}

RandomSensor::RandomSensor(QObject *parent)
    : AbstractSensor(parent)
{
}

bool RandomSensor::plug()
{
    qsrand(QTime::currentTime().msec());
    startTimer(1000);

    return true;
}

void RandomSensor::serialize(QTextStream *stream)
{
    int value = qrand();

    (*stream)<<QString::number(value);
}

void RandomSensor::timerEvent(QTimerEvent *)
{
    qDebug()<<__PRETTY_FUNCTION__;
    emit dataAvailable();
}
