system(more README)

TEMPLATE = subdirs

unix:SUBDIRS += libsensor
SUBDIRS += oobwizard
buildQtDesktopComponents: {
	SUBDIRS += qt-components-desktop/desktop.pro
}
