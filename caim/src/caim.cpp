#include <QDebug>
#include <QCoreApplication>

int main(int argc, char **argv)
{
    QCoreApplication app(argc, argv);

    app.setOrganizationName(ORGANIZATION_NAME);
    app.setOrganizationDomain(ORGANIZATION_DOMAIN);
    app.setApplicationName(APPLICATION_NAME);
    app.setApplicationVersion(QString("0.1.%1").arg(APPLICATION_VERSION));
    qDebug()<<QString("Starting %1 %2 %3...").arg(app.organizationName())
              .arg(app.applicationName()).arg(app.applicationVersion());

    return app.exec();
}
