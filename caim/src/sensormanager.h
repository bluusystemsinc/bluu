#ifndef SENSORMANAGER_H
#define SENSORMANAGER_H

#include <QObject>
#include <QMultiMap>

class AbstractSensor;

class SensorManager : public QObject
{
    Q_OBJECT
public:
    explicit SensorManager(QObject *parent = 0);

public slots:
    void loadSensorLibraries();
private:
    typedef QMultiMap<QString,AbstractSensor*>PluginsLoadedMap;

    PluginsLoadedMap m_pluginsLoaded;
};

#endif // SENSORMANAGER_H
