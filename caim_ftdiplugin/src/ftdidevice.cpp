#include "ftdidevice.h"

#include <QDebug>
#include <QThread>
#include <QMetaEnum>
#include <QMetaObject>

#include <debug.h>

QDebug operator<<(QDebug dbg, const FtdiDevice::FtStatus &status)
{
//    dbg.nospace() << "(" << status.x() << ", " << status.y() << ")";
    const QMetaObject &object = FtdiDevice::staticMetaObject;
    const int enumeratorIndex = object.indexOfEnumerator("FtStatus");
    const QMetaEnum enumerator = object.enumerator(enumeratorIndex);

    dbg.nospace()<<"FtStatus::"<<enumerator.valueToKey(status);

    return dbg.space();
}

FtdiDevice::FtdiDevice(QObject *parent) :
    QIODevice(parent)
{
    m_rxBytes = m_txBytes = m_event = 0;
}

FtdiDevice::FtStatus FtdiDevice::error() const
{
    return m_lastStatus;
}

bool FtdiDevice::open(int deviceNumber)
{
    log()<<"m_handle"<<m_handle;
    setLastError(FT_Open(deviceNumber, &m_handle));
    log()<<"m_lastStatus"<<m_lastStatus<<"m_handle"<<m_handle;
    if(FtOk == m_lastStatus)
    {
        FT_SetBaudRate(m_handle, FT_BAUD_57600);
        FT_SetDataCharacteristics(m_handle, FT_BITS_8, FT_STOP_BITS_1,
                                  FT_PARITY_NONE);
        startTimer(2000);
    }
    return FtOk == m_lastStatus;
}

qint64 FtdiDevice::bytesAvailable()
{
    return static_cast<qint64>(m_rxBytes);
}

qint64 FtdiDevice::readData(char *data, qint64 maxlen)
{
    setLastError(FT_Read(m_handle, data, maxlen, &m_bytesReceived));
    log()<<"m_lastStatus"<<m_lastStatus;
    return FtOk == m_lastStatus ? m_bytesReceived : -1;
}

qint64 FtdiDevice::writeData(const char */*data*/, qint64 /*len*/)
{
    return -1;
}

void FtdiDevice::timerEvent(QTimerEvent *)
{
    getStatus();
}

void FtdiDevice::setLastError(FT_STATUS status)
{
    m_lastStatus = static_cast<FtStatus>(status);
}

void FtdiDevice::getStatus()
{
    setLastError(FT_GetStatus(m_handle, &m_rxBytes, &m_txBytes, &m_event));
    log()<<"m_lastStatus"<<m_lastStatus<<"handle"<<m_handle;
    if(FtOk == m_lastStatus && m_rxBytes > 0)
        emit readyRead();
}
