#include "ftdiserialport.h"

FTDISerialPort::FTDISerialPort(const QString &portName, QObject *parent) :
    QextSerialPort(portName, EventDriven, parent)
{
    setBaudRate(BAUD57600);
    setParity(PAR_NONE);
    setDataBits(DATA_8);
}

void FTDISerialPort::setPortName(const QString &name)
{
    QextSerialPort::setPortName(name);
}

void FTDISerialPort::setQueryMode(QextSerialPort::QueryMode mode)
{
    QextSerialPort::setQueryMode(mode);
}

void FTDISerialPort::setBaudRate(BaudRateType baudRate)
{
    QextSerialPort::setBaudRate(baudRate);
}

void FTDISerialPort::setDataBits(DataBitsType dataBits)
{
    QextSerialPort::setDataBits(dataBits);
}

void FTDISerialPort::setParity(ParityType parity)
{
    QextSerialPort::setParity(parity);
}

void FTDISerialPort::setStopBits(StopBitsType stopBits)
{
    QextSerialPort::setStopBits(stopBits);
}

void FTDISerialPort::setFlowControl(FlowType fowControl)
{
    QextSerialPort::setFlowControl(fowControl);
}

void FTDISerialPort::setTimeout(long timeout)
{
    QextSerialPort::setTimeout(timeout);
}

void FTDISerialPort::setDtr(bool set)
{
    QextSerialPort::setDtr(set);
}

void FTDISerialPort::setRts(bool set)
{
    QextSerialPort::setRts(set);
}
