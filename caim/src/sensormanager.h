#ifndef SENSORMANAGER_H
#define SENSORMANAGER_H

#include <QObject>

class SensorManager : public QObject
{
    Q_OBJECT
public:
    explicit SensorManager(QObject *parent = 0);

public slots:
    void loadSensorLibraries();
};

#endif // SENSORMANAGER_H
