PLUGIN_NAME = BtSensor

include(../caim_sensorbase/caim_sensorbase.pri)

DEFINES += MAJOR_VERSION=0
DEFINES += MINOR_VERSION=1
INCLUDEPATH += $$HOME/projects/bluez-4.98/lib
INCLUDEPATH += /home/robal/projects/bluez-4.98/lib
QMAKE_CXXFLAGS += -fpermissive

HEADERS += \
    src/btdevice.h \
    src/btdevicethread.h \
    src/btplugin.h \
    src/btsensor.h

SOURCES += \
    src/btdevice.cpp \
    src/btdevicethread.cpp \
    src/btplugin.cpp \
    src/btsensor.cpp
