#include "sensormanager.h"

#include <QDir>
#include <QDebug>
#include <QThread>
#include <QLibrary>
#include <QFileInfo>
#include <QTextStream>
#include <QCoreApplication>

#include <abstractsensor.h>

SensorManager::SensorManager(QObject *parent) :
    QObject(parent)
{
}

void SensorManager::loadSensorLibraries()
{
    QDir libraryDir(QDir::cleanPath(QString("%1/../lib")
                                    .arg(qApp->applicationDirPath())));

    foreach(QFileInfo fi, libraryDir.entryInfoList(
                QStringList()<<"libcaim*.so"))
    {
        QLibrary *library = new QLibrary(this);

        library->setFileName(fi.path() + "/" + fi.baseName());

        qDebug()<<"Plugin found:"<<fi.fileName();

        if(library->load())
        {
            FNVersionPtr fnVersionPtr = 0;
            FNInstancesPtr fnInstancesPtr = 0;

            qDebug()<<"Plugin loaded";
            fnVersionPtr = reinterpret_cast<FNVersionPtr>(
                        library->resolve(QTOSTRING(version)));
            fnInstancesPtr = reinterpret_cast<FNInstancesPtr>(
                        library->resolve(QTOSTRING(instances)));
            if(fnVersionPtr && fnInstancesPtr)
            {
                VersionInfo versionInfo = fnVersionPtr();
                AbstractSensorList sensorList = fnInstancesPtr();

                qDebug()<<QString("%1 %2.%3")
                          .arg(versionInfo.pluginName)
                          .arg(versionInfo.majorVersion)
                          .arg(versionInfo.minorVersion);
                qDebug()<<"Number of sensors:"<<sensorList.count();
                foreach(AbstractSensor *sensor, sensorList)
                {
                    QThread *thread = new QThread(this);

                    thread->start();
                    sensor->moveToThread(thread);
                    connect(thread, SIGNAL(started()), sensor, SLOT(plug()));
                    connect(sensor, SIGNAL(dataAvailable()), SLOT(readData()));
                    qDebug()<<"Sensor moved"<<qApp->thread()<<
                              "->"<<sensor->thread();
                    m_pluginsLoaded.insert(versionInfo.pluginName, sensor);
                }
            }
            else
            {
                qCritical()<<"Plugin not compatible";
                library->unload();
                delete library;
            }

        }
        else
        {
            qCritical()<<"Plugin not loaded"<<library->errorString();
            delete library;
        }
    }
}

void SensorManager::readData()
{
    QByteArray data;
    QTextStream stream(&data, QIODevice::WriteOnly);
    AbstractSensor *sensor = dynamic_cast<AbstractSensor*>(sender());

    sensor->serialize(&stream);
    stream.flush();
    qDebug()<<__PRETTY_FUNCTION__<<sensor->metaObject()->className()<<data<<
              QThread::currentThread();
}

