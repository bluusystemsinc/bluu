#ifndef DEBUG_H
#define DEBUG_H

#include <QDebug>
#include <QThread>

// #define debugMessage() qDebug()<<QThread::currentThread()<<__PRETTY_FUNCTION__
#define debugMessage() qDebug() << __PRETTY_FUNCTION__

#define debugMessageThread(value) \
{ \
    QString     debugMessage = QString("%1 %2").arg(__PRETTY_FUNCTION__).arg(value); \
\
    emit debugSignal(debugMessage); \
};

#endif // DEBUG_H
