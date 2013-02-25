#ifndef DATABASEMANAGER_H
#define DATABASEMANAGER_H

#include <QObject>
#include <QSqlDatabase>
#include "singleton.h"

class DatabaseManager : public QObject
{
    Q_OBJECT

protected:
    QSqlDatabase    database;

public:
    explicit DatabaseManager(QObject *parent = 0);
    bool openDB();
    bool deleteDB();
    bool writePacket(QString* packet);
    bool createTable();

signals:
    
public slots:
    void databaseStorePacketSlot(QString* packet);
};

typedef CBluuSingleton<DatabaseManager>     CBluuDatabaseManager;

#endif // DATABASEMANAGER_H
