#ifndef DATABASEEXCEPTION_H
#define DATABASEEXCEPTION_H

#include "exception.h"
#include <QString>
#include <QSqlError>

class DatabaseException : public Exception
{
public:
    enum EDatabaseException
    {
        databaseOpenException,
        databaseTableException,
        databaseInsertException,
        databaseSelectException,
        databaseRemoveException,
        databaseUnknowException,
    };

protected:
    EDatabaseException  type;
    QSqlError   error;
    QString     databaseText;
    QString     driverText;
    QString     text;

public:
    explicit DatabaseException(const EDatabaseException& e = databaseUnknowException);
    explicit DatabaseException(const EDatabaseException& e, const QSqlError& value);
    virtual const char* what();
    void setSqlError(const QSqlError& value);
};

#endif // DATABASEEXCEPTION_H
