include(../common.pri)

QT = core network

DEFINES += 'APPLICATION_NAME=\'\"Caim\"\''
VERSION = $$system(git rev-list HEAD | wc -l)
DEFINES += 'APPLICATION_VERSION=\'\"$${VERSION}\"\''

DEPENDPATH += . \
              qtservice/src \
              qtservice/examples/controller \
              qtservice/examples/interactive \
              qtservice/examples/server

INCLUDEPATH += . qtservice/src ../caim_sensorbase/include

# Input
HEADERS += qtservice/src/qtservice.h \
           qtservice/src/qtservice_p.h \
    src/sensormanager.h

HEADERS += ../caim_sensorbase/include/abstractsensor.h

SOURCES += src/caim.cpp \
           qtservice/src/qtservice.cpp \
    src/sensormanager.cpp

unix {
    HEADERS += qtservice/src/qtunixserversocket.h \
               qtservice/src/qtunixsocket.h

    SOURCES += qtservice/src/qtservice_unix.cpp \
               qtservice/src/qtunixserversocket.cpp \
               qtservice/src/qtunixsocket.cpp
}

win32:SOURCES += qtservice/src/qtservice_win.cpp

SAMPLES += qtservice/examples/controller/main.cpp \
           qtservice/examples/interactive/main.cpp \
           qtservice/examples/server/main.cpp

OTHER_FILES += $$SAMPLES
