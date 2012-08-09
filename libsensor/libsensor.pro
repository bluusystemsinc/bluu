CONFIG += testing

testing  {
    OLDTARGET = $$TARGET
    TEMPLATE = app
    DESTDIR = ../bin
    TARGET = testing_$$OLDTARGET
}
else {
    TEMPLATE = lib
    DESTDIR = ../lib
}

QT -= gui

OBJECTS_DIR = o
MOC_DIR = o

include(../qextserialport/src/qextserialport.pri)
#QEXTSERIALPORT_LIBRARY = yes
QEXTSERIALPORT_STATIC = yes

HEADERS += \
    src/ftdiserialport.h

SOURCES += \
    src/ftdiserialport.cpp

testing:SOURCES += src/main.cpp
