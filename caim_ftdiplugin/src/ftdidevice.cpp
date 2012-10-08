#include "ftdidevice.h"

#include <QTimer>

FTDIDevice::FTDIDevice(QObject *parent) :
    QIODevice(parent)
{
    m_rxBytes = m_txBytes = m_event = 0;

    m_timer = new QTimer(this);
    m_timer->setInterval(100);
    connect(m_timer, SIGNAL(timeout()), SLOT(getStatus()));
}

FT_STATUS FTDIDevice::error() const
{
    return m_lastStatus;
}

bool FTDIDevice::open(int deviceNumber)
{
    m_lastStatus = FT_Open(deviceNumber, &m_handle);

    if(FT_OK == m_lastStatus)
    {
        FT_SetBaudRate(m_handle, FT_BAUD_57600);
        FT_SetDataCharacteristics(m_handle, FT_BITS_8, FT_STOP_BITS_1,
                                  FT_PARITY_NONE);
        m_timer->start(100);
    }
    return FT_OK == m_lastStatus;
}

qint64 FTDIDevice::readData(char *data, qint64 maxlen)
{
    m_lastStatus = FT_Read(m_handle, data, maxlen, &m_bytesReceived);
    return FT_OK == m_lastStatus ? m_bytesReceived : -1;
}

qint64 FTDIDevice::writeData(const char */*data*/, qint64 /*len*/)
{
    return -1;
}

void FTDIDevice::getStatus()
{
    m_lastStatus = FT_GetStatus(m_handle, &m_rxBytes, &m_txBytes, &m_event);
    if(FT_OK == m_lastStatus && m_rxBytes > 0)
        emit readyRead();
}
