#include "sensormanager.h"

#include <QDir>
#include <QDebug>
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
        qDebug()<<"Plugin found:"<<fi.fileName();
    }
}
