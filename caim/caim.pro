include(../common.pri)

QT = core network sql

DEFINES += 'APPLICATION_NAME=\'\"Caim\"\''
VERSION = $$system(git rev-list HEAD | wc -l)
DEFINES += 'APPLICATION_VERSION=\'\"$${VERSION}\"\''

DEPENDPATH += . \
              qtservice/src \
              qtservice/examples/controller \
              qtservice/examples/interactive \
              qtservice/examples/server

INCLUDEPATH += . qtservice/src ../caim_sensorbase/include
INCLUDEPATH += ../utils
INCLUDEPATH += /home/robal/libs/qjson/build/lib/Headers
INCLUDEPATH += /home/robal/libs/jsonqt/lib

LIBS += -L/home/robal/libs/qjson/build/lib -lqjson
LIBS += -L/home/robal/libs/jsonqt/build/lib -lJsonQt

# Input
HEADERS += qtservice/src/qtservice.h \
           qtservice/src/qtservice_p.h \
    src/sensormanager.h \
    ../utils/unixsignals.h \
    ../utils/singleton.h \
    src/dataparser.h \
    src/datapacket.h \
    src/datamanager.h \
    src/webrequest.h \
    src/datamanagerthread.h \
    src/databasemanager.h \
    ../caim_sensorbase/include/debug.h \
    src/debugger.h \
    src/exception.h \
    src/databaseexception.h \
    src/scheduler.h \
    src/task.h \
    src/databasesendtask.h \
    src/packetsendtask.h \
    src/settingsmanager.h \
    src/controlerlivetask.h

HEADERS += ../caim_sensorbase/include/abstractsensor.h

SOURCES += src/caim.cpp \
           src/datamanager.cpp \
           src/dataparser.cpp \
           src/datapacket.cpp \
           src/sensormanager.cpp \
           ../utils/unixsignals.cpp \
    src/webrequest.cpp \
    src/datamanagerthread.cpp \
    src/databasemanager.cpp \
    src/debugger.cpp \
    src/exception.cpp \
    src/databaseexception.cpp \
    src/scheduler.cpp \
    src/task.cpp \
    src/databasesendtask.cpp \
    src/packetsendtask.cpp \
    src/settingsmanager.cpp \
    src/controlerlivetask.cpp

unix {
    HEADERS += qtservice/src/qtunixserversocket.h \
               qtservice/src/qtunixsocket.h

    SOURCES +=
}

win32:SOURCES +=

SAMPLES += qtservice/examples/controller/main.cpp \
           qtservice/examples/interactive/main.cpp \
           qtservice/examples/server/main.cpp

OTHER_FILES += $$SAMPLES

HEADERS += \
    src/senddatamanager.h

SOURCES += \
    src/senddatamanager.cpp

HEADERS += \
    src/jsonrequest.h

SOURCES += \
    src/jsonrequest.cpp

HEADERS +=
