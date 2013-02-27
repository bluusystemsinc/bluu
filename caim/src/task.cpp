#include "task.h"

/**
 * @brief Task::Task
 * @param parent
 */
Task::Task(QObject *parent)
    : QObject(parent)
{
    type = taskUnknown;
    valid = false;
    busy = false;
    initial = true;
}

/**
 * @brief Task::validateTask
 * @param dateTime
 * @return
 */
bool Task::validateTask(const QDateTime& dateTime)
{
    currentDateTime = dateTime;

    return false;
}

/**
 * @brief Task::getType
 * @return
 */
Task::ETaskType Task::getType()
{
    return type;
}

/**
 * @brief Task::setType
 * @param t
 */
void Task::setType(const Task::ETaskType &t)
{
    type = t;
}
