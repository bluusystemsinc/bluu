#ifndef ABSTRACTSENSOR_H
#define ABSTRACTSENSOR_H

#include <QObject>

class QTextStream;

class AbstractSensor : public QObject
{
    Q_OBJECT

public slots:
    // Class members initialization go in this function. It will be called in
    // sensor thread
    virtual bool plug() = 0;

    // This function will serialize the data in json format to send to
    // the server
    virtual void serialize(QTextStream *stream) = 0;
    virtual void serialize(QByteArray* stream) = 0;

protected:
    AbstractSensor(QObject *parent = 0) : QObject(parent) {}

signals:
    // For notify Caim about new data available
    void dataAvailable();
    void plugged();
    void unplugged();
};

typedef QList<AbstractSensor*> AbstractSensorList;
typedef int MajorVersion, MinorVersion;

struct VersionInfo
{
    QString pluginName;
    int majorVersion;
    int minorVersion;
};

extern "C" AbstractSensorList instances();

extern "C" VersionInfo version();

typedef VersionInfo(*FNVersionPtr)();
typedef AbstractSensorList(*FNInstancesPtr)();

// Version info MACRO define it once per plugin
#define addVersionInfo() extern "C" VersionInfo version() { \
    VersionInfo r; \
    r.pluginName = PLUGIN_NAME; \
    r.majorVersion = MAJOR_VERSION; \
    r.minorVersion = MINOR_VERSION; \
    return r; \
}

#endif // ABSTRACTSENSOR_H
