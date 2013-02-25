#include "datapacket.h"
#include "parser.h"
#include "serializer.h"
#include "debug.h"
#include "datamanager.h"
#include <QVariantList>
#include <QFile>
#include <QDateTime>

static QMap<quint8, QString> devicesMapInit()
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

static QMap<quint8, QString> statusMapInit()
{
    QMap<quint8, QString>   map;

    map.insert(STATUS_ACTION, "action");
    map.insert(STATUS_INPUT1, "input1");
    map.insert(STATUS_INPUT2, "input2");
    map.insert(STATUS_INPUT3, "input3");
    map.insert(STATUS_INPUT4, "input4");
    map.insert(STATUS_TAMPER, "tamper");
    map.insert(STATUS_BATTERY, "battery");
    map.insert(STATUS_SUPERVISORY, "supervisory");

    return map;
}

static const QMap<quint8, QString>  devicesMap = devicesMapInit();
static const QMap<quint8, QString>  statusMap = statusMapInit();

/**
 * @brief DataPacket::DataPacket TDOO
 * @param parent
 */
DataPacket::DataPacket(QObject *parent) :
    QObject(parent)
{
    debugMessage();
    connect(this, SIGNAL(packedReadySignal(QByteArray)), CBluuDataManager::Instance(), SLOT(packedReadySlot(QByteArray)));
}

/**
 * @brief DataPacket::setSource TODO
 * @param src
 */
void DataPacket::setSource(const quint8& src)
{
    debugMessage();

    source = src;
}

/**
 * @brief DataPacket::setStatus TODO
 * @param stat
 */
void DataPacket::setStatus(const quint8& stat)
{
    debugMessage();

    status = stat;
}

/**
 * @brief DataPacket::setSerial
 * @param ser
 */
void DataPacket::setSerial(const QByteArray& ser)
{
    debugMessage();

    serial = ser;
}

/**
 * @brief DataPacket::setId TODO
 * @param dev
 * @return
 */
void DataPacket::setId(const quint8& dev)
{
    debugMessage();

    id = dev;
}

/**
 * @brief DataPacket::generateJson TODO
 */
void DataPacket::generateJson()
{
    debugMessage();

    QFile           file("json.txt");

    file.open(QIODevice::Append | QIODevice::WriteOnly | QIODevice::Text);

    QTextStream     stream(&file);

    QJson::Parser       parser;
    QJson::Serializer   serializer;
    QVariantMap     map;
    QByteArray      out;

    map.insert("timestamp", QDateTime::currentDateTime ().toString("yyyy-MM-dd hh:mm:ss"));
    map.insert("serial", serial);
    map.insert("data", 0);
    map.insert("signal", 80);
    map.unite(generateJsonStatus());

    serializer.setIndentMode(QJson::IndentFull);
    out = serializer.serialize(map);

    stream << out << "\n";
    file.close();

    emit packedReadySignal(out);
    debugMessage() << out;
}

/**
 * @brief DataPacket::generateJsonStatus TODO
 * @param map
 */
QVariantMap DataPacket::generateJsonStatus()
{
    debugMessage();

    QVariantMap     map;

    jsonStatus(STATUS_ACTION, map);
    jsonStatus(STATUS_INPUT1, map);
    jsonStatus(STATUS_INPUT2, map);
    jsonStatus(STATUS_INPUT3, map);
    jsonStatus(STATUS_INPUT4, map);
    jsonStatus(STATUS_TAMPER, map);
    jsonStatus(STATUS_BATTERY, map);
    jsonStatus(STATUS_SUPERVISORY, map);

    return map;
}

/**
 * @brief DataPacket::jSonStatus TODO
 * @param bit
 * @param map
 */
void DataPacket::jsonStatus(const quint8& bit, QVariantMap& map)
{
    // debugMessage();

    if(0 != (bit & status))
        map.insert(statusMap.value(bit), true);
    else
        map.insert(statusMap.value(bit), false);
}
