#ifndef DATABASEMANAGER_H
#define DATABASEMANAGER_H

#include <QObject>
#include <QSqlDatabase>
#include <QNetworkReply>
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
    void networkSendSignal(QString data);
    
public slots:
    void databaseStorePacketSlot(QString* packet);
    void databaseSendPacketSlot();
    void networkReplySlot(QNetworkReply* reply);
};

typedef CBluuSingleton<DatabaseManager>     CBluuDatabaseManager;

#endif // DATABASEMANAGER_H
