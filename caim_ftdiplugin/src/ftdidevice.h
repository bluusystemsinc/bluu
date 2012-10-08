#ifndef FTDIDEVICE_H
#define FTDIDEVICE_H

#include <QIODevice>
#include <ftd2xx.h>

class QTimer;

class FTDIDevice : public QIODevice
{
    Q_OBJECT
public:
    explicit FTDIDevice(QObject *parent = 0);

    virtual FT_STATUS error() const;
    virtual bool open(int deviceNumber);

protected:
    virtual qint64 readData(char *data, qint64 maxlen);
    virtual qint64 writeData(const char *data, qint64 len);

protected slots:
    void getStatus();

private:
    FT_STATUS m_lastStatus;
    FT_HANDLE m_handle;
    QTimer *m_timer;
    DWORD m_rxBytes, m_txBytes, m_event, m_bytesReceived;
};

#endif // FTDIDEVICE_H
