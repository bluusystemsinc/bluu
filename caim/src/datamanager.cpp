#include "datamanager.h"
#include "dataparser.h"
#include "debug.h"

DataManager::DataManager(QObject *parent) :
    QObject(parent)
{
}

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
