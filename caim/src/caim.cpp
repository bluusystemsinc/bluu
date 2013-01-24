#include <QDebug>
#include <QThread>
#include <QCoreApplication>

#include "sensormanager.h"
#include "unixsignals.h"

int main(int argc, char **argv)
{
    QCoreApplication app(argc, argv);
    SensorManager sm;

    CBluuUnixSignals::Instance()->setupUnixSignalHandlers();
    app.setOrganizationName(ORGANIZATION_NAME);
    app.setOrganizationDomain(ORGANIZATION_DOMAIN);
    app.setApplicationName(APPLICATION_NAME);
    app.setApplicationVersion(QString("0.1.%1").arg(APPLICATION_VERSION));

    qDebug()<<QString("Starting %1 %2 %3...").arg(app.organizationName())
              .arg(app.applicationName()).arg(app.applicationVersion());

    qDebug()<<"Ideal thread count:"<<QThread::idealThreadCount();
    sm.connect(CBluuUnixSignals::Instance(), SIGNAL(unloadSensorsSignal()), SLOT(unloadSensorsSlot()));
    sm.loadSensorLibraries();

    return app.exec();
}

