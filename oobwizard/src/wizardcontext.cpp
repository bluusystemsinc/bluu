#include "wizardcontext.h"

#define BEGIN_BRACE __PRETTY_FUNCTION__

#include <QUrl>
#include <QFile>
#include <QDebug>
#include <QTimer>
#include <QProcess>
#include <QButtonGroup>
#include <QStateMachine>

#include "ui_oobwizardwidget.h"

WizardContext::WizardContext(Ui::OobWizardWidget */*ui*/, QObject *parent) :
    QObject(parent), m_isConnected(notConnected)
{
//    QButtonGroup *systemConfigurationButtonGroup = new QButtonGroup(this);
//    QButtonGroup *connectionTypeButtonGroup = new QButtonGroup(this);

//    systemConfigurationButtonGroup->addButton(ui->networkConfigurationButton);
//    systemConfigurationButtonGroup->addButton(ui->endUserRegistrationButton);

//    connectionTypeButtonGroup->addButton(ui->wiredConnectionButton);
//    connectionTypeButtonGroup->addButton(ui->wirelessConnectionButton);

//    m_ui = ui;


//    m_stateMachine = new QStateMachine(this);

//    m_welcomeState = new QState(m_stateMachine);
//    m_welcomeState->assignProperty(ui->stackedWidget, "currentIndex", 0);
//    m_welcomeState->assignProperty(ui->backButton, "enabled", false);
//    m_welcomeState->assignProperty(ui->nextButton, "enabled", true);

//    m_controllerState = new QState(m_stateMachine);
//    m_controllerState->assignProperty(ui->stackedWidget, "currentIndex", 1);
//    m_controllerState->assignProperty(ui->backButton, "enabled", true);
//    m_controllerState->assignProperty(ui->nextButton, "enabled", false);

//    m_systemConfigurationState = new QState(m_stateMachine);
//    m_systemConfigurationState->assignProperty(ui->stackedWidget,
//                                               "currentIndex", 2);

//    m_connectionTypeState = new QState(m_stateMachine);
//    m_connectionTypeState->assignProperty(ui->stackedWidget, "currentIndex", 3);

//    m_wirelessSettingsState = new QState(m_stateMachine);
//    m_wirelessSettingsState->assignProperty(ui->stackedWidget, "currentIndex",
//                                            4);

//    m_endUserRegistrationState = new QState(m_stateMachine);
//    m_endUserRegistrationState->assignProperty(ui->stackedWidget,
//                                               "currentIndex", 7);


//    m_welcomeState->addTransition(ui->nextButton, SIGNAL(clicked()),
//                                m_controllerState);

//    m_controllerState->addTransition(ui->backButton, SIGNAL(clicked()),
//                                   m_welcomeState);
//    m_controllerState->addTransition(ui->nextButton, SIGNAL(clicked()),
//                                   m_systemConfigurationState);

//    setSystemControllerTransitions();

//    setConnectionTypeTransitions();

//    m_wirelessSettingsState->addTransition(ui->backButton, SIGNAL(clicked()),
//                                           m_connectionTypeState);

////    m_endUserRegistrationState->addTransition(this, SIGNAL(backClicked()), m_welcomeState);

//    m_stateMachine->setInitialState(m_welcomeState);
//    m_stateMachine->start();

//    ui->eulaTextEdit->setPlainText(eula());
//    emit eulaChanged();

//    connect(systemConfigurationButtonGroup, SIGNAL(buttonClicked(int)),
//            SLOT(setSystemControllerTransitions()));
//    connect(connectionTypeButtonGroup, SIGNAL(buttonClicked(int)),
//            SLOT(setConnectionTypeTransitions()));
}

QUrl WizardContext::currentUrl() const
{
    qDebug()<<__PRETTY_FUNCTION__;

    return m_currentUrl;
}

QString WizardContext::eula() const
{
    QFile file("text/eula");
    QString retval;
    if(file.open(QIODevice::ReadOnly))
    {
        QTextStream stream(&file);

        retval = stream.readAll();
    }
    else
        qFatal("eula file not found");

    return retval;
}

bool WizardContext::isBackEnabled() const
{
    return m_isBackEnabled;
}

bool WizardContext::isNextEnabled() const
{
    return m_isNextEnabled;
}

bool WizardContext::isConnectionTestRunning() const
{
    return m_isConnectionTestRunning;
}

void WizardContext::setBackEnabled(bool value)
{
    if(m_isBackEnabled != value)
    {
        m_isBackEnabled = value;
        emit isBackEnabledChanged();
    }
}

void WizardContext::setNextEnabled(bool value)
{
    if(m_isNextEnabled != value)
    {
        m_isNextEnabled = value;
        emit isNextEnabledChanged();
    }
}

void WizardContext::runConnectionTest(QString hostname)
{
     QString program = "../scripts/connectionTest.sh";
     QStringList arg;

     arg << hostname;
     QProcess *myProcess = new QProcess();
     connect(myProcess, SIGNAL(finished(int, QProcess::ExitStatus)), this,
             SLOT(updateExit(int, QProcess::ExitStatus)));
     myProcess->start(program,arg);
}

void WizardContext::setCurrentUrl(const QUrl &url)
{
    qDebug()<<__PRETTY_FUNCTION__<<url;

    if(m_currentUrl != url)
    {
        m_currentUrl = url;
        emit currentUrlChanged();
    }
}

void WizardContext::setSystemControllerTransitions()
{
//    foreach(QAbstractTransition *transition,
//            m_systemConfigurationState->transitions())
//    {
//        m_systemConfigurationState->removeTransition(transition);
//    }

//    m_systemConfigurationState->addTransition(m_ui->backButton,
//                                              SIGNAL(clicked()),
//                                              m_controllerState);

//    if(m_ui->networkConfigurationButton->isChecked())
//    {
//        m_systemConfigurationState->addTransition(m_ui->nextButton,
//                                                  SIGNAL(clicked()),
//                                                  m_connectionTypeState);
//        m_connectionTypeState->addTransition(m_ui->backButton,
//                                             SIGNAL(clicked()),
//                                             m_systemConfigurationState);
//    }
//    else if(m_ui->endUserRegistrationButton->isChecked())
//    {
//        m_systemConfigurationState->addTransition(m_ui->nextButton,
//                                                  SIGNAL(clicked()),
//                                                  m_endUserRegistrationState);
//        m_connectionTypeState->addTransition(m_ui->backButton,
//                                             SIGNAL(clicked()),
//                                             m_systemConfigurationState);
//    }
}

void WizardContext::setConnectionTypeTransitions()
{
}

void WizardContext::updateExit(int exitCode,
                               QProcess::ExitStatus /*exitStatus*/)
{
    qDebug() << "exitCode:" << exitCode << endl;
    if(exitCode)
        this->m_isConnected = connectionTested;
    else
        this->m_isConnected = connecitonError;
}
