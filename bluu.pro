TEMPLATE = subdirs

unix:SUBDIRS += libsensor/libsensor.pro
SUBDIRS += oobwizard/oobwizard.pro
buildQtDesktopComponents:SUBDIRS += qt-components-desktop/desktop.pro
