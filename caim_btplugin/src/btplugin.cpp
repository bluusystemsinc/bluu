#include "btplugin.h"

addVersionInfo();

extern "C" AbstractSensorList instances()
{
    AbstractSensorList list;

    // list.append(new FtdiSensor);
    return list;
}
