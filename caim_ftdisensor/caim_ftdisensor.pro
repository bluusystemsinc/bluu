PLUGIN_NAME = FtdiSensor

include(../caim_sensorbase/caim_sensorbase.pri)

DEFINES += MAJOR_VERSION=0
DEFINES += MINOR_VERSION=1

HEADERS += \
    src/ftdisensor.h

SOURCES += \
    src/ftdisensor.cpp
