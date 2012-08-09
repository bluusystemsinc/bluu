#ifndef FTDISERIALPORT_H
#define FTDISERIALPORT_H

#include <qextserialport.h>

class FTDISerialPort : public QextSerialPort
{
    Q_OBJECT
public:
    explicit FTDISerialPort(const QString &portName, QObject *parent = 0);
    
protected slots:
    void setPortName(const QString &name);
    void setQueryMode(QueryMode mode);
    void setBaudRate(BaudRateType baudRate);
    void setDataBits(DataBitsType dataBits);
    void setParity(ParityType parity);
    void setStopBits(StopBitsType stopBits);
    void setFlowControl(FlowType fowControl);
    void setTimeout(long timeout);

    void setDtr(bool set = true);
    void setRts(bool set = true);
};

#endif // FTDISERIALPORT_H
