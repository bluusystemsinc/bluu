#include "datamanager.h"
#include "dataparser.h"
#include "debug.h"
#include "webrequest.h"

/**
 * @brief DataManager::DataManager TODO
 * @param parent
 */
DataManager::DataManager(QObject *parent) :
    QObject(parent)
{
}

/**
 * @brief DataManager::processData TODO
 * @param data
 */
void DataManager::processData(QByteArray* data)
{
    log();

    if(NULL != data)
    {
        int     count = data->count();

        if(0 == count % 9)
        {
            if(9 == count)
            {
                CBluuDataParser::Instance()->parseData(data);
            }
            else
            {
                for(int i = 0; i < count % 9; i++)
                {
                    QByteArray  tmp = data->mid(i * 9, 9);

                    CBluuDataParser::Instance()->parseData(&tmp);
                }
            }
        }
        else
        {
            log() << "Some data are missing";
        }
    }
}

/**
 * @brief DataManager::packedReadySlot TODO
 */
void DataManager::packedReadySlot(QByteArray json)
{
    CBluuWebRequest::Instance()->sendDataToServer(json);
}
