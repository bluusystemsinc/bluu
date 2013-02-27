#ifndef PACKETSENDTASK_H
#define PACKETSENDTASK_H

#include "task.h"
#include <QNetworkReply>
#include <QStringList>

/**
 * @brief The PacketSendTask class
 */
class PacketSendTask : public Task
{
    Q_OBJECT

private:
    QStringList::iterator it;

public:
    explicit PacketSendTask(QObject *parent = 0);
    virtual bool validateTask(const QDateTime& dateTime);
    void setSpan(const QTime& tm);
    
signals:
    void databaseStorePacketSignal(QString* data);
    void debugSignal(QString debugMessage);
    void networkSendSignal(QString* data);
    void sendSignal();
    
public slots:
    virtual void processTask();
    void networkReplySlot(QNetworkReply* reply);
    void databasePacketStoredSlot();
    void sendSlot();
};

#endif // PACKETSENDTASK_H
