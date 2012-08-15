#ifndef WIZARDCONTEXT_H
#define WIZARDCONTEXT_H

#include <QUrl>
#include <QObject>

class QStateMachine;

class WizardContext : public QObject
{
    Q_OBJECT
public:
    Q_PROPERTY(QUrl currentUrl READ currentUrl WRITE setCurrentUrl
               NOTIFY currentUrlChanged)

    explicit WizardContext(QObject *parent = 0);

    QUrl currentUrl() const;

signals:
    void currentUrlChanged();

protected slots:
    void setCurrentUrl(const QUrl &url);
    void onStateChanged();
private:
    QStateMachine *m_stateMachine;
};

#endif // WIZARDCONTEXT_H
