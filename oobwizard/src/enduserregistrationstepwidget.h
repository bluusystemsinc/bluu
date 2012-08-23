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

protected:
    Q_INVOKABLE bool validateFirstName();
    Q_INVOKABLE bool validateMiddleName();
    Q_INVOKABLE bool validateLastName();
    Q_INVOKABLE bool validateAddress();
    Q_INVOKABLE bool validateCity();
    Q_INVOKABLE bool validateZipCode();
    Q_INVOKABLE bool validateEmailAddress();
    Q_INVOKABLE bool validatePhoneNumber();
    Q_INVOKABLE bool validateDealerId();

protected slots:
    void validate();

};

#endif // ENDUSERREGISTRATIONSTEPWIDGET_H
