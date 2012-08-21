#include "networksettingsstepwidget.h"

NetworkSettingsStepWidget::NetworkSettingsStepWidget(QWidget *parent) :
    QWidget(parent)
{
    setupUi(this);

    connect(backButton, SIGNAL(clicked()), SIGNAL(back()));
    connect(nextButton, SIGNAL(clicked()), SIGNAL(next()));
}
