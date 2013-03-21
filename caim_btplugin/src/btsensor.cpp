#include "btsensor.h"

/**
 * @brief BtSensor::BtSensor
 * @param parent
 */
BtSensor::BtSensor(QObject* parent)
        : AbstractSensor(parent)
{
}

/**
 * @brief BtSensor::plug
 * @return
 */
bool BtSensor::plug()
{
    device = new BtDevice(this);

    emit plugged();
    return true;
}

/**
 * @brief BtSensor::serialize
 * @param buffer
 */
void BtSensor::serialize(QByteArray *buffer)
{
}

/**
 * @brief BtSensor::serialize
 * @param stream
 */
void BtSensor::serialize(QTextStream *stream)
{
}
