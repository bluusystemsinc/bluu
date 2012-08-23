#include "enduserregistrationsummarystep.h"
#include "ui_enduserregistrationsummarystep.h"

endUserRegistrationSummaryStep::endUserRegistrationSummaryStep(QWidget *parent) :
    QWidget(parent)
{
    setupUi(this);


    connect(backButton, SIGNAL(clicked()), SIGNAL(back()));
    connect(nextButton, SIGNAL(clicked()), SIGNAL(next()));
}

endUserRegistrationSummaryStep::~endUserRegistrationSummaryStep()
{
    delete ui;
}
