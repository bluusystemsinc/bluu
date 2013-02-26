#include "databaseexception.h"

/**
 * @brief DatabaseException::DatabaseException
 * @param e
 */
DatabaseException::DatabaseException(const EDatabaseException& e)
                 : Exception()
{
    type = e;
}

/**
 * @brief DatabaseException::DatabaseException
 * @param e
 * @param value
 */
DatabaseException::DatabaseException(const DatabaseException::EDatabaseException &e, const QSqlError &value)
{
    type = e;
    error = value;
    databaseText = error.databaseText();
    driverText = error.driverText();
    text = error.text();
}

/**
 * @brief DatabaseException::what
 * @return
 */
const char *DatabaseException::what()
{
    return "Database Exception";
}

/**
 * @brief DatabaseException::setSqlError
 * @param value
 */
void DatabaseException::setSqlError(const QSqlError& value)
{
}
