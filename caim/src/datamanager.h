#ifndef DATAMANAGER_H
#define DATAMANAGER_H

#include <QObject>
#include "singleton.h"

class DataManager : public QObject
{
    Q_OBJECT

public:
    explicit DataManager(QObject *parent = 0);
    void processData(QByteArray* data);
    
signals:
    
public slots:
    void packedReadySlot(QByteArray json);
};

typedef CBluuSingleton<DataManager>     CBluuDataManager;

#endif // DATAMANAGER_H
