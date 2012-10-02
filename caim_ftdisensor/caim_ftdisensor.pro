PLUGIN_NAME = FtdiSensor

include(../caim_sensorbase/caim_sensorbase.pri)

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


DEFINES += MAJOR_VERSION=0
DEFINES += MINOR_VERSION=1

HEADERS += \
    src/ftdisensor.h

SOURCES += \
    src/ftdisensor.cpp
