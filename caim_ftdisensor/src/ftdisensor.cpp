#include "ftdisensor.h"

#include <QDebug>
#include <QThread>
#include <QStringList>

#include <unistd.h>
#include <ftd2xx.h>

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

bool FtdiSensor::plug()
{
    FT_STATUS ftStatus;
    DWORD numDevices = 0;

    qDebug()<<"I'm at working at"<<QThread::currentThread();

    ftStatus = FT_CreateDeviceInfoList(&numDevices);
    if(FT_OK != ftStatus)
    {
        qCritical()<<"Error FT_CreateDeviceInfoList"<<ftStatus;
        return false;
    }
    qDebug()<<"FT_CreateDeviceInfoList"<<ftStatus;
    for(DWORD i = 0; i < numDevices; i++)
    {
        qDebug()<<"Device"<<i;
    }
    return true;
}

void FtdiSensor::serialize(QTextStream */*stream*/)
{
}
