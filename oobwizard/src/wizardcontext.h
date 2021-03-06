#ifndef WIZARDCONTEXT_H
#define WIZARDCONTEXT_H

#include <QUrl>
#include <QObject>
#include <QProcess>

class QState;
class QStateMachine;
class QSignalTransition;

namespace Ui {
class OobWizardWidget;
}

class WizardContext : public QObject
{
    Q_OBJECT
public:
    enum networkStates {
        notConnected,
        connectionNotTested,
        connectionTested,
        connectionOk,
        connecitonError
    };

    Q_PROPERTY(QUrl currentUrl READ currentUrl WRITE setCurrentUrl
               NOTIFY currentUrlChanged)
    Q_PROPERTY(QString eula READ eula NOTIFY eulaChanged)
    Q_PROPERTY(bool isBackEnabled READ isBackEnabled WRITE setBackEnabled
               NOTIFY isBackEnabledChanged)
    Q_PROPERTY(bool isNextEnabled READ isNextEnabled WRITE setNextEnabled
               NOTIFY isNextEnabledChanged)
    Q_PROPERTY(bool isConnectionTestRunning READ isConnectionTestRunning
               NOTIFY isConnectionTestRunningChanged)

    explicit WizardContext(Ui::OobWizardWidget *ui, QObject *parent = 0);

    QUrl currentUrl() const;
    QString eula() const;
    bool isBackEnabled() const;
    bool isNextEnabled() const;
    bool isConnectionTestRunning() const;

public slots:
    void setBackEnabled(bool value);
    void setNextEnabled(bool value);
    void runConnectionTest(QString hostname);
    void updateExit(int exitCode, QProcess::ExitStatus exitStatus);

signals:
    void backClicked();
    void nextClicked();
    void currentUrlChanged();
    void eulaChanged();
    void isBackEnabledChanged();
    void isNextEnabledChanged();
    void isConnectionTestRunningChanged();

protected slots:
    void setCurrentUrl(const QUrl &);
    void setSystemControllerTransitions();
    void setConnectionTypeTransitions();

private:
    QStateMachine *m_stateMachine;
    QUrl m_currentUrl;
    bool m_isBackEnabled;
    bool m_isNextEnabled;
    bool m_isConnectionTestRunning;
    networkStates m_isConnected;
    Ui::OobWizardWidget *m_ui;
    QState *m_welcomeState, *m_endUserRegistrationState, *m_controllerState,
            *m_systemConfigurationState, *m_connectionTypeState,
            *m_wirelessSettingsState;
};

#endif // WIZARDCONTEXT_H
