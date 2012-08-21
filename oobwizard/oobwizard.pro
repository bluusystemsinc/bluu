include(../common.pri)

TEMPLATE = app

DESTDIR = ../bin

embedded {
    DEFINES += EMBEDDED
}

HEADERS += src/wizardcontext.h \
    src/oobwizardwidget.h \
    src/welcomestepwidget.h \
    src/controllerstepwidget.h \
    src/systemconfigurationstepwidget.h \
    src/connectiontypestepwidget.h \
    src/enduserregistrationstepwidget.h \
    src/wirelesssettingsstepwidget.h \
    src/networksettingsstepwidget.h \
    src/networksettingssummarystepwidget.h

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
    src/networksettingssummarystepwidget.cpp

FORMS += ui/oobwizardwidget.ui \
    ui/welcomeStep.ui \
    ui/controllerStep.ui \
    ui/systemConfigurationStep.ui \
    ui/connectionTypeStep.ui \
    ui/wirelessSettingsStep.ui \
    ui/networkSettingsStep.ui \
    ui/networkSettingsSummaryStep.ui \
    ui/endUserRegistrationStep.ui
