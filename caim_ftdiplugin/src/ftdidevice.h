#ifndef FTDIDEVICE_H
#define FTDIDEVICE_H

#include <QIODevice>
#include <ftd2xx.h>

class QTimer;

class FtdiDevice : public QIODevice
{
    Q_OBJECT
    Q_ENUMS(FtStatus)

public:
    enum FtStatus {
        FtOk = FT_OK,
        FtInvalidHandle = FT_INVALID_HANDLE,
        FtDeviceNotFound = FT_DEVICE_NOT_FOUND,
        FtDeviceNotOpened = FT_DEVICE_NOT_OPENED,
        FtIoError = FT_IO_ERROR,
        FtInsufficientResources = FT_INSUFFICIENT_RESOURCES,
        FtInvalidParameter = FT_INVALID_PARAMETER,
        FtInvalidBaudRate = FT_INVALID_BAUD_RATE,
        FtDeviceNotOpenedForErase = FT_DEVICE_NOT_OPENED_FOR_ERASE,
        FtDeviceNotOpenedForWrite = FT_DEVICE_NOT_OPENED_FOR_WRITE,
        FtFailedToWriteDevice = FT_FAILED_TO_WRITE_DEVICE,
        FtEepromReadFailed = FT_EEPROM_READ_FAILED,
        FtEepromWriteFailed = FT_EEPROM_WRITE_FAILED,
        FtEepromEraseFailed = FT_EEPROM_ERASE_FAILED,
        FtEepromNotPresent = FT_EEPROM_NOT_PRESENT,
        FtEepromNotProgrammed = FT_EEPROM_NOT_PROGRAMMED,
        FtInvalidArgs = FT_INVALID_ARGS,
        FtNotSupported = FT_NOT_SUPPORTED,
        FtOtherError = FT_OTHER_ERROR,
        FtDeviceListNotReady = FT_DEVICE_LIST_NOT_READY
    };

    explicit FtdiDevice(QObject *parent = 0);

    virtual FtStatus error() const;
    virtual bool open(int deviceNumber);
    virtual qint64 bytesAvailable();

protected:
    virtual qint64 readData(char *data, qint64 maxlen);
    virtual qint64 writeData(const char *data, qint64 len);
    void timerEvent(QTimerEvent *);
    void setLastError(FT_STATUS status);

protected slots:
    void getStatus();

private:
    FtStatus m_lastStatus;
    FT_HANDLE m_handle;
    DWORD m_rxBytes, m_txBytes, m_event, m_bytesReceived;
};

#endif // FTDIDEVICE_H
