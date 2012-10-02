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
    FT_DEVICE_LIST_INFO_NODE *devInfo;

    qDebug()<<"I'm at working at"<<QThread::currentThread();

    ftStatus = FT_CreateDeviceInfoList(&numDevices);
    if(FT_OK != ftStatus)
    {
        qCritical()<<"Error FT_CreateDeviceInfoList"<<ftStatus;
        return false;
    }
    qDebug()<<"FT_CreateDeviceInfoList"<<ftStatus;
    devInfo = new FT_DEVICE_LIST_INFO_NODE[numDevices];
    ftStatus = FT_GetDeviceInfoList(devInfo, &numDevices);
    if(FT_OK != ftStatus)
    {
        qCritical()<<"Error FT_GetDeviceInfoList"<<ftStatus;
        return false;
    }
    for(DWORD i = 0; i < numDevices; i++)
    {
        FT_DEVICE_LIST_INFO_NODE *node = devInfo + i;

        ftStatus = FT_Open(i, &(node->ftHandle));
        if(FT_OK != ftStatus)
        {
            qCritical()<<"Error FT_Open"<<ftStatus;
            return false;
        }

        qDebug()<<"Device"<<i;
        qDebug()<<" Flags"<<node->Flags;
        qDebug()<<" Type"<<node->Type;
        qDebug()<<" ID"<<node->ID;
        qDebug()<<" LocId"<<node->LocId;
        qDebug()<<" Serial number"<<node->SerialNumber;
        qDebug()<<" Description"<<node->Description;
        qDebug()<<" ftHandle"<<node->ftHandle;
    }
    return true;
}

void FtdiSensor::serialize(QTextStream */*stream*/)
{
}
