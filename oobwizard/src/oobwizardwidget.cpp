#include "oobwizardwidget.h"
#include "ui_oobwizardwidget.h"

OobWizardWidget::OobWizardWidget(QWidget *parent) :
    QWidget(parent),
    ui(new Ui::OobWizardWidget)
{
    ui->setupUi(this);
}

OobWizardWidget::~OobWizardWidget()
{
    delete ui;
}
