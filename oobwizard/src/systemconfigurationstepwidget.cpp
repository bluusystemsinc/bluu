#include "systemconfigurationstepwidget.h"

SystemConfigurationStepWidget::SystemConfigurationStepWidget(QWidget *parent) :
    QWidget(parent)
{

    setupUi(this);

    m_buttonGroup = new QButtonGroup(this);
    m_buttonGroup->addButton(networkConfigurationButton, NetworkConfiguration);
    m_buttonGroup->addButton(endUserRegistrationButton, EndUserRegistration);

    connect(backButton, SIGNAL(clicked()), SIGNAL(back()));
}


void SystemConfigurationStepWidget::on_nextButton_clicked()
{
    switch(m_buttonGroup->checkedId())
    {
    case NetworkConfiguration:
        emit networkConfiguration();
        break;
    case EndUserRegistration:
        emit endUserRegistration();
        break;
    default:
        qFatal("Unknown button");
    }
}
