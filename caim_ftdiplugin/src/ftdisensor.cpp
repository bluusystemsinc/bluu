#include "ftdisensor.h"

#include <QDebug>
#include <QThread>
#include <QStringList>

#include <unistd.h>
#include <ftd2xx.h>

#include "ftdidevice.h"

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
    m_device = new FtdiDevice(this);

    if(!m_device->open(0))
    {
        emit unplugged();
        return false;
    }
    qDebug()<<"FTDIDevice open";
    connect(m_device, SIGNAL(readyRead()), SIGNAL(dataAvailable()));

    emit plugged();
    return true;
}

void FtdiSensor::serialize(QTextStream *stream)
{
    qDebug()<<__PRETTY_FUNCTION__;
    QTextStream out(stream->device());

    out<<m_device->readAll();
}
