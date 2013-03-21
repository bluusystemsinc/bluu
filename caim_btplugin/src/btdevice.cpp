#include "btdevice.h"
#include "debug.h"
#include <sys/socket.h>
#include <errno.h>
#include <bluetooth.h>
#include <hci.h>
#include <hci_lib.h>

/**
 * @brief BtDevice::BtDevice
 * @param parent
 */
BtDevice::BtDevice(QObject* parent)
        : QObject(parent)
{
    debugMessage();

    int     sck;
    int     opt;
    int     res;
    int     dev = 0;
    struct hci_filter   flt;
    struct sockaddr_hci addr;

    /* Create HCI socket */
    sck = socket(AF_BLUETOOTH, SOCK_RAW, BTPROTO_HCI);

    if(0 > sck)
        qDebug() << "Can't create raw socket";

    opt = 1;
    res = setsockopt(sck, SOL_HCI, HCI_DATA_DIR, &opt, sizeof(opt));

    if(0 > res)
        qDebug() << "Can't enable data direction info";

    opt = 1;
    res = setsockopt(sck, SOL_HCI, HCI_TIME_STAMP, &opt, sizeof(opt));

    if(0 > res)
        qDebug() << "Can't enable time stamp";

    /* Setup filter */
    hci_filter_clear(&flt);
    hci_filter_all_ptypes(&flt);
    hci_filter_all_events(&flt);
    res = setsockopt(sck, SOL_HCI, HCI_FILTER, &flt, sizeof(flt));

    if(0 > res)
        qDebug() << "Can't set filter";

    /* Bind socket to the HCI device */
    memset(&addr, 0, sizeof(addr));
    addr.hci_family = AF_BLUETOOTH;
    addr.hci_dev = dev;
    res = bind(sck, (struct sockaddr *) &addr, sizeof(addr));

    if(0 > res)
    {
        QString     str = QString("Can't attach to device hci%1. %2(%3)").arg(dev).arg(strerror(errno)).arg(errno);
        qDebug() << str;
    }

    thread.setSocket(sck);
    thread.start();
}
