#include "wizardcontext.h"

#define BEGIN_BRACE __PRETTY_FUNCTION__

#include <QUrl>
#include <QFile>
#include <QDebug>
#include <QTimer>
#include <QStateMachine>
#include <QProcess>

#include "ui_oobwizardwidget.h"

WizardContext::WizardContext(Ui::OobWizardWidget *ui, QObject *parent) :
    QObject(parent), m_isConnected(notConnected)
{
    m_ui = ui;

    m_stateMachine = new QStateMachine(this);

    QState *welcomeState, *userDataState, *controllerState;

    welcomeState = new QState(m_stateMachine);
    welcomeState->assignProperty(ui->stackedWidget, "currentIndex", 0);
    welcomeState->assignProperty(ui->backButton, "enabled", false);
    welcomeState->assignProperty(ui->nextButton, "enabled", true);

    controllerState = new QState(m_stateMachine);
    controllerState->assignProperty(ui->stackedWidget, "currentIndex", 1);
    controllerState->assignProperty(ui->backButton, "enabled", true);
    controllerState->assignProperty(ui->nextButton, "enabled", false);

    userDataState = new QState(m_stateMachine);
    userDataState->assignProperty(ui->stackedWidget, "currentIndex", 7);

    welcomeState->addTransition(ui->nextButton, SIGNAL(clicked()),
                                controllerState);

    controllerState->addTransition(ui->backButton, SIGNAL(clicked()),
                                   welcomeState);

    userDataState->addTransition(this, SIGNAL(backClicked()), welcomeState);

    m_stateMachine->setInitialState(welcomeState);
    m_stateMachine->start();

    ui->eulaTextEdit->setPlainText(eula());
    emit eulaChanged();
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
     connect(myProcess, SIGNAL(finished(int, QProcess::ExitStatus)), this, SLOT(updateExit(int, QProcess::ExitStatus)));
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
void WizardContext::updateExit(int exitCode, QProcess::ExitStatus /*exitStatus*/)
{
    qDebug() << "exitCode:" << exitCode << endl;
    if(exitCode)
        this->m_isConnected = connectionTested;
    else
        this->m_isConnected = connecitonError;
}
