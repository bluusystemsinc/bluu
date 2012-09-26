TEMPLATE = app

include(../common.pri)
DESTDIR = ../bin

embedded {
    DEFINES += EMBEDDED
}

QT += network

HEADERS += src/wizardcontext.h \
    src/oobwizardwidget.h \
    src/welcomestepwidget.h \
    src/controllerstepwidget.h \
    src/systemconfigurationstepwidget.h \
    src/connectiontypestepwidget.h \
    src/enduserregistrationstepwidget.h \
    src/wirelesssettingsstepwidget.h \
    src/networksettingsstepwidget.h \
    src/networksettingssummarystepwidget.h \
    src/workflowfinishedstepwidget.h \
    src/enduserregistrationsummarystep.h \
    src/webRequest.h \
    src/qjson/stack.hh \
    src/qjson/serializerrunnable.h \
    src/qjson/serializer.h \
    src/qjson/qobjecthelper.h \
    src/qjson/qjson_export.h \
    src/qjson/qjson_debug.h \
    src/qjson/position.hh \
    src/qjson/parserrunnable.h \
    src/qjson/parser_p.h \
    src/qjson/parser.h \
    src/qjson/location.hh

SOURCES += src/oobwizard.cpp \
   src/wizardcontext.cpp \
    src/oobwizardwidget.cpp \
    src/welcomestepwidget.cpp \
    src/controllerstepwidget.cpp \
    src/systemconfigurationstepwidget.cpp \
    src/connectiontypestepwidget.cpp \
    src/enduserregistrationstepwidget.cpp \
    src/wirelesssettingsstepwidget.cpp \
    src/networksettingsstepwidget.cpp \
    src/networksettingssummarystepwidget.cpp \
    src/workflowfinishedstepwidget.cpp \
    src/enduserregistrationsummarystep.cpp \
    src/webRequest.cpp \
    src/qjson/serializerrunnable.cpp \
    src/qjson/serializer.cpp \
    src/qjson/qobjecthelper.cpp \
    src/qjson/parserrunnable.cpp \
    src/qjson/parser.cpp \
    src/qjson/json_scanner.cpp \
    src/qjson/json_parser.cc

FORMS += ui/oobwizardwidget.ui \
    ui/welcomeStep.ui \
    ui/controllerStep.ui \
    ui/systemConfigurationStep.ui \
    ui/connectionTypeStep.ui \
    ui/wirelessSettingsStep.ui \
    ui/networkSettingsStep.ui \
    ui/networkSettingsSummaryStep.ui \
    ui/endUserRegistrationStep.ui \
    ui/workflowFinished.ui \
    ui/enduserregistrationsummarystep.ui

OTHER_FILES += \
    src/qjson/json_parser.yy \
    ../../../qjson/src/json_parser.yy \
    src/qjson/json_parser.yy
