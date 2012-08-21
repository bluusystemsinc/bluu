#ifndef CONTROLLERSTEPWIDGET_H
#define CONTROLLERSTEPWIDGET_H

#include <QWidget>
#include <ui_controllerStep.h>

class ControllerStepWidget : public QWidget, private Ui::ControllerStepWidget
{
    Q_OBJECT
public:
    explicit ControllerStepWidget(QWidget *parent = 0);
    
signals:
    void next();
    void back();

protected slots:
    void validate();
};

#endif // CONTROLLERSTEPWIDGET_H
