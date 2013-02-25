#ifndef DEBUGGER_H
#define DEBUGGER_H

#include <QObject>
#include "singleton.h"

/**
 * @brief The Debugger class
 */
class Debugger : public QObject
{
    Q_OBJECT

public:
    explicit Debugger(QObject *parent = 0);
    
signals:
    
public slots:
    void debugSlot(QString debugMessage);
};

typedef CBluuSingleton<Debugger>    CBluuDebugger;

#endif // DEBUGGER_H
