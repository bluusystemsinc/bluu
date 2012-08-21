#include "oobwizardwidget.h"
#include "ui_oobwizardwidget.h"

#include "wizardcontext.h"

OobWizardWidget::OobWizardWidget(QWidget *parent) :
    QWidget(parent)
{
    setupUi(this);

    m_context = new WizardContext(this, this);

    installValidators();
    connect(userNameLineEdit, SIGNAL(textChanged(QString)),
            SLOT(validateControlStep()));
}

OobWizardWidget::~OobWizardWidget()
{
}

void OobWizardWidget::installValidators()
{
    QRegExp rxUserName("[a-zA-Z][\\w0-9]{4,16}");

    userNameLineEdit->setValidator(new QRegExpValidator(rxUserName, this));
}

void OobWizardWidget::validateControlStep()
{
    QString userName = userNameLineEdit->text();
    const QValidator *validator = userNameLineEdit->validator();
    int pos;

    nextButton->setEnabled(QValidator::Acceptable == validator->validate(
                                     userName, pos));
}
