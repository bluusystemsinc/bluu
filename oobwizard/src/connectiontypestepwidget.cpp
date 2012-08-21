#include "connectiontypestepwidget.h"

ConnectionTypeStepWidget::ConnectionTypeStepWidget(QWidget *parent) :
    QWidget(parent)
{
    setupUi(this);

    m_buttonGroup = new QButtonGroup(this);
    m_buttonGroup->addButton(wiredConnectionButton, WiredConnection);
    m_buttonGroup->addButton(wirelessConnectionButton, WirelessConnection);

    connect(backButton, SIGNAL(clicked()), SIGNAL(back()));
}


void ConnectionTypeStepWidget::on_nextButton_clicked()
{
    switch(m_buttonGroup->checkedId())
    {
    case WiredConnection:
        emit wiredConnection();
        break;
    case WirelessConnection:
        emit wirelessConnection();
        break;
    default:
        qFatal("Unknown button");
    }
}
