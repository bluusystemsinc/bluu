#include "oobwizardwidget.h"
#include "ui_oobwizardwidget.h"

#include "wizardcontext.h"

OobWizardWidget::OobWizardWidget(QWidget *parent) :
    QWidget(parent),
    m_ui(new Ui::OobWizardWidget)
{
    m_ui->setupUi(this);

    m_context = new WizardContext(m_ui, this);

    installValidators();
    connect(m_ui->userNameLineEdit, SIGNAL(textChanged(QString)),
            SLOT(validateControlStep()));
}

OobWizardWidget::~OobWizardWidget()
{
    delete m_ui;
}

void OobWizardWidget::installValidators()
{
    QRegExp rxUserName("[a-zA-Z][\\w0-9]{4,16}");

    m_ui->userNameLineEdit->setValidator(new QRegExpValidator(rxUserName,
                                                              this));
}

void OobWizardWidget::validateControlStep()
{
    QString userName = m_ui->userNameLineEdit->text();
    const QValidator *validator = m_ui->userNameLineEdit->validator();
    int pos;

    m_ui->nextButton->setEnabled(QValidator::Acceptable == validator->validate(
                                     userName, pos));
}
