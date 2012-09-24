CONFIG += testing debug

OBJECTS_DIR = o
MOC_DIR = o
UI_DIR = o

CPU = $$(CPU)
isEmpty(CPU) {
    CPU = i386
}

equals(TEMPLATE, app) {
    DESTDIR = $$PWD/bin
}
equals(TEMPLATE, lib) {
    DESTDIR = $$PWD/lib
}

DEFINES += 'ORGANIZATION_NAME=\'\"Bluu Systems\"\''
DEFINES += 'ORGANIZATION_DOMAIN=\'\"bluu\"\''

message(Building $${TARGET} for $${CPU})

