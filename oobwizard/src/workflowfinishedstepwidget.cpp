#include "workflowfinishedstepwidget.h"
#include <QFile>

WorkflowFinishedStepWidget::WorkflowFinishedStepWidget(QWidget *parent) :
    QWidget(parent)
{
    setupUi(this);

    connect(finishButton, SIGNAL(clicked()),this  , SLOT(finish()));

}
void WorkflowFinishedStepWidget::finish()
{
    QFile::remove("endUserRegistrationInfo.txt");
    QApplication::quit();
}
