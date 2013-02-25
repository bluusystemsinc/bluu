#include "databasemanager.h"
#include <QDir>
#include <QSqlQuery>
#include <QSqlError>

/**
 * @brief DatabaseManager::DatabaseManager
 * @param parent
 */
DatabaseManager::DatabaseManager(QObject *parent)
               : QObject(parent)
{
}

/**
 * @brief DatabaseManager::openDB
 * @return
 */
bool DatabaseManager::openDB()
{
    database = QSqlDatabase::addDatabase("QSQLITE");

#ifdef Q_OS_LINUX
    QString path(QDir::home().path());
    path.append(QDir::separator()).append("my.db.sqlite");
    path = QDir::toNativeSeparators(path);
    database.setDatabaseName(path);
#else
    db.setDatabaseName("my.db.sqlite");
#endif

    return database.open();
}

/**
 * @brief DatabaseManager::deleteDB
 * @return
 */
bool DatabaseManager::deleteDB()
{
    // Close database
    database.close();

#ifdef Q_OS_LINUX
    // NOTE: We have to store database file into user home folder in Linux
    QString path(QDir::home().path());
    path.append(QDir::separator()).append("my.db.sqlite");
    path = QDir::toNativeSeparators(path);
    return QFile::remove(path);
#else

    // Remove created database binary file
    return QFile::remove("my.db.sqlite");
#endif
}

/**
 * @brief DatabaseManager::writePacket
 * @param packet
 */
bool DatabaseManager::writePacket(QString* packet)
{
    bool    result = false;

    if(true == database.isOpen())
    {
        if(true == database.tables().contains("packet"))
        {
            QString     str = QString("insert into packet values (NULL, %1").arg(*packet);
            QSqlQuery   query(str);

            result = query.exec();
        }
    }

    return result;
}

/**
 * @brief DatabaseManager::createTable
 */
bool DatabaseManager::createTable()
{
    if(true == database.isOpen())
    {
        if(false == database.tables().contains("packet"))
        {
            QSqlQuery   query("create table packet (id integer primary key, content varchar)");

            if(false == query.exec())
                throw 0;
        }
    }
    else
        throw 0;

    return false;
}

/**
 * @brief DatabaseManager::databaseStorePacketSlot
 * @param packet
 */
void DatabaseManager::databaseStorePacketSlot(QString* packet)
{
    bool    result = false;

    if(true == database.isOpen())
    {
        if(true == database.tables().contains("packet"))
        {
            QString     str = QString("insert into packet (content) values ('%1')").arg(*packet);
            QSqlQuery   query(str);

            result = query.exec();

            if(false == result)
            {
                QSqlError   error = query.lastError();
                QString     textDatabase = error.databaseText();
                QString     textDriver = error.driverText();
                QString     text = error.text();
                throw 0;
            }
        }
        else
            throw 0;
    }
    else
        throw 0;
}
