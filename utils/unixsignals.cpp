#include <QDebug>
#include <sys/socket.h>
#include <signal.h>
#include "unixsignals.h"

int UnixSignals::sighupFd[2];
int UnixSignals::sigtermFd[2];
int UnixSignals::sigintFd[2];

UnixSignals::UnixSignals(QObject* parent)
            : QObject(parent)
{
    qDebug() << __PRETTY_FUNCTION__;

    if (::socketpair(AF_UNIX, SOCK_STREAM, 0, sighupFd))
        qFatal("Couldn't create HUP socketpair");

    if (::socketpair(AF_UNIX, SOCK_STREAM, 0, sigtermFd))
        qFatal("Couldn't create TERM socketpair");

    if (::socketpair(AF_UNIX, SOCK_STREAM, 0, sigintFd))
        qFatal("Couldn't create TERM socketpair");

    snHup = new QSocketNotifier(sighupFd[1], QSocketNotifier::Read, this);
    connect(snHup, SIGNAL(activated(int)), this, SLOT(handleSigHup()));
    snTerm = new QSocketNotifier(sigtermFd[1], QSocketNotifier::Read, this);
    connect(snTerm, SIGNAL(activated(int)), this, SLOT(handleSigTerm()));
    snInt = new QSocketNotifier(sigintFd[1], QSocketNotifier::Read, this);
    connect(snInt, SIGNAL(activated(int)), this, SLOT(handleSigInt()));
}

int UnixSignals::setupUnixSignalHandlers()
 {
     struct sigaction    hup;
     struct sigaction    term;
     struct sigaction    sigInt;

     hup.sa_handler = UnixSignals::hupSignalHandler;
     sigemptyset(&hup.sa_mask);
     hup.sa_flags = 0;
     hup.sa_flags |= SA_RESTART;

     if(sigaction(SIGHUP, &hup, 0) > 0)
        return 1;

     term.sa_handler = UnixSignals::termSignalHandler;
     sigemptyset(&term.sa_mask);
     term.sa_flags |= SA_RESTART;

     if(sigaction(SIGTERM, &term, 0) > 0)
        return 2;

     sigInt.sa_handler = UnixSignals::intSignalHandler;
     sigemptyset(&sigInt.sa_mask);
     sigInt.sa_flags |= SA_ONSTACK;

     if (sigaction(SIGINT, &sigInt, 0) > 0)
        return 1;

     return 0;
 }

void UnixSignals::hupSignalHandler(int unused)
{
    Q_UNUSED(unused);

    char a = 1;
    ::write(sighupFd[0], &a, sizeof(a));
}

void UnixSignals::termSignalHandler(int unused)
{
    Q_UNUSED(unused);

    char a = 1;
    ::write(sigtermFd[0], &a, sizeof(a));
}

void UnixSignals::intSignalHandler(int unused)
{
    qDebug() << __PRETTY_FUNCTION__;

    Q_UNUSED(unused);

    char a = 1;
    ::write(sigintFd[0], &a, sizeof(a));
}

void UnixSignals::handleSigHup()
{
    snHup->setEnabled(false);
    char tmp;
    ::read(sighupFd[1], &tmp, sizeof(tmp));

    // do Qt stuff

    snHup->setEnabled(true);
}

void UnixSignals::handleSigTerm()
{
    snTerm->setEnabled(false);
    char tmp;
    ::read(sigtermFd[1], &tmp, sizeof(tmp));

    // do Qt stuff

    snTerm->setEnabled(true);
}

void UnixSignals::handleSigInt()
{
    qDebug() << __PRETTY_FUNCTION__;

    snInt->setEnabled(false);
    char tmp;
    ::read(sigintFd[1], &tmp, sizeof(tmp));

    // do Qt stuff
    emit unloadSensorsSignal();

    snInt->setEnabled(true);
    exit(0);
}
