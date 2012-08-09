#include <QTime>
#include <QDebug>
#include <QRegExp>
#include <qextserialenumerator.h>

#include "ftdiserialport.h"

int main(int /*argc*/, char** /*argv*/)
{
    QList<QextPortInfo> ports = QextSerialEnumerator::getPorts();
    qDebug() << "List of ports:";
    foreach (QextPortInfo info, ports) {
        if(QRegExp("ttyUSB\\d").exactMatch(info.portName))
        {
            FTDISerialPort serialPort(info.portName);

            qDebug() << "port name:"       << info.portName;
            qDebug() << "friendly name:"   << info.friendName;
            qDebug() << "physical name:"   << info.physName;
            qDebug() << "enumerator name:" << info.enumName;
            qDebug() << "vendor ID:"       << info.vendorID;
            qDebug() << "product ID:"      << info.productID;

            qDebug() << "===================================";

            forever
            {
                if(serialPort.bytesAvailable())
                {
                    QTime time = QTime::currentTime();

                    qDebug()<<time<<serialPort.readAll();
                }
            }
        }
    }
    return 0;
}
