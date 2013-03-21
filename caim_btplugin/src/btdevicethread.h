#ifndef BTDEVICETHREAD_H
#define BTDEVICETHREAD_H

#include <stdint.h>
#include <bluetooth.h>
#include <QThread>
#include <hci.h>

/**
 * @brief The frame struct
 */
struct frame {
        void            *data;
        uint32_t        data_len;
        void            *ptr;
        uint32_t        len;
        uint16_t        dev_id;
        uint8_t         in;
        uint8_t         master;
        uint16_t        handle;
        uint16_t        cid;
        uint16_t        num;
        uint8_t         dlci;
        uint8_t         channel;
        unsigned long   flags;
        struct timeval  ts;
        int             pppdump_fd;
        int             audio_fd;
};

/**
 * @brief The hcidump_hdr struct
 */
struct hcidump_hdr
{
    quint16	len;
    quint8	in;
    quint8	pad;
    quint32	ts_sec;
    quint32	ts_usec;
} __attribute__ ((packed));

#define HCIDUMP_HDR_SIZE (sizeof(struct hcidump_hdr))
#define SNAP_LEN	HCI_MAX_FRAME_SIZE

/**
 * @brief The BtDeviceThread class
 */
class BtDeviceThread : public QThread
{
    Q_OBJECT

protected:
    int     sck;

protected:
    virtual void run();
    void parse(frame* frm);

public:
    explicit BtDeviceThread(QObject* parent = 0);
    void setSocket(const int& sk);
    
signals:
    
public slots:
    
};

#endif // BTDEVICETHREAD_H
