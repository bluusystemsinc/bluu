#ifndef DATAPARSER_H
#define DATAPARSER_H

#include <QObject>
#include "singleton.h"
#include "datapacket.h"

class DataParser : public QObject
{
    Q_OBJECT

private:
    QByteArray*     data;
    DataPacket      packet;

protected:
    bool checkCRC();
    bool checkMagic();
    bool checkSource();
    bool checkDevice();
    void checkStatus();
    void checkSerial();

public:
    explicit DataParser(QObject *parent = 0);
    void parseData(QByteArray* buffer);
    
signals:
    
public slots:
    
};

typedef CBluuSingleton<DataParser>      CBluuDataParser;

#endif // DATAPARSER_H
