#ifndef WIZARDCONTEXT_H
#define WIZARDCONTEXT_H

#include <QUrl>
#include <QObject>

class QStateMachine;

class WizardContext : public QObject
{
    Q_OBJECT
public:
    enum networkStates {
        ConnectionNotTested,
        ConnectionTested,
        ConnectionOk,
        ConnecitonError
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

    explicit WizardContext(QObject *parent = 0);

    QUrl currentUrl() const;
    QString eula() const;
    bool isBackEnabled() const;
    bool isNextEnabled() const;
    bool isConnectionTestRunning() const;

public slots:
    void setBackEnabled(bool value);
    void setNextEnabled(bool value);
    void runConnectionTest(QString hostname);
    void updateExit();

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

private:
    QStateMachine *m_stateMachine;
    QUrl m_currentUrl;
    bool m_isBackEnabled;
    bool m_isNextEnabled;
    bool m_isConnectionTestRunning;
    networkStates m_isConnected;

};

#endif // WIZARDCONTEXT_H
