PLUGIN_NAME = TestSensor

include(../caim_sensorbase/caim_sensorbase.pri)

DEFINES += MAJOR_VERSION=0
DEFINES += MINOR_VERSION=1

HEADERS += \
    src/randomsensor.h

SOURCES += \
    src/randomsensor.cpp
