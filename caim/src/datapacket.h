#ifndef DATAPACKET_H
#define DATAPACKET_H

#include <QObject>
#include <QMap>

// magic number (packet start)
#define MAGIC_NUMBER        0xAA

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

class DataPacket : public QObject
{
    Q_OBJECT

protected:
    char            source;
    char            status;
    char            id;
    unsigned char   serial[3];

public:
    explicit DataPacket(QObject *parent = 0);
    void setSource(const char& src);
    void setStatus(const char& stat);
    void setSerial(const char ser[3]);
    void setId(const char& dev);
    void generateJson();
    
signals:
    
public slots:
    
};

#endif // DATAPACKET_H
