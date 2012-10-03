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
    FT_DEVICE_LIST_INFO_NODE *node;
    QByteArray array;

    qDebug()<<"I'm at working at"<<QThread::currentThread();

    ftStatus = FT_CreateDeviceInfoList(&numDevices);
    if(FT_OK != ftStatus)
    {
        qCritical()<<"Error FT_CreateDeviceInfoList"<<ftStatus;
        return false;
    }
    qDebug()<<"FT_CreateDeviceInfoList"<<ftStatus;
    node = devInfo = new FT_DEVICE_LIST_INFO_NODE[numDevices];
    ftStatus = FT_GetDeviceInfoList(devInfo, &numDevices);
    if(FT_OK != ftStatus)
    {
        qCritical()<<"Error FT_GetDeviceInfoList"<<ftStatus;
        return false;
    }


    ftStatus = FT_Open(0, &(node->ftHandle));
    if(FT_OK != ftStatus)
    {
        qCritical()<<"Error FT_Open"<<ftStatus;
        return false;
    }
    ftStatus = FT_SetBaudRate(node->ftHandle, FT_BAUD_57600);
    ftStatus = FT_SetDataCharacteristics(node->ftHandle, FT_BITS_8,
                                         FT_STOP_BITS_1, FT_PARITY_NONE);

    qDebug()<<"Flags"<<node->Flags;
    qDebug()<<"Type"<<node->Type;
    qDebug()<<"ID"<<node->ID;
    qDebug()<<"LocId"<<node->LocId;
    qDebug()<<"Serial number"<<node->SerialNumber;
    qDebug()<<"Description"<<node->Description;
    qDebug()<<"ftHandle"<<node->ftHandle;

    while(FT_OK == ftStatus)
    {
        DWORD rxBytes, txBytes, bytesReceived, event;
        char *bytes;

        ftStatus = FT_GetStatus(node->ftHandle, &rxBytes, &txBytes, &event);
        if(rxBytes > 0)
        {
            bytes = new char[rxBytes];
            ftStatus = FT_Read(node->ftHandle, bytes, rxBytes, &bytesReceived);
            qDebug()<<bytes;
            if(bytes[0] == 'U' && bytes[1] == 'B')
            {
                qDebug()<<"Final array:"<<array.toHex()<<array.toInt();
                array.setRawData(bytes, rxBytes);
            }
            else
                array.append(bytes, rxBytes);
            delete [] bytes;

        }
    }
//    while(FT_OK == FT_Read(node->ftHandle, buffer, )
    return true;
}

void FtdiSensor::serialize(QTextStream */*stream*/)
{
}
