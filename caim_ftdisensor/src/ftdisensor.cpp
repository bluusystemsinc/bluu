#include "ftdisensor.h"

#include <QDebug>
#include <QThread>
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

void FtdiSensor::plug()
{
    qDebug()<<"I'm at working at"<<QThread::currentThread();
}

void FtdiSensor::serialize(QTextStream */*stream*/)
{
}
