#include "task.h"

/**
 * @brief Task::Task
 * @param parent
 */
Task::Task(QObject *parent)
    : QObject(parent)
{
    type = taskUnknown;
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
