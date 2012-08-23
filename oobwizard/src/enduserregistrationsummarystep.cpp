#include "src/enduserregistrationsummarystep.h"
#include "ui_enduserregistrationsummarystep.h"

endUserRegistrationSummaryStep::endUserRegistrationSummaryStep(QWidget *parent) :
    QWidget(parent),
    ui(new Ui::endUserRegistrationSummaryStep)
{
    ui->setupUi(this);
}

endUserRegistrationSummaryStep::~endUserRegistrationSummaryStep()
{
    delete ui;
}
