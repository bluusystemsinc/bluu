#include "dataparser.h"
#include "debug.h"

/**
 * @brief DataParser::DataParser TODO
 * @param parent
 */
DataParser::DataParser(QObject *parent) :
    QObject(parent)
{
    log();

    data = NULL;
}

/**
 * @brief DataParser::parseData TODO
 * @param buffer
 */
void DataParser::parseData(QByteArray* buffer)
{
    log();

    if(NULL != buffer)
    {
        data = buffer;

        if(true == checkCRC())
        {
            if(true == checkMagic())
            {
                if(true == checkSource())
                {
                    if(true == checkDevice())
                    {
                        checkStatus();
                        checkSerial();
                        packet.generateJson();
                    }
                    else
                    {
                        log() << "Unknown device";
                    }
                }
                else
                {
                    log() << "Source device unknow";
                }
            }
            else
            {
                log() << "Magic number is wrong";
            }
        }
        else
        {
            log() << "CRC is wrong, cannot process data";
        }
    }
    else
    {
        log() << "Data buffer is empty";
    }
}

/**
 * @brief DataParser::checkCRC TODO
 * @return
 */
bool DataParser::checkCRC()
{
    // TODO retrieve CRC algorithm to check data integrity
    return true;
}

/**
 * @brief DataParser::checkMagic TODO
 * @return
 */
bool DataParser::checkMagic()
{
    char            x = data->at(0);
    unsigned char   y = data->at(0);

    return MAGIC_NUMBER == static_cast<unsigned char>(data->at(0)) ? true : false;
}

/**
 * @brief DataParser::checkSource TODO
 * @return
 */
bool DataParser::checkSource()
{
    bool    result = false;

    switch(static_cast<unsigned char>(data->at(1)))
    {
    case SOURCE_RECEIVER:
    case SOURCE_SENSOR:
        result = true;
        packet.setSource(data->at(1));
        break;

    default:
        break;
    }

    return result;
}

/**
 * @brief DataParser::checkDevice TODO
 * @return
 */
bool DataParser::checkDevice()
{
    bool            result = false;
    unsigned char   id = static_cast<unsigned char>(data->at(3)) >> 4;

    switch(id)
    {
    case DEV_RECEIVER:
    case DEV_DWV1:
    case DEV_DWV2:
    case DEV_DWV3:
    case DEV_SHOCK:
    case DEV_TILT:
    case DEV_FLOOD:
    case DEV_CO:
    case DEV_SMOKE:
    case DEV_PIR:
    case DEV_GLASS:
    case DEV_TAKEOVER:
    case DEV_KEY:
    case DEV_PANIC:
        packet.setId(id);
        result = true;
        break;
    }

    return result;
}

/**
 * @brief DataParser::checkStatus TODO
 */
void DataParser::checkStatus()
{
    packet.setStatus(data->at(2));
}

/**
 * @brief DataParser::checkSerial TODO
 */
void DataParser::checkSerial()
{
    char    serial[3];

    serial[0] = data->at(4);
    serial[1] = data->at(5);
    serial[2] = data->at(6);
}
