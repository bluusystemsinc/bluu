#include "enduserregistrationstepwidget.h"

#include <QDebug>
#include <QMetaMethod>

EndUserRegistrationStepWidget::EndUserRegistrationStepWidget(QWidget *parent) :
    QWidget(parent)
{
//    QRegExp rxStrings("[a-zA-Z ]{3,15}");
//    QRegExpValidator *validatorString = new QRegExpValidator(rxStrings, this);

//    QRegExp phoneNumber("[0-9]{7,10}");
//    QRegExpValidator *validatorPhoneNumber = new QRegExpValidator(phoneNumber, this);


//    QRegExp rxEmail("^[a-zA-Z][\\w\\.-]*[a-zA-Z0-9]@[a-zA-Z0-9][\\w\\.-]*[a-zA-Z0-9]\\.[a-zA-Z][a-zA-Z\\.]*[a-zA-Z]$");
//    QRegExpValidator *validatorEmail = new QRegExpValidator(rxEmail, this);

//    QRegExp zipCode("[0-9]{5,7}");
//    QRegExpValidator *validatorZipCode = new QRegExpValidator(zipCode, this);

//    QRegExp dealerId("[0-9]{5,7}");
//    QRegExpValidator *validatorDealerID = new QRegExpValidator(dealerId, this);

//    setupUi(this);

//    firstNameLineEdit->setValidator(validatorString);
//    middleNameLineEdit->setValidator(validatorString);
//    lastNameLineEdit->setValidator(validatorString);
//    addressLineEdit->setValidator(validatorString);
//    cityLineEdit->setValidator(validatorString);
//    zipCodeLineEdit->setValidator(validatorZipCode);
//    emailAddressLineEdit->setValidator(validatorEmail);
//    phoneNumberLineEdit->setValidator(validatorPhoneNumber);
//    dealerIDLineEdit->setValidator(validatorDealerID);
//    validate();

//    connect(firstNameLineEdit, SIGNAL(textChanged(QString)), SLOT(validate()));
//    connect(middleNameLineEdit, SIGNAL(textChanged(QString)), SLOT(validate()));
//    connect(lastNameLineEdit, SIGNAL(textChanged(QString)), SLOT(validate()));
//    connect(addressLineEdit, SIGNAL(textChanged(QString)), SLOT(validate()));
//    connect(cityLineEdit, SIGNAL(textChanged(QString)), SLOT(validate()));
//    connect(zipCodeLineEdit, SIGNAL(textChanged(QString)), SLOT(validate()));
//    connect(emailAddressLineEdit, SIGNAL(textChanged(QString)),
//            SLOT(validate()));
//    connect(phoneNumberLineEdit, SIGNAL(textChanged(QString)),
//            SLOT(validate()));
//    connect(dealerIDLineEdit, SIGNAL(textChanged(QString)), SLOT(validate()));


//    connect(nextButton, SIGNAL(clicked()), SIGNAL(next()));
//    connect(backButton, SIGNAL(clicked()), SIGNAL(back()));
//    connect(nextButton, SIGNAL(clicked()), this, SIGNAL(trt()));
}

 EndUserRegistrationStepWidget::EndUserRegistrationStepWidget(
         endUserRegistrationSummaryStep *endUserRegistrationSummaryStepPtr,
         QWidget *parent)
     : QWidget(parent)
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
     middleNameLineEdit->setValidator(validatorString);
     lastNameLineEdit->setValidator(validatorString);
     addressLineEdit->setValidator(validatorString);
     cityLineEdit->setValidator(validatorString);
     zipCodeLineEdit->setValidator(validatorZipCode);
     emailAddressLineEdit->setValidator(validatorEmail);
     phoneNumberLineEdit->setValidator(validatorPhoneNumber);
     dealerIDLineEdit->setValidator(validatorDealerID);
     validate();

     connect(firstNameLineEdit, SIGNAL(textChanged(QString)), SLOT(validate()));
     connect(middleNameLineEdit, SIGNAL(textChanged(QString)), SLOT(validate()));
     connect(lastNameLineEdit, SIGNAL(textChanged(QString)), SLOT(validate()));
     connect(addressLineEdit, SIGNAL(textChanged(QString)), SLOT(validate()));
     connect(cityLineEdit, SIGNAL(textChanged(QString)), SLOT(validate()));
     connect(zipCodeLineEdit, SIGNAL(textChanged(QString)), SLOT(validate()));
     connect(emailAddressLineEdit, SIGNAL(textChanged(QString)),
             SLOT(validate()));
     connect(phoneNumberLineEdit, SIGNAL(textChanged(QString)),
             SLOT(validate()));
     connect(dealerIDLineEdit, SIGNAL(textChanged(QString)), SLOT(validate()));


     connect(nextButton, SIGNAL(clicked()), SIGNAL(next()));
     connect(backButton, SIGNAL(clicked()), SIGNAL(back()));
     connect(nextButton, SIGNAL(clicked()), this, SLOT(trt()));

     m_endUserRegistrationSummaryStepPtr = endUserRegistrationSummaryStepPtr;
 }

void EndUserRegistrationStepWidget::trt()
{
    m_endUserRegistrationSummaryStepPtr->endFirstNameLabel->setText(firstNameLineEdit->text());
    m_endUserRegistrationSummaryStepPtr->endMiddleInitialLabel->setText(middleNameLineEdit->text());
    m_endUserRegistrationSummaryStepPtr->endLastNameLabel->setText(lastNameLineEdit->text());
    m_endUserRegistrationSummaryStepPtr->EndSiteStreetAddressLabel->setText(addressLineEdit->text());
    m_endUserRegistrationSummaryStepPtr->endSiteCityLabel->setText(cityLineEdit->text());
    m_endUserRegistrationSummaryStepPtr->endZIPCodeLabel->setText(zipCodeLineEdit->text());
    m_endUserRegistrationSummaryStepPtr->endSiteCountryLabel->setText(countryLineEdit->currentText());
    m_endUserRegistrationSummaryStepPtr->endUserEmailAddressLabel->setText(emailAddressLineEdit->text());
    m_endUserRegistrationSummaryStepPtr->endUserPhoneNumberLabel->setText(phoneNumberLineEdit->text());
    m_endUserRegistrationSummaryStepPtr->endDealerIDLabel->setText(dealerIDLineEdit->text());
}

bool EndUserRegistrationStepWidget::validateFirstName()
{
    QString string = firstNameLineEdit->text();
    const QValidator *validator = firstNameLineEdit->validator();
    int pos;

    return QValidator::Acceptable == validator->validate(string, pos);
}

bool EndUserRegistrationStepWidget::validateMiddleName()
{
    QString string = middleNameLineEdit->text();
    const QValidator *validator = middleNameLineEdit->validator();
    int pos;

    return QValidator::Acceptable == validator->validate(string, pos);
}

bool EndUserRegistrationStepWidget::validateLastName()
{
    QString string = lastNameLineEdit->text();
    const QValidator *validator = lastNameLineEdit->validator();
    int pos;

    return QValidator::Acceptable == validator->validate(string, pos);
}

bool EndUserRegistrationStepWidget::validateAddress()
{
    QString string = addressLineEdit->text();
    const QValidator *validator = addressLineEdit->validator();
    int pos;

    return QValidator::Acceptable == validator->validate(string, pos);
}

bool EndUserRegistrationStepWidget::validateCity()
{
    QString string = cityLineEdit->text();
    const QValidator *validator = cityLineEdit->validator();
    int pos;

    return QValidator::Acceptable == validator->validate(string, pos);
}

bool EndUserRegistrationStepWidget::validateZipCode()
{
    QString string = zipCodeLineEdit->text();
    const QValidator *validator = zipCodeLineEdit->validator();
    int pos;

    return QValidator::Acceptable == validator->validate(string, pos);
}

bool EndUserRegistrationStepWidget::validateEmailAddress()
{
    QString string = emailAddressLineEdit->text();
    const QValidator *validator = emailAddressLineEdit->validator();
    int pos;

    return QValidator::Acceptable == validator->validate(string, pos);
}

bool EndUserRegistrationStepWidget::validatePhoneNumber()
{
    QString string = phoneNumberLineEdit->text();
    const QValidator *validator = phoneNumberLineEdit->validator();
    int pos;

    return QValidator::Acceptable == validator->validate(string, pos);
}

bool EndUserRegistrationStepWidget::validateDealerId()
{
    QString string = dealerIDLineEdit->text();
    const QValidator *validator = dealerIDLineEdit->validator();
    int pos;

    return QValidator::Acceptable == validator->validate(string, pos);
}

void EndUserRegistrationStepWidget::validate()
{
    bool value = true;

    for(int i = 0; i < staticMetaObject.methodCount() && value; i++)
    {
        QMetaMethod currMethod = staticMetaObject.method(i);
        QString signature(currMethod.signature());

        if(signature.startsWith("validate")
                && !signature.endsWith("validate()"))
        {
            currMethod.invoke(this, Q_RETURN_ARG(bool, value));
        }
    }

    nextButton->setEnabled(value);
}
