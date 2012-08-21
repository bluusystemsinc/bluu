#include "controllerstepwidget.h"

ControllerStepWidget::ControllerStepWidget(QWidget *parent) :
    QWidget(parent)
{
    QRegExp rx("[a-zA-Z][\\w0-9]{4,16}");
    QRegExpValidator *validator = new QRegExpValidator(rx, this);

    setupUi(this);

    userNameLineEdit->setValidator(validator);
    validate();

    connect(nextButton, SIGNAL(clicked()), SIGNAL(next()));
    connect(backButton, SIGNAL(clicked()), SIGNAL(back()));
    connect(userNameLineEdit, SIGNAL(textChanged(QString)), SLOT(validate()));
}


void ControllerStepWidget::validate()
{
    QString string = userNameLineEdit->text();
    const QValidator *validator = userNameLineEdit->validator();
    int pos;
    bool value = QValidator::Acceptable == validator->validate(string, pos);

    nextButton->setEnabled(value);
}
