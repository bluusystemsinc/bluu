#ifndef DATAPACKET_H
#define DATAPACKET_H

#include <QObject>
#include <QMap>

// magic number (packet start)
#define MAGIC_NUMBER        0xAA
#include <QVariantMap>

// source type
#define SOURCE_SENSOR       0x57
#define SOURCE_RECEIVER     0x77

// device type
#define DEV_RECEIVER    0x00
#define DEV_DWV1        0x01
#define DEV_DWV2        0x02
#define DEV_DWV3        0x03
#define DEV_SHOCK       0x05
#define DEV_TILT        0x06
#define DEV_FLOOD       0x07
#define DEV_CO          0x08
#define DEV_SMOKE       0x09
#define DEV_PIR         0x0A
#define DEV_GLASS       0x0B
#define DEV_TAKEOVER    0x0C
#define DEV_KEY         0x0E
#define DEV_PANIC       0x0F

// status bytes
#define STATUS_ACTION       0x80
#define STATUS_INPUT1       0x40
#define STATUS_INPUT2       0x20
#define STATUS_INPUT3       0x10
#define STATUS_INPUT4       0x08
#define STATUS_TAMPER       0x04
#define STATUS_BATTERY      0x02
#define STATUS_SUPERVISORY  0x01

class DataPacket : public QObject
{
    Q_OBJECT

protected:
    quint8      source;
    quint8      status;
    quint8      id;
    QByteArray  serial;

protected:
    void jsonStatus(const quint8& bit, QVariantMap& map);

public:
    explicit DataPacket(QObject *parent = 0);
    void setSource(const quint8& src);
    void setStatus(const quint8& stat);
    void setSerial(const QByteArray& ser);
    void setId(const quint8& dev);
    void generateJson();
    QVariantMap generateJsonStatus();
    
signals:
    void packedReadySignal(QByteArray json);
    
public slots:
    
};

#endif // DATAPACKET_H
