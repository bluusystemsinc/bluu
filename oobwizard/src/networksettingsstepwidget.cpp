#include "networksettingsstepwidget.h"
#include "QFile"
#include <QTextStream>
#include <QDebug>

NetworkSettingsStepWidget::NetworkSettingsStepWidget(QWidget *parent) :
    QWidget(parent)
{
    setupUi(this);

    connect(backButton, SIGNAL(clicked()), SIGNAL(back()));
    connect(nextButton, SIGNAL(clicked()), SIGNAL(next()));
    connect(nextButton, SIGNAL(clicked()), this, SLOT(createConnetion()));
}

void NetworkSettingsStepWidget::createConnetion()
{
    QString program("wiredConnectionScript.sh");

    QFile file(program);
    file.open(QIODevice::WriteOnly | QIODevice::Text);
    QTextStream out(&file);
    out << "#/bin/sh\n";

    if(wiredDHCPRadioBtn->isChecked())
    {
        out << "/sbin/dhclient\n";
    }
    else
    {
      out << "lanName=\"$(ifconfig | awk \"/^eth/ {print \\$1}\")\"\n";
      out << "/sbin/ifconfig $lanName " << staticIpAddrlineEdit->text() << " netmask " << subnetMaskLineEdit->text() << " broadcast " << defaultGatewayLineEdit->text() << "\n";
      out << "/sbin/route add default gw " << defaultGatewayLineEdit->text() << "\n";
    }
    file.close();

    if(dnsNoRadioBtn->isChecked())
    {
        QString nameserverFileName("/etc/resolv.conf");
        QFile nameserverFile(nameserverFileName);

        bool ret = nameserverFile.open(QIODevice::Append | QIODevice::Text);
        if(ret)
            qDebug() << "ok\n";
        else
            qDebug() << "not ok\n";
        QTextStream out1(&nameserverFile);
        out1 << "nameserver " << defaultGatewayLineEdit->text() << "\n";
        out1 << "nameserver " << dnsServer1LineEdit->text() << "\n";
        out1 << "nameserver " << dnsServer2LineEdit->text() << "\n";
        nameserverFile.close();
    }

//    QString program("testRouter.sh");

//    QFile routerFile(program);
//    routerFile.open(QIODevice::WriteOnly | QIODevice::Text);
//    QTextStream out1(&routerFile);
//    out1 << "#/bin/sh\n";
//    out1 << "/bin/ping " << st

//    routerFile.close();
}
