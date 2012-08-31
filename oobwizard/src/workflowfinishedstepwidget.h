#ifndef WORKFLOWFINISHEDSTEPWIDGET_H
#define WORKFLOWFINISHEDSTEPWIDGET_H

#include <QWidget>
#include <QApplication>
#include "ui_workflowFinished.h"

class WorkflowFinishedStepWidget : public QWidget, private Ui::workflowFinished
{
    Q_OBJECT
public:
    explicit WorkflowFinishedStepWidget(QWidget *parent = 0);
    
private slots:
    void finish();
};

#endif // WORKFLOWFINISHEDSTEPWIDGET_H
