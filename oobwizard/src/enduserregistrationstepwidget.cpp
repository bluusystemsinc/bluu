#include "enduserregistrationstepwidget.h"

EndUserRegistrationStepWidget::EndUserRegistrationStepWidget(QWidget *parent) :
    QWidget(parent)
{
    QRegExp rxStrings("[a-zA-Z]{3,15}");
    QRegExpValidator *validatorString = new QRegExpValidator(rxStrings, this);

    QRegExp rxNumbers("[0-9]{4,10}");
    QRegExpValidator *validatorNumbers = new QRegExpValidator(rxNumbers, this);


    setupUi(this);

    firstNameLineEdit->setValidator(validatorString);
    validateFirstName();
    middleNameLineEdit->setValidator(validatorString);
    validateMiddleName();
    lastNameLineEdit->setValidator(validatorString);
    validateLastName();
    addressLineEdit->setValidator(validatorString);
    validateAddress();
    cityLineEdit->setValidator(validatorString);
    validateCity();
    zipCodeLineEdit->setValidator(validatorNumbers);
    validateZipCode();
    emailAddressLineEdit->setValidator(validatorString);
    validateEmailAddress();
    phoneNumberLineEdit->setValidator(validatorNumbers);
    validatePhoneNumber();
    dealerIDLineEdit->setValidator(validatorNumbers);
    validateDealerId();



    connect(firstNameLineEdit, SIGNAL(textChanged(QString)), SLOT(validateFirstName()));
    connect(middleNameLineEdit, SIGNAL(textChanged(QString)), SLOT(validateMiddleName()));
    connect(lastNameLineEdit, SIGNAL(textChanged(QString)), SLOT(validateLastName()));
    connect(addressLineEdit, SIGNAL(textChanged(QString)), SLOT(validateAddress()));
    connect(cityLineEdit, SIGNAL(textChanged(QString)), SLOT(validateCity()));
    connect(zipCodeLineEdit, SIGNAL(textChanged(QString)), SLOT(validateZipCode()));
    connect(emailAddressLineEdit, SIGNAL(textChanged(QString)), SLOT(validateEmailAddress()));
    connect(phoneNumberLineEdit, SIGNAL(textChanged(QString)), SLOT(validatePhoneNumber()));
    connect(dealerIDLineEdit, SIGNAL(textChanged(QString)), SLOT(validateDealerId()));


    connect(nextButton, SIGNAL(clicked()), SIGNAL(next()));
    connect(backButton, SIGNAL(clicked()), SIGNAL(back()));
}

void EndUserRegistrationStepWidget::validateFirstName()
{
    QString string = firstNameLineEdit->text();
    const QValidator *validator = firstNameLineEdit->validator();
    int pos;
    bool value = QValidator::Acceptable == validator->validate(string, pos);

    if(value)
    {
        middleNameLabel->setEnabled(true);
        middleNameLineEdit->setEnabled(true);
    }
}
void EndUserRegistrationStepWidget::validateMiddleName()
{
    QString string = middleNameLineEdit->text();
    const QValidator *validator = middleNameLineEdit->validator();
    int pos;
    bool value = QValidator::Acceptable == validator->validate(string, pos);

    if(value)
    {
        lastNameLabel->setEnabled(true);
        lastNameLineEdit->setEnabled(true);
    }
}
void EndUserRegistrationStepWidget::validateLastName()
{
    QString string = lastNameLineEdit->text();
    const QValidator *validator = lastNameLineEdit->validator();
    int pos;
    bool value = QValidator::Acceptable == validator->validate(string, pos);

    if(value)
    {
        streetAddressLabel->setEnabled(true);
        addressLineEdit->setEnabled(true);
    }
}
void EndUserRegistrationStepWidget::validateAddress()
{
    QString string = addressLineEdit->text();
    const QValidator *validator = addressLineEdit->validator();
    int pos;
    bool value = QValidator::Acceptable == validator->validate(string, pos);

    if(value)
    {
        cityLabel->setEnabled(true);
        cityLineEdit->setEnabled(true);
    }
}
void EndUserRegistrationStepWidget::validateCity()
{
    QString string = cityLineEdit->text();
    const QValidator *validator = cityLineEdit->validator();
    int pos;
    bool value = QValidator::Acceptable == validator->validate(string, pos);

    if(value)
    {
        zipCodeLabel->setEnabled(true);
        zipCodeLineEdit->setEnabled(true);
    }
}
void EndUserRegistrationStepWidget::validateZipCode()
{
    QString string = zipCodeLineEdit->text();
    const QValidator *validator = zipCodeLineEdit->validator();
    int pos;
    bool value = QValidator::Acceptable == validator->validate(string, pos);

    if(value)
    {
        stateCountryLabel->setEnabled(value);
        countryLineEdit->setEnabled(value);
        emailAddressLabel->setEnabled(true);
        emailAddressLineEdit->setEnabled(true);
    }
}
void EndUserRegistrationStepWidget::validateEmailAddress()
{
    QString string = emailAddressLineEdit->text();
    const QValidator *validator = emailAddressLineEdit->validator();
    int pos;
    bool value = QValidator::Acceptable == validator->validate(string, pos);

    if(value)
    {
        phoneNumberLabel->setEnabled(true);
        phoneNumberLineEdit->setEnabled(true);
    }
}
void EndUserRegistrationStepWidget::validatePhoneNumber()
{
    QString string = phoneNumberLineEdit->text();
    const QValidator *validator = phoneNumberLineEdit->validator();
    int pos;
    bool value = QValidator::Acceptable == validator->validate(string, pos);

     if(value)
     {
         dealerIdLabel->setEnabled(true);
         dealerIDLineEdit->setEnabled(true);
     }
}
void EndUserRegistrationStepWidget::validateDealerId()
{
    QString string = dealerIDLineEdit->text();
    const QValidator *validator = dealerIDLineEdit->validator();
    int pos;
    bool value = QValidator::Acceptable == validator->validate(string, pos);

    if(value)
        nextButton->setEnabled(value);
}
