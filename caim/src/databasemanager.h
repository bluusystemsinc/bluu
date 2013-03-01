#ifndef DATABASEMANAGER_H
#define DATABASEMANAGER_H

#include <QObject>
#include <QSqlDatabase>
#include <QSqlQuery>
#include <QNetworkReply>
#include "singleton.h"

class DatabaseManager : public QObject
{
    Q_OBJECT

protected:
    QSqlDatabase    database;
    QSqlQuery       qr;

public:
    explicit DatabaseManager(QObject *parent = 0);
    bool openDB();
    bool deleteDB();
    bool writePacket(QString* packet);
    void removePacket(const quint64& id);
    void createTable();

signals:
    void networkSendSignal(QString* data);
    void databasePacketStoredSignal();
    void databaseSendPacketsSignal();
    void sendSignal(QSqlQuery* query);
    
public slots:
    void databaseStorePacketSlot(QString* packet);
    void databaseSendPacketsSlot();
    void networkReplySlot(QNetworkReply* reply);
    void sendSlot(QSqlQuery* query);
};

typedef CBluuSingleton<DatabaseManager>     CBluuDatabaseManager;

#endif // DATABASEMANAGER_H
