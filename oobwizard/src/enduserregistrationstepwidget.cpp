#include "enduserregistrationstepwidget.h"

EndUserRegistrationStepWidget::EndUserRegistrationStepWidget(QWidget *parent) :
    QWidget(parent)
{
    QRegExp rx("[a-zA-Z]{3,10}");
    QRegExpValidator *validator = new QRegExpValidator(rx, this);

    setupUi(this);

    firstNameLineEdit->setValidator(validator);
    validate();

    connect(nextButton, SIGNAL(clicked()), SIGNAL(next()));
    connect(backButton, SIGNAL(clicked()), SIGNAL(back()));
    connect(firstNameLineEdit, SIGNAL(textChanged(QString)), SLOT(validate()));

//    connect(backButton, SIGNAL(clicked()), SIGNAL(back()));
//    connect(nextButton, SIGNAL(clicked()), SIGNAL(next()));
}

void EndUserRegistrationStepWidget::validate()
{
    QString string = firstNameLineEdit->text();
    const QValidator *validator = firstNameLineEdit->validator();
    int pos;
    bool value = QValidator::Acceptable == validator->validate(string, pos);

    nextButton->setEnabled(value);
}
