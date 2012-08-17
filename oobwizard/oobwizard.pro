include(../common.pri)

TEMPLATE = app
QT += declarative

DESTDIR = ../bin

QML_IMPORT_PATH = ../lib/imports

HEADERS += \
    src/wizardcontext.h
SOURCES += src/oobwizard.cpp \
    src/wizardcontext.cpp

QML_FILES += qml/main.qml \
    qml/welcomeStep.qml \
    qml/userDataStep.qml

OTHER_FILES = $$QML_FILES

for(qml, QML_FILES) {
    QML = $$basename(qml)
    QMLNAME = $$replace(QML, \\., _)
    DEFINES *= '$$upper($$QMLNAME)=\\"$$QML\\"'
    message($$DEFINES)
}
