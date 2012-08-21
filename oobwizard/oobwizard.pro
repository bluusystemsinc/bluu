include(../common.pri)

TEMPLATE = app
QT += declarative

DESTDIR = ../bin

QML_IMPORT_PATH = ../lib/imports

HEADERS += \
#    src/wizardcontext.h \
    src/oobwizardwidget.h

SOURCES += src/oobwizard.cpp \
#   src/wizardcontext.cpp \
    src/oobwizardwidget.cpp

#QML_FILES += qml/main.qml \
#    qml/welcomeStep.qml \
#    qml/userDataStep.qml

#DUMMY_QML_FILES += dummydata/context.qml \
#    dummydata/context/main.qml

#OTHER_FILES = $$QML_FILES $$DUMMY_QML_FILES

#for(qml, QML_FILES) {
#    QML = $$basename(qml)
#    QMLNAME = $$replace(QML, \\., _)
#    DEFINES *= '$$upper($$QMLNAME)=\\"$$QML\\"'
#    message($$DEFINES)
#}

FORMS += \
    src/oobwizardwidget.ui
