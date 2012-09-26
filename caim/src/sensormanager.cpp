#include "sensormanager.h"

#include <QDir>
#include <QDebug>
#include <QLibrary>
#include <QFileInfo>
#include <QCoreApplication>

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
        QLibrary library(fi.fileName());

        qDebug()<<"Plugin found:"<<fi.fileName();

        if(library.load())
        {
            qDebug()<<"Plugin loaded";
            library.unload();
        }
    }
}
