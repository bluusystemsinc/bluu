win32:system(type README)
else:system(cat README)

TEMPLATE = subdirs
#unix:SUBDIRS += libsensor
#SUBDIRS += qt-desktop-components
SUBDIRS += oobwizard
<<<<<<< HEAD
=======
SUBDIRS += caim

>>>>>>> 4768e5e734e86600a813c5c163e001da18219fb3
qt-desktop-components.file = qt-components-desktop/desktop.pro

copy_qtdesktop.commands = mkdir -p lib/imports && \
    rsync -avz --exclude 'Makefile' qt-components-desktop/components/ \
        lib/imports/QtDesktop

OTHER_FILES += README

QMAKE_EXTRA_TARGETS += copy_qtdesktop


