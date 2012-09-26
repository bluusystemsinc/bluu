TEMPLATE = lib
QT = core network

include(../common.pri)

INCLUDEPATH = $$PWD/include
HEADERS += $$PWD/include/abstractsensor.h

isEmpty(PLUGIN_NAME) {
    error(PLUGIN_NAME can't be empty)
}

DEFINES += 'PLUGIN_NAME=\'\"$${PLUGIN_NAME}\"\''
