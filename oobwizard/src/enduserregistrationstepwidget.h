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
    bool check(bool value,int inputLineNumber);

    enum {
        firstName = 1,
        middleName,
        lastName,
        address,
        city,
        zipCode,
        emailAddress,
        phoneNumber,
        dealerId
    };
    int allValidate;
signals:
    void back();
    void next();
protected slots:
    void validateFirstName();
    void validateMiddleName();
    void validateLastName();
    void validateAddress();
    void validateCity();
    void validateZipCode();
    void validateEmailAddress();
    void validatePhoneNumber();
    void validateDealerId();

};

#endif // ENDUSERREGISTRATIONSTEPWIDGET_H
