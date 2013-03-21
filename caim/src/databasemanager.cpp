#include "databasemanager.h"
#include "webrequest.h"
#include "databaseexception.h"
#include "debug.h"
#include "parser.h"
#include <QDir>
#include <QSqlQuery>
#include <QSqlError>
#include <QVariant>
#include <QDebug>
/**
 * @brief DatabaseManager::DatabaseManager
 * @param parent
 */
DatabaseManager::DatabaseManager(QObject *parent)
               : QObject(parent)
{
    debugMessage();

    connect(this, SIGNAL(sendSignal(QSqlQuery*)), SLOT(sendSlot(QSqlQuery*)));
    connect(this, SIGNAL(networkSendSignal(QString*)), CBluuWebRequest::Instance(), SLOT(sendDataToServer(QString*)));
    connect(CBluuWebRequest::Instance(), SIGNAL(networkReplyDatabaseSendSignal(QNetworkReply*)), this, SLOT(networkReplySlot(QNetworkReply*)));
}

/**
 * @brief DatabaseManager::openDB
 * @return
 */
bool DatabaseManager::openDB()
{
    debugMessage();

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
    debugMessage();

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
    debugMessage();

    bool    result = false;

    if(true == database.isOpen())
    {
        if(true == database.tables().contains("packet"))
        {
            QString     str = QString("insert into packet values (NULL, %1").arg(*packet);
            QSqlQuery   query(str);

            if(false == query.exec())
                throw DatabaseException(DatabaseException::databaseInsertException, query.lastError());
        }
        else
            throw DatabaseException(DatabaseException::databaseTableException);
    }
    else
        throw DatabaseException(DatabaseException::databaseOpenException);

    return result;
}

/**
 * @brief DatabaseManager::removePacket
 * @param id
 * @return
 */
void DatabaseManager::removePacket(const quint64 &id)
{
    debugMessage();

    if(true == database.isOpen())
    {
        if(true == database.tables().contains("packet"))
        {
            QSqlQuery   query(QString("delete from packet where id = %1").arg(id));

            if(false == query.exec())
                throw DatabaseException(DatabaseException::databaseRemoveException, query.lastError());
        }
        else
            throw DatabaseException(DatabaseException::databaseTableException);
    }
    else
        throw DatabaseException(DatabaseException::databaseOpenException);
}

/**
 * @brief DatabaseManager::createTable
 */
void DatabaseManager::createTable()
{
    debugMessage();

    if(true == database.isOpen())
    {
        if(false == database.tables().contains("packet"))
        {
            QSqlQuery   query(database);

            if(false == query.exec("create table packet (id integer primary key, content varchar)"))
                throw DatabaseException(DatabaseException::databaseTableException, query.lastError());
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
    debugMessage();

    if(true == database.isOpen())
    {
        if(true == database.tables().contains("packet"))
        {
            QString     str = QString("insert into packet (content) values ('%1')").arg(*packet);
            QSqlQuery   query(str);

            if(false == query.exec())
                throw DatabaseException(DatabaseException::databaseInsertException, query.lastError());
            else
                emit databasePacketStoredSignal();
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
void DatabaseManager::databaseSendPacketsSlot(QDateTime time)
{
    debugMessage();

    if(true == database.isOpen())
    {
        if(true == database.tables().contains("packet"))
        {
            QString     str = QString("select * from packet");
            QSqlQuery   query(str);

            if(true == query.exec())
            {
                qr = QSqlQuery(query);
                removeOutdated(time);
                qr.first();
                emit sendSignal(&qr);
            }
            else
                throw DatabaseException(DatabaseException::databaseSelectException, query.lastError());
        }
        else
            throw DatabaseException(DatabaseException::databaseTableException);
    }
    else
        throw DatabaseException(DatabaseException::databaseOpenException);
}

/**
 * @brief DatabaseManager::networkReplySlot
 * @param reply
 */
void DatabaseManager::networkReplySlot(QNetworkReply* reply)
{
    debugMessage();

    if(QNetworkReply::NoError == reply->error())
    {
        quint64     id = qr.value(0).toInt();

        removePacket(id);
        emit sendSignal(&qr);
    }
}

/**
 * @brief DatabaseManager::sendSlot
 * @param query
 */
void DatabaseManager::sendSlot(QSqlQuery* query)
{
    debugMessage();

    if(NULL != query)
    {
        if(true == query->next())
        {
            QString     packet = query->value(1).toString();
            emit networkSendSignal(&packet);
        }
        else
            emit databaseSendPacketsSignal();
    }
}

/**
 * @brief DatabaseManager::removeOutdated
 * @param time
 */
void DatabaseManager::removeOutdated(const QDateTime &time)
{
    debugMessage();

    QJson::Parser   parser;

    while(true == qr.next())
    {
        qulonglong    id = qr.value(0).toULongLong();
        QString       packet = qr.value(1).toString();
        QVariantMap   map = parser.parse(packet.toUtf8()).toMap();
        QDateTime     dateTime = QDateTime::fromString(map["timestamp"].toString(), "yyyy-MM-dd hh:mm:ss");

        if(14 <= dateTime.daysTo(time))
            removePacket(id);
    }
}
