#include <QTime>
#include <QFile>
#include <QDebug>
#include <QRegExp>
#include <ftd2xx.h>
#include <qextserialenumerator.h>

#include "ftdiserialport.h"

int main(int /*argc*/, char** /*argv*/)
{
    FT_STATUS result = FT_OK;
    DWORD dwNumDevices;

    result = FT_CreateDeviceInfoList(&dwNumDevices);

    if(FT_OK == result)
    {
        qDebug()<<"Num devices:"<<dwNumDevices;
    }
    else if(dwNumDevices == 0)
        qFatal("No devices installed");
    else
        qFatal("ERROR");

    for(DWORD i = 0; i < dwNumDevices; i++)
    {
        FT_DEVICE_LIST_INFO_NODE device;

        result = FT_GetDeviceInfoList(&device, &dwNumDevices);

        qDebug()<<"Flags"<<device.Flags;
        qDebug()<<"Type"<<device.Type;
        qDebug()<<"ID"<<device.ID;
        qDebug()<<"LocId"<<device.LocId;
        qDebug()<<"SerialNumber"<<device.SerialNumber;
        qDebug()<<"Description"<<device.Description;
        qDebug()<<"Handle"<<device.ftHandle;
    }


//    QList<QextPortInfo> ports = QextSerialEnumerator::getPorts();
//    qDebug() << "List of ports:";
//    foreach (QextPortInfo info, ports) {
//        if(QRegExp("ttyUSB\\d").exactMatch(info.portName))
//        {
//            bool result;
//            QFile file("/tmp/dump");
//            FTDISerialPort serialPort(info.portName);
//            QDataStream stream;

//            qDebug() << "port name:"       << info.portName;
//            qDebug() << "friendly name:"   << info.friendName;
//            qDebug() << "physical name:"   << info.physName;
//            qDebug() << "enumerator name:" << info.enumName;
//            qDebug() << "vendor ID:"       << info.vendorID;
//            qDebug() << "product ID:"      << info.productID;

//            qDebug() << "===================================";

//            result = serialPort.open(QIODevice::ReadWrite);
////            A4 01 4A 00 EF
//            stream.setDevice(&serialPort);
//            stream<<(char)0xa4<<(char)0x01<<(char)0x4a<<(char)0<<(char)0xef;

//            qDebug()<<"Result?"<<result<<"("<<serialPort.errorString()<<")";

//            forever
//            {
//                if(serialPort.bytesAvailable())
//                {
//                    QByteArray data = serialPort.readAll();
//                    QTime time = QTime::currentTime();

//                    result = file.open(QIODevice::WriteOnly | QFile::Append);
//                    qDebug()<<time<<data;
//                    file.write(data);
//                    file.close();
//                }
//            }
//            file.close();
//        }
//    }
    return EXIT_SUCCESS;
}
