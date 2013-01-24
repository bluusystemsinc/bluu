#ifndef UNIXSIGNALS_H
#define UNIXSIGNALS_H

#include <QObject>
#include <QSocketNotifier>
#include "singleton.h"

class UnixSignals : public QObject
{
    Q_OBJECT

public:
    explicit UnixSignals(QObject* parent = 0);

    // Unix signal handlers.
    static void hupSignalHandler(int unused);
    static void termSignalHandler(int unused);
    static void intSignalHandler(int unused);
    static int setupUnixSignalHandlers();

private:
    static int sighupFd[2];
    static int sigtermFd[2];
    static int sigintFd[2];
    QSocketNotifier*    snHup;
    QSocketNotifier*    snTerm;
    QSocketNotifier*    snInt;

signals:
    void unloadSensorsSignal();
    
public slots:
    void handleSigHup();
    void handleSigTerm();
    void handleSigInt();
};

typedef CBluuSingleton<UnixSignals>     CBluuUnixSignals;

#endif // UNIXSIGNALS_H
