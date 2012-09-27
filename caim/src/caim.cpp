#include <QDebug>
#include <QThread>
#include <QCoreApplication>

#include "sensormanager.h"

int main(int argc, char **argv)
{
    QCoreApplication app(argc, argv);
    SensorManager sm;

    app.setOrganizationName(ORGANIZATION_NAME);
    app.setOrganizationDomain(ORGANIZATION_DOMAIN);
    app.setApplicationName(APPLICATION_NAME);
    app.setApplicationVersion(QString("0.1.%1").arg(APPLICATION_VERSION));

    qDebug()<<QString("Starting %1 %2 %3...").arg(app.organizationName())
              .arg(app.applicationName()).arg(app.applicationVersion());

    qDebug()<<"Ideal thread count:"<<QThread::idealThreadCount();

    sm.loadSensorLibraries();

    return app.exec();
}

