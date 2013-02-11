#include "datapacket.h"
#include "parser.h"
#include "serializer.h"
#include "debug.h"
#include <QVariantList>
#include <QVariantMap>

static QMap<quint8, QString> devicesMap()
{
    QMap<quint8, QString>   map;

    map.insert(DEV_RECEIVER, "receiver");
    map.insert(DEV_DWV1, "dw1");
    map.insert(DEV_DWV2, "dw2");
    map.insert(DEV_DWV3, "dw3");
    map.insert(DEV_SHOCK, "shock");
    map.insert(DEV_TILT, "tilt");
    map.insert(DEV_FLOOD, "flood");
    map.insert(DEV_CO, "co");
    map.insert(DEV_SMOKE, "smoke");
    map.insert(DEV_PIR, "pir");
    map.insert(DEV_GLASS, "glass");
    map.insert(DEV_TAKEOVER, "takeover");
    map.insert(DEV_KEY, "key");
    map.insert(DEV_PANIC, "panic");

    return map;
}

static const QMap<quint8, QString> devices = devicesMap();

/**
 * @brief DataPacket::DataPacket TDOO
 * @param parent
 */
DataPacket::DataPacket(QObject *parent) :
    QObject(parent)
{
    log();
}

/**
 * @brief DataPacket::setSource TODO
 * @param src
 */
void DataPacket::setSource(const char &src)
{
    log();

    source = src;
}

/**
 * @brief DataPacket::setStatus TODO
 * @param stat
 */
void DataPacket::setStatus(const char &stat)
{
    log();

    status = stat;
}

void DataPacket::setSerial(const char ser[3])
{
    log();

    serial[0] = ser[0];
    serial[1] = ser[1];
    serial[2] = ser[2];
}

/**
 * @brief DataPacket::setId TODO
 * @param dev
 * @return
 */
void DataPacket::setId(const char& dev)
{
    log();

    id = dev;
}

/**
 * @brief DataPacket::generateJson TODO
 */
void DataPacket::generateJson()
{
    log();

    QJson::Parser       parser;
    QJson::Serializer   serializer;
    QVariantMap     map;
    QByteArray      out;

    map.insert("device", devices.value(id));
    map.insert("serial", "123ab");
    map.insert("data", "123");
    map.insert("signal", "80");
    // map.insert("action");
    // map.insert("battery");

    out = serializer.serialize(map);
    log() << out;
}
