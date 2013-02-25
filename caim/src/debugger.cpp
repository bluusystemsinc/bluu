#include "debugger.h"
#include <QDebug>

/**
 * @brief Debugger::Debugger
 * @param parent
 */
Debugger::Debugger(QObject *parent)
        : QObject(parent)
{
}

void Debugger::debugSlot(QString debugMessage)
{
    qDebug() << debugMessage;
}
