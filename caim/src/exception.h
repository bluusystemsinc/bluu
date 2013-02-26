#ifndef EXCEPTION_H
#define EXCEPTION_H

#include <exception>

/**
 * @brief The Exception class
 */
class Exception//  : public std::exception
{
public:
    explicit Exception();
    // virtual const char* what();
};

#endif // EXCEPTION_H
