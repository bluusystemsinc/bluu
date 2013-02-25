#ifndef DATAMANAGER_H
#define DATAMANAGER_H

#include <QObject>
#include <QStringList>
#include <QMutex>
#include "singleton.h"

class DataManager : public QObject
{
    Q_OBJECT

protected:
    QStringList        packets;
    QMutex             mutex;

public:
    explicit DataManager(QObject *parent = 0);
    void processData(QByteArray* data);
    QMutex* getMutex();
    QStringList* getPackets();
    
signals:
    
public slots:
    void packedReadySlot(QByteArray json);
};

typedef CBluuSingleton<DataManager>     CBluuDataManager;

#endif // DATAMANAGER_H
