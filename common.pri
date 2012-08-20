CONFIG += testing debug

OBJECTS_DIR = o
MOC_DIR = o
UI_DIR = o

CPU = $$(CPU)
isEmpty(CPU) {
    CPU = i386
}

message(Building $${TARGET} for $${CPU})

