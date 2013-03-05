#include "controlerlivetask.h"
#include "debug.h"
#include "debugger.h"
#include "serializer.h"
#include "settingsmanager.h"
#include "webrequest.h"

/**
 * @brief ControlerLiveTask::ControlerLiveTask
 * @param parent
 */
ControlerLiveTask::ControlerLiveTask(QObject *parent)
                 : Task(parent)
{
    connect(this, SIGNAL(debugSignal(QString)), CBluuDebugger::Instance(), SLOT(debugSlot(QString)));
    connect(this, SIGNAL(networkSendSignal(QString*)), CBluuWebRequest::Instance(), SLOT(sendDataToServer(QString*)));
    connect(CBluuWebRequest::Instance(), SIGNAL(networkReplyControlerSignal(QNetworkReply*)), this, SLOT(networkReplySlot(QNetworkReply*)));
    type = taskRepeat;
}

/**
 * @brief ControlerLiveTask::validateTask
 * @param dateTime
 * @return
 */
bool ControlerLiveTask::validateTask(const QDateTime &dateTime)
{
    if(false == busy)
    {
        if(false == initial)
        {
            // debugMessageThread(QString("%1").arg(previousDateTime.secsTo(dateTime)));

            if(60 <= previousDateTime.secsTo(dateTime))
            {
                debugMessageThread("Task validated");
                valid = true;
                previousDateTime = dateTime;
            }
            else
            {
                // debugMessageThread("Task invalidated");
                valid = false;
            }
        }
        else
        {
            initial = false;
            valid = true;
            previousDateTime = dateTime;
        }
    }

    return valid;
}

/**
 * @brief ControlerLiveTask::processTask
 */
void ControlerLiveTask::processTask()
{
    debugMessageThread("");

    QJson::Serializer   serializer;
    QVariantMap         map;

    map.insert("timestamp", previousDateTime.toString("yyyy-MM-dd hh:mm:ss"));
    map.insert("mac", CBluuSettingsManager::Instance()->getSettings()->value("mac"));
    serializer.setIndentMode(QJson::IndentFull);
    out = QString(serializer.serialize(map));
    emit networkSendSignal(&out);
    debugMessageThread(out);
}

/**
 * @brief ControlerLiveTask::networkReplySlot
 * @param reply
 */
void ControlerLiveTask::networkReplySlot(QNetworkReply* reply)
{
    if(QNetworkReply::NoError == reply->error())
    {
        debugMessageThread("Packet send OK");
    }
    else
    {
        debugMessageThread("Packed send FAIL");
    }

    busy = false;
    valid = false;
}
