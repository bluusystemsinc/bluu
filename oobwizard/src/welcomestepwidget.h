#ifndef WELCOMESTEPWIDGET_H
#define WELCOMESTEPWIDGET_H

#include <QWidget>
#include <ui_welcomeStep.h>

class WelcomeStepWidget : public QWidget, private Ui::WelcomeStepWidget
{
    Q_OBJECT
public:
    explicit WelcomeStepWidget(QWidget *parent = 0);    

signals:
    void next();
};

#endif // WELCOMESTEPWIDGET_H
