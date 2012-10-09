#ifndef DEBUG_H
#define DEBUG_H

#include <QDebug>
#include <QThread>

#define log() qDebug()<<QThread::currentThread()<<__PRETTY_FUNCTION__

#endif // DEBUG_H
