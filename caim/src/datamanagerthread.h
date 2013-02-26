#ifndef DATAMANAGERTHREAD_H
#define DATAMANAGERTHREAD_H

#include <QThread>
#include <QNetworkReply>
#include <QTimer>
#include <QStringList>

/**
 * @brief The DataManagerThread class
 */
class DataManagerThread : public QThread
{
    Q_OBJECT

private:
    QStringList::iterator it;

protected:
    QTimer*     timerPackets;
    QTimer*     timerDatabase;

protected:
    virtual void run();

public:
    explicit DataManagerThread(QObject *parent = 0);
    
signals:
    void sendSignal();
    void databaseStorePacketSignal(QString* data);
    void databaseSendPacketSignal();
    void networkSendSignal(QString data);
    void debugSignal(QString debugMessage);
    
public slots:
    void timeOutSlot();
    void sendSlot();
    void sendDatabaseSlot();
    void networkReplySlot(QNetworkReply* reply);
};

#endif // DATAMANAGERTHREAD_H
