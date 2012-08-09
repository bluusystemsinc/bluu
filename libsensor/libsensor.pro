CONFIG += testing

testing  {
    TEMPLATE = app
}
else {
    TEMPLATE = lib
}

QT -= gui

DESTDIR = ../lib
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
