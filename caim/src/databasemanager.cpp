#include "databasemanager.h"
#include "webrequest.h"
#include "databaseexception.h"
#include <QDir>
#include <QSqlQuery>
#include <QSqlError>
#include <QVariant>

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
void DatabaseManager::createTable()
{
    if(true == database.isOpen())
    {
        if(false == database.tables().contains("packet"))
        {
            QSqlQuery   query("create table packet (id integer primary key, content varchar)");

            if(false == query.exec())
                throw DatabaseException(DatabaseException::databaseTableException);
        }
    }
    else
        throw DatabaseException(DatabaseException::databaseOpenException);
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
                throw DatabaseException(DatabaseException::databaseInsertException, query.lastError());
        }
        else
            throw DatabaseException(DatabaseException::databaseTableException);
    }
    else
        throw DatabaseException(DatabaseException::databaseOpenException);
}

/**
 * @brief DatabaseManager::databaseSendPacketSlot
 */
void DatabaseManager::databaseSendPacketSlot()
{
    if(true == database.isOpen())
    {
        if(true == database.tables().contains("packet"))
        {

            QString     str = QString("select * from packet");
            QSqlQuery   query(str);

            if(true == query.exec())
            {
                while(true == query.next())
                {
                    /*
                    quint64     id = query.value(0).toInt();
                    QString     packet = query.value(1).toString();

                    connect(this, SIGNAL(networkSendSignal(QString)), CBluuWebRequest::Instance(),
                                  SLOT(sendDataToServer(QString)), Qt::BlockingQueuedConnection);
                    emit networkSendSignal(packet);
                    */
                }
            }
        }
        else
            throw 0;
    }
    else
        throw 0;
}

/**
 * @brief DatabaseManager::networkReplySlot
 * @param reply
 */
void DatabaseManager::networkReplySlot(QNetworkReply* reply)
{
    // disconnect(this, SIGNAL(networkSendSignal(QString)), CBluuWebRequest::Instance(), SLOT(sendDataToServer(QString)));

    if(QNetworkReply::NoError == reply->error())
        {
            // debugMessageThread("Packet send OK");
            // result = true;
            // emit sendSignal();
        }
        else
        {
            throw DatabaseException();
            // debugMessageThread("Packed send FAIL, store in database");
            // emit databaseStorePacketSignal(&*it);
            // result = CBluuDatabaseManager::Instance()->writePacket(&*it);
        }

    /*
        if(true == result)
        {
            QStringList*  packets = CBluuDataManager::Instance()->getPackets();
            QMutexLocker    locker(CBluuDataManager::Instance()->getMutex());

            packets->erase(it);
        }
        */
}
