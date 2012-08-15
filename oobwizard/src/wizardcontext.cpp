#include "wizardcontext.h"

#include <QUrl>
#include <QDebug>
#include <QTimer>
#include <QStateMachine>

WizardContext::WizardContext(QObject *parent) :
    QObject(parent)
{
    m_stateMachine = new QStateMachine(this);

    QState *welcomeState = new QState;

    connect(m_stateMachine, SIGNAL(entered()),
            SLOT(onStateChanged()));
    welcomeState->assignProperty(this, "url", WELCOMESTEP_QML);

    m_stateMachine->addState(welcomeState);
    m_stateMachine->setInitialState(welcomeState);
    m_stateMachine->start();
}

QUrl WizardContext::currentUrl() const
{
    QSet<QAbstractState *> configuration = m_stateMachine->configuration();
    QSet<QAbstractState*>::ConstIterator it;
    QAbstractState *state;

    qDebug()<<configuration.size();
    Q_ASSERT(configuration.size() <= 1);
    it = configuration.constBegin();
    state = *it;
    return state->property("url").toUrl();
}

void WizardContext::onStateChanged()
{
    qDebug()<<__PRETTY_FUNCTION__;
}

void WizardContext::setCurrentUrl(const QUrl &url)
{
    qDebug()<<__PRETTY_FUNCTION__;
}
