#include <QDebug>
#include <QRegExp>
#include <qextserialport.h>
#include <qextserialenumerator.h>

int main(int /*argc*/, char** /*argv*/)
{
    QList<QextPortInfo> ports = QextSerialEnumerator::getPorts();
    qDebug() << "List of ports:";
    foreach (QextPortInfo info, ports) {
        if(QRegExp("ttyUSB\\d").exactMatch(info.portName))
        {
            QextSerialPort port(info.physName, QextSerialPort::EventDriven);

            port.setBaudRate(BAUD57600);
            port.setParity(PAR_NONE);
            port.setDataBits(DATA_8);

            qDebug() << "port name:"       << info.portName;
            qDebug() << "friendly name:"   << info.friendName;
            qDebug() << "physical name:"   << info.physName;
            qDebug() << "enumerator name:" << info.enumName;
            qDebug() << "vendor ID:"       << info.vendorID;
            qDebug() << "product ID:"      << info.productID;

            qDebug() << "===================================";

            forever
            {
                if(port.bytesAvailable())
                {
                }
            }
        }
    }
    return 0;
}
