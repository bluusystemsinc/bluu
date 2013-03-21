#include "btplugin.h"
#include "btsensor.h"

addVersionInfo();

extern "C" AbstractSensorList instances()
{
    AbstractSensorList list;

    list.append(new BtSensor());
    return list;
}
