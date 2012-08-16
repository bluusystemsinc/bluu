win32:system(type README)
else:system(cat README)

TEMPLATE = subdirs

unix:SUBDIRS += libsensor
SUBDIRS += oobwizard
buildQtDesktopComponents: {
        SUBDIRS += qt-components-desktop/desktop.pro
}
