#include "btdevicethread.h"
#include "debug.h"
#include <poll.h>

/**
 * @brief BtDeviceThread::BtDeviceThread
 * @param parent
 */
BtDeviceThread::BtDeviceThread(QObject* parent)
              : QThread(parent)
{
}

/**
 * @brief BtDeviceThread::setSocket
 * @param sck
 */
void BtDeviceThread::setSocket(const int &sk)
{
    sck = sk;
}

/**
 * @brief BtDeviceThread::run
 */
void BtDeviceThread::run()
{
    int     device = 0;
    int     hdr_size = HCIDUMP_HDR_SIZE;
    int     snap_len = SNAP_LEN;
    char*   buf = NULL;
    char*   ctrl = NULL;
    struct hcidump_hdr*     dh;
    struct btsnoop_pkt*     dp;
    struct frame frm;
    struct msghdr msg;
    struct cmsghdr* cmsg;
    struct iovec  iv;
    struct pollfd fds[2];
    int nfds = 0;
    int len = 0;

    if(0 > sck)
    {
        // TODO debug thread messge
        return;
    }

    buf = malloc(snap_len + hdr_size);
    dh = (void*) buf;
    dp = (void*) buf;
    frm.data = buf + hdr_size;
    ctrl = malloc(100);
    memset(&msg, 0, sizeof(msg));
    fds[nfds].fd = sck;
    fds[nfds].events = POLLIN;
    fds[nfds].revents = 0;
    nfds++;

    while(1)
    {
        int i, n = poll(fds, nfds, -1);

        if (n <= 0)
                    continue;

        iv.iov_base = frm.data;
        iv.iov_len  = snap_len;

        msg.msg_iov = &iv;
        msg.msg_iovlen = 1;
        msg.msg_control = ctrl;
        msg.msg_controllen = 100;
        len = recvmsg(sck, &msg, MSG_DONTWAIT);

        /* Process control message */
        frm.data_len = len;
        frm.dev_id = device;
        frm.in = 0;
        // frm.pppdump_fd = parser.pppdump_fd;
        // frm.audio_fd   = parser.audio_fd;

        cmsg = CMSG_FIRSTHDR(&msg);

        while (cmsg) {
            int dir;
            switch (cmsg->cmsg_type) {
            case HCI_CMSG_DIR:
                memcpy(&dir, CMSG_DATA(cmsg), sizeof(int));
                frm.in = (uint8_t) dir;
                break;
            case HCI_CMSG_TSTAMP:
                memcpy(&frm.ts, CMSG_DATA(cmsg),
                       sizeof(struct timeval));
                break;
            }
            cmsg = CMSG_NXTHDR(&msg, cmsg);
        }

        frm.ptr = frm.data;
        frm.len = frm.data_len;
    }
}

/**
 * @brief BtDeviceThread::parse
 * @param frm
 */
void BtDeviceThread::parse(frame* frm)
{
}
