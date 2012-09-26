#include "ftdisensor.h"

addVersionInfo()

FtdiSensor::FtdiSensor(QObject *parent) :
    AbstractSensor(parent)
{
}

void FtdiSensor::serialize(QTextStream *stream)
{
}
