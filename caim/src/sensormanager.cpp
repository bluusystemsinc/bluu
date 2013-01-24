#include "sensormanager.h"

#include <QDir>
#include <QDebug>
#include <QThread>
#include <QLibrary>
#include <QFileInfo>
#include <QTextStream>
#include <QMetaObject>
#include <QCoreApplication>

#include <debug.h>
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
                    connect(sensor, SIGNAL(unplugged()),
                            SLOT(sensorUnplugged()));
                    qDebug()<<"Sensor moved"<<qApp->thread()<<
                              "->"<<sensor->thread();
                    m_pluginsLoaded.insert(thread, sensor);
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

void SensorManager::unloadSensorsSlot()
{
    qDebug() << __PRETTY_FUNCTION__;

    PluginsLoadedMap::iterator  it = m_pluginsLoaded.begin();

    while(0 < m_pluginsLoaded.count())
    {
        QThread*        thread = NULL;
        AbstractSensor*     sensor = NULL;

        it = m_pluginsLoaded.begin();
        thread = it.key();

        if(NULL != thread)
        {
            sensor = m_pluginsLoaded.value(thread);

            if(NULL != sensor)
                delete sensor;

            thread->exit();
            m_pluginsLoaded.remove(thread);
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

void SensorManager::sensorUnplugged()
{
    log()<<sender()->metaObject()->className()<<"unplugged";
}
