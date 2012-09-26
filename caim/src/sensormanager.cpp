#include "sensormanager.h"

#include <QDir>
#include <QDebug>
#include <QLibrary>
#include <QFileInfo>
#include <QCoreApplication>

#include <abstractsensor.h>

SensorManager::SensorManager(QObject *parent) :
    QObject(parent)
{
}

void SensorManager::loadSensorLibraries()
{
    QString libraryPath = QDir::cleanPath(QString("%1/../lib")
                                          .arg(qApp->applicationDirPath()));
    QDir libraryDir(libraryPath);

    foreach(QFileInfo fi, libraryDir.entryInfoList(
                QStringList()<<"libcaim*.so"))
    {
        QLibrary library(fi.path() + "/" + fi.baseName());

        qDebug()<<"Plugin found:"<<fi.fileName();

        if(library.load())
        {
            fnVersionPointer version = 0;
            VersionInfo versionInfo;

            qDebug()<<"Plugin loaded";
            version = reinterpret_cast<fnVersionPointer>(
                        library.resolve("version"));

            versionInfo = version();
            qDebug()<<"VERSION!!!!:"<<versionInfo.pluginName
                   <<versionInfo.majorVersion<<versionInfo.minorVersion;
            library.unload();
        }
        else
        {
            qCritical()<<"Plugin not loaded"<<library.errorString();
        }
    }
}
