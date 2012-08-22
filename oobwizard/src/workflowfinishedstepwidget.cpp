#include "workflowfinishedstepwidget.h"


WorkflowFinishedStepWidget::WorkflowFinishedStepWidget(QWidget *parent) :
    QWidget(parent)
{
    setupUi(this);

    connect(finishButton, SIGNAL(clicked()),this  , SLOT(trt()));

}
void WorkflowFinishedStepWidget::trt()
{
    QApplication::quit();
}
