TEMPLATE += app

QT -= gui

DESTDIR = ../lib
OBJECTS_DIR = o
MOC_DIR = o

include(../qextserialport/src/qextserialport.pri)
#QEXTSERIALPORT_LIBRARY = yes
QEXTSERIALPORT_STATIC = yes


SOURCES += src/main.cpp
