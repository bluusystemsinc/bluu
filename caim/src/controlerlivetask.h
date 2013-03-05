#ifndef CONTROLERLIVETASK_H
#define CONTROLERLIVETASK_H

#include "task.h"
#include <QNetworkReply>

/**
 * @brief The ControlerLiveTask class
 */
class ControlerLiveTask : public Task
{
    Q_OBJECT

private:
    QString     out;

public:
    explicit ControlerLiveTask(QObject *parent = 0);
    virtual bool validateTask(const QDateTime& dateTime);
    
signals:
    void debugSignal(QString debugMessage);
    void networkSendSignal(QString* data);
    
public slots:
   virtual void processTask();
    void networkReplySlot(QNetworkReply* reply);
};

#endif // CONTROLERLIVETASK_H
