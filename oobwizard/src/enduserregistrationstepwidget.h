#ifndef ENDUSERREGISTRATIONSTEPWIDGET_H
#define ENDUSERREGISTRATIONSTEPWIDGET_H

#include <QWidget>
#include <ui_endUserRegistrationStep.h>

class EndUserRegistrationStepWidget : public QWidget,
        private Ui::EndUserRegistrationStepWidget
{
    Q_OBJECT
public:
    explicit EndUserRegistrationStepWidget(QWidget *parent = 0);
    
signals:
    void back();
    void next();
protected slots:
    void validate();
};

#endif // ENDUSERREGISTRATIONSTEPWIDGET_H
