#include "enduserregistrationstepwidget.h"

EndUserRegistrationStepWidget::EndUserRegistrationStepWidget(QWidget *parent) :
    QWidget(parent)
{
    QRegExp rxStrings("[a-zA-Z ]{3,15}");
    QRegExpValidator *validatorString = new QRegExpValidator(rxStrings, this);

    QRegExp phoneNumber("[0-9]{7,10}");
    QRegExpValidator *validatorPhoneNumber = new QRegExpValidator(phoneNumber, this);


    QRegExp rxEmail("^[a-zA-Z][\\w\\.-]*[a-zA-Z0-9]@[a-zA-Z0-9][\\w\\.-]*[a-zA-Z0-9]\\.[a-zA-Z][a-zA-Z\\.]*[a-zA-Z]$");
    QRegExpValidator *validatorEmail = new QRegExpValidator(rxEmail, this);

    QRegExp zipCode("[0-9]{5,7}");
    QRegExpValidator *validatorZipCode = new QRegExpValidator(zipCode, this);

    QRegExp dealerId("[0-9]{5,7}");
    QRegExpValidator *validatorDealerID = new QRegExpValidator(dealerId, this);

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
    zipCodeLineEdit->setValidator(validatorZipCode);
    validateZipCode();
    emailAddressLineEdit->setValidator(validatorEmail);
    validateEmailAddress();
    phoneNumberLineEdit->setValidator(validatorPhoneNumber);
    validatePhoneNumber();
    dealerIDLineEdit->setValidator(validatorDealerID);
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

    middleNameLabel->setEnabled(value);
    middleNameLineEdit->setEnabled(value);

}
void EndUserRegistrationStepWidget::validateMiddleName()
{
    QString string = middleNameLineEdit->text();
    const QValidator *validator = middleNameLineEdit->validator();
    int pos;
    bool value = QValidator::Acceptable == validator->validate(string, pos);

    lastNameLabel->setEnabled(value);
    lastNameLineEdit->setEnabled(value);
}
void EndUserRegistrationStepWidget::validateLastName()
{
    QString string = lastNameLineEdit->text();
    const QValidator *validator = lastNameLineEdit->validator();
    int pos;
    bool value = QValidator::Acceptable == validator->validate(string, pos);

    streetAddressLabel->setEnabled(value);
    addressLineEdit->setEnabled(value);
}
void EndUserRegistrationStepWidget::validateAddress()
{
    QString string = addressLineEdit->text();
    const QValidator *validator = addressLineEdit->validator();
    int pos;
    bool value = QValidator::Acceptable == validator->validate(string, pos);

    cityLabel->setEnabled(value);
    cityLineEdit->setEnabled(value);
}
void EndUserRegistrationStepWidget::validateCity()
{
    QString string = cityLineEdit->text();
    const QValidator *validator = cityLineEdit->validator();
    int pos;
    bool value = QValidator::Acceptable == validator->validate(string, pos);

    zipCodeLabel->setEnabled(value);
    zipCodeLineEdit->setEnabled(value);
}
void EndUserRegistrationStepWidget::validateZipCode()
{
    QString string = zipCodeLineEdit->text();
    const QValidator *validator = zipCodeLineEdit->validator();
    int pos;
    bool value = QValidator::Acceptable == validator->validate(string, pos);

    stateCountryLabel->setEnabled(value);
    countryLineEdit->setEnabled(value);
    emailAddressLabel->setEnabled(value);
    emailAddressLineEdit->setEnabled(value);
}
void EndUserRegistrationStepWidget::validateEmailAddress()
{
    QString string = emailAddressLineEdit->text();
    const QValidator *validator = emailAddressLineEdit->validator();
    int pos;
    bool value = QValidator::Acceptable == validator->validate(string, pos);

    phoneNumberLabel->setEnabled(value);
    phoneNumberLineEdit->setEnabled(value);
}
void EndUserRegistrationStepWidget::validatePhoneNumber()
{
    QString string = phoneNumberLineEdit->text();
    const QValidator *validator = phoneNumberLineEdit->validator();
    int pos;
    bool value = QValidator::Acceptable == validator->validate(string, pos);

    dealerIdLabel->setEnabled(value);
    dealerIDLineEdit->setEnabled(value);
}
void EndUserRegistrationStepWidget::validateDealerId()
{
    QString string = dealerIDLineEdit->text();
    const QValidator *validator = dealerIDLineEdit->validator();
    int pos;
    bool value = QValidator::Acceptable == validator->validate(string, pos);

    nextButton->setEnabled(value);
}
