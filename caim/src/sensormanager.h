#ifndef SENSORMANAGER_H
#define SENSORMANAGER_H

#include <QMap>
#include <QObject>

class QThread;
class AbstractSensor;

class SensorManager : public QObject
{
    Q_OBJECT
public:
    explicit SensorManager(QObject *parent = 0);

public slots:
    void loadSensorLibraries();

protected slots:
    void sensorUnplugged();
    void readData();
private:
    typedef QMap<QThread*,AbstractSensor*>PluginsLoadedMap;

    PluginsLoadedMap m_pluginsLoaded;
};

#endif // SENSORMANAGER_H
