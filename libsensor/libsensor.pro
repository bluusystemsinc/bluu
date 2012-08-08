TEMPLATE += app

QT -= gui

include(../qextserialport/src/qextserialport.pri)
#QEXTSERIALPORT_LIBRARY = yes
QEXTSERIALPORT_STATIC = yes

SOURCES += src/main.cpp
