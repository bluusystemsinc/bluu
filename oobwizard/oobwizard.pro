include(../common.pri)

TEMPLATE = app

DESTDIR = ../bin

embedded {
    DEFINES += EMBEDDED
}

HEADERS += src/wizardcontext.h \
    src/oobwizardwidget.h

SOURCES += src/oobwizard.cpp \
   src/wizardcontext.cpp \
    src/oobwizardwidget.cpp

FORMS += src/oobwizardwidget.ui
