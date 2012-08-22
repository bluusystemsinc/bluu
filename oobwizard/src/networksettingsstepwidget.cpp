#include "networksettingsstepwidget.h"

NetworkSettingsStepWidget::NetworkSettingsStepWidget(QWidget *parent) :
    QWidget(parent)
{
    setupUi(this);

    connect(backButton, SIGNAL(clicked()), SIGNAL(back()));
    connect(nextButton, SIGNAL(clicked()), SIGNAL(next()));
    connect(wiredDHCPRadioBtn, SIGNAL(clicked()), SLOT(disableStaticConf()));
    connect(wiredStaticRadioBtn, SIGNAL(clicked()), SLOT(enableStaticConf()));
    connect(dnsYesRadioBtn, SIGNAL(clicked()), SLOT(enableDNS()));
    connect(dnsNoRadioBtn, SIGNAL(clicked()), SLOT(disableDNS()));
}

void NetworkSettingsStepWidget::disableStaticConf()
{
    staticIpAddrlineEdit->setEnabled(false);
    subnetMaskLineEdit->setEnabled(false);
    defaultGatewayLineEdit->setEnabled(false);
    DNSgroupBox->setEnabled(false);
    ipAddressLabel->setEnabled(false);
    subnetMaskLabel->setEnabled(false);
    defGatewayLabel->setEnabled(false);
}
void NetworkSettingsStepWidget::enableStaticConf()
{
    staticIpAddrlineEdit->setEnabled(true);
    subnetMaskLineEdit->setEnabled(true);
    defaultGatewayLineEdit->setEnabled(true);
    DNSgroupBox->setEnabled(true);
    ipAddressLabel->setEnabled(true);
    subnetMaskLabel->setEnabled(true);
    defGatewayLabel->setEnabled(true);
}
void NetworkSettingsStepWidget::disableDNS()
{
    dnsServer1Label->setEnabled(false);
    dnsServer1LineEdit->setEnabled(false);
    dnsServer2Label->setEnabled(false);
    dnsServer2LineEdit->setEnabled(false);
}

void NetworkSettingsStepWidget::enableDNS()
{
    dnsServer1Label->setEnabled(true);
    dnsServer1LineEdit->setEnabled(true);
    dnsServer2Label->setEnabled(true);
    dnsServer2LineEdit->setEnabled(true);
}
