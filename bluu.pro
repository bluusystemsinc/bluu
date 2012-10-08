win32:system(type README)
else:system(cat README)

TEMPLATE = subdirs
unix:SUBDIRS += libsensor
#SUBDIRS += qt-desktop-components
SUBDIRS += oobwizard

SUBDIRS += caim
SUBDIRS += caim_ftdisensor
SUBDIRS += caim_testsensor

qt-desktop-components.file = qt-components-desktop/desktop.pro

copy_qtdesktop.commands = mkdir -p lib/imports && \
    rsync -avz --exclude 'Makefile' qt-components-desktop/components/ \
        lib/imports/QtDesktop

OTHER_FILES += README

QMAKE_EXTRA_TARGETS += copy_qtdesktop


