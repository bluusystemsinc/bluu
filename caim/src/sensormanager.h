#ifndef SENSORMANAGER_H
#define SENSORMANAGER_H

#include <QObject>
#include <QMultiMap>
#include <QTimer>

class AbstractSensor;

class SensorManager : public QObject
{
    Q_OBJECT
public:
    explicit SensorManager(QObject *parent = 0);

    QTimer *timer;

public slots:
    void loadSensorLibraries();

    void timerSlot();
private:
    typedef QMultiMap<QString,AbstractSensor*>PluginsLoadedMap;

    PluginsLoadedMap m_pluginsLoaded;
};

#endif // SENSORMANAGER_H
