#include "ftdisensor.h"

#include <QStringList>

addVersionInfo()

extern "C" AbstractSensorList instances()
{
    AbstractSensorList list;

    list.append(new FtdiSensor);
    return list;
}

FtdiSensor::FtdiSensor(QObject *parent) :
    AbstractSensor(parent)
{
}

void FtdiSensor::serialize(QTextStream */*stream*/)
{
}
