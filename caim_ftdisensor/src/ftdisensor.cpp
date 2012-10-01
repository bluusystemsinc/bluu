#include "ftdisensor.h"

#include <QDebug>
#include <QThread>
#include <QStringList>
#include <QFile>

addVersionInfo()

extern "C" AbstractSensorList instances()
{
    AbstractSensorList list;
    list.append(new FtdiSensor);

    FtdiSensor *timeoutSensor = new FtdiSensor(2000);
    list.append(timeoutSensor);


    return list;
}

FtdiSensor::FtdiSensor(QObject *parent) :
    AbstractSensor(parent)
{
}

FtdiSensor::FtdiSensor(int timeout, QObject *parent) :
    AbstractSensor(parent)
{
    timer = new QTimer(this);
    connect(timer, SIGNAL(timeout()), this,SLOT(timerSlot()));

    timer->start(timeout);
}

void FtdiSensor::plug()
{
    qDebug()<<"I'm at working at"<<QThread::currentThread();
}

void FtdiSensor::serialize(QTextStream */*stream*/)
{
}

void FtdiSensor::timerSlot()
{
    QFile file("/dev/urandom");
    quint32 x;

    if(!file.open(QIODevice::ReadOnly))
    {
        qDebug() << "Can not open for read\n";
    }

    QDataStream in(&file);
    in >> x;

    qDebug() << "Timer elipsed" << x << "\n";

}
