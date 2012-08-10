CONFIG += testing debug

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

CPU = $$(CPU)
isEmpty(CPU) {
    CPU = i386
}
message(Building for $${CPU})

include(../qextserialport/src/qextserialport.pri)
#QEXTSERIALPORT_LIBRARY = yes
QEXTSERIALPORT_STATIC = yes

INCLUDEPATH += $$PWD/../libftd2xx
DEPENDPATH += $$PWD/../libftd2xx
unix:!macx:!symbian: {
    LIBS += -L$$PWD/../libftd2xx/build/$${CPU}
    LIBS += -ldl
    LIBS += -lrt
    LIBS += -lftd2xx
    PRE_TARGETDEPS += $$PWD/../libftd2xx/build/$${CPU}/libftd2xx.a
}
unix:!macx:!symbian:

HEADERS += \
    src/ftdiserialport.h

SOURCES += \
    src/ftdiserialport.cpp

testing:SOURCES += src/main.cpp
