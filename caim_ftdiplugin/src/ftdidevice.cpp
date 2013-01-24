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
    connect(&thread, SIGNAL(dataAvailable()), SLOT(getStatus()));
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
        FT_SetBaudRate(m_handle, FT_BAUD_460800);
        FT_SetDataCharacteristics(m_handle, FT_BITS_8, FT_STOP_BITS_1,
                                  FT_PARITY_NONE);
        thread.setHandle(m_handle);
        thread.start();
    }
    return FtOk == m_lastStatus;
}

qint64 FtdiDevice::bytesAvailable()
{
    return static_cast<qint64>(m_rxBytes);
}

QByteArray FtdiDevice::readAll()
{
    QByteArray  out;
    BYTE        buffer[64];
    DWORD       count = 0;
    FT_STATUS   status = FT_OTHER_ERROR;
    QString     s = "";

    status = FT_Read(m_handle, buffer, m_rxBytes, &count);

    if(FT_OK == status)
    {
        for(int i = 0; i < count; i++)
        {
            out.append(buffer[i]);
            s += QString::number(buffer[i], 16);
            s += " ";
        }

        log() << s;
    }
    else
    {
        log() << "FT_Read failed: " << status;
    }

    return out;
}

qint64 FtdiDevice::readData(char *data, qint64 maxlen)
{
    log();


    /*
    setLastError(FT_Read(m_handle, data, maxlen, &m_bytesReceived));
    log()<<"m_lastStatus"<<m_lastStatus;
    return FtOk == m_lastStatus ? m_bytesReceived : -1;
    */
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
    log();

    DWORD       event = 0;
    FT_STATUS   status = FT_OTHER_ERROR;

    status = FT_GetStatus(m_handle, &m_rxBytes, &m_txBytes, &event);

    if(FT_OK == status)
    {
        if(0 < m_rxBytes)
        {
            emit readyRead();
        }
        else
        {
            log() << "FT_GetStatus failed, no bytes read";
        }
    }
    else
    {
        log() << "FT_GetStatus failed: " << status;
    }

    /*
    {
        DWORD   EventDWord;
        DWORD   RxBytes;
        DWORD   TxBytes;
        DWORD   Status;
        DWORD   count = 0;
        BYTE    buffer[256];

        FT_GetStatus(handle,&RxBytes,&TxBytes,&EventDWord);

        if(RxBytes > 0)
        {
            // log() << "RxBytes: " << RxBytes;
            // log() << "TxBytes: " << TxBytes;
            // log() << "EventDWord: " << EventDWord;
            FT_Read(handle, buffer, RxBytes, &count);
            log() << "read bytes: " << count;

            QString     s = 0;

            for(int i = 0; i < count; i++)
            {
                s += QString::number(buffer[i], 16);
                s += " ";
             }

            log() << s;
        }
    }
    */

    /*
    setLastError(FT_GetStatus(m_handle, &m_rxBytes, &m_txBytes, &m_event));

    log()<<"m_lastStatus"<<m_lastStatus<<"handle"<<m_handle;

    if(FtOk == m_lastStatus)
    {
        if(0 < m_rxBytes)
        {
            BYTE        buffer[256];
            DWORD       count = 0;
            FT_STATUS   status = FT_Read(m_handle, buffer, m_rxBytes, &count);

            if(FT_OK == status)
            {
                log() << count << "bytes read";

                for(int i = 0; i < count; i++)
                    log() << std::hex << buffer[i] << "\n";

                emit readyRead();
                m_rxBytes = 0;
            }
            else
            {
                log() << "Error reading bytes";
            }
        }
        else
        {
            log() << "No bytes read";
        }
    }
    else
    {
        log() << "Status failed: " << m_lastStatus;
    }
    */
}

void FtdiDeviceThread::setHandle(const FT_HANDLE &_handle)
{
    handle = _handle;
}

void FtdiDeviceThread::run()
{
    log();

    DWORD           eventMask;
    EVENT_HANDLE    eventHandle;

    pthread_mutex_init(&eventHandle.eMutex, NULL);
    pthread_cond_init(&eventHandle.eCondVar, NULL);
    eventMask = FT_EVENT_RXCHAR;
    FT_SetEventNotification(handle, eventMask, (PVOID)&eventHandle);

    while(1)
    {
        pthread_mutex_lock(&eventHandle.eMutex);
        pthread_cond_wait(&eventHandle.eCondVar, &eventHandle.eMutex);
        pthread_mutex_unlock(&eventHandle.eMutex);
        waitForBuffer();
        emit dataAvailable();
        FT_SetEventNotification(handle, eventMask, (PVOID)&eventHandle);
    }
}

void FtdiDeviceThread::waitForBuffer()
{
    for(int i = 0; i < 1000000; i++)
        ;
}
