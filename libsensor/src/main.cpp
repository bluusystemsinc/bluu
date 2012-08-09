#include <QTime>
#include <QFile>
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
            bool result;
            QFile file("/tmp/dump");
            FTDISerialPort serialPort(info.portName);

            qDebug() << "port name:"       << info.portName;
            qDebug() << "friendly name:"   << info.friendName;
            qDebug() << "physical name:"   << info.physName;
            qDebug() << "enumerator name:" << info.enumName;
            qDebug() << "vendor ID:"       << info.vendorID;
            qDebug() << "product ID:"      << info.productID;

            qDebug() << "===================================";

            result = serialPort.open(QIODevice::ReadWrite);

            qDebug()<<"Result?"<<result<<"("<<serialPort.errorString()<<")";

            forever
            {
                if(serialPort.bytesAvailable())
                {
                    QByteArray data = serialPort.readAll();
                    QTime time = QTime::currentTime();

                    result = file.open(QIODevice::WriteOnly | QFile::Append);
                    qDebug()<<"Open?"<<result;
                    qDebug()<<time<<data;
                    file.write(data);
                    file.close();
                }
            }
            file.close();
        }
    }
    return 0;
}
