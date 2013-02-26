#ifndef TASK_H
#define TASK_H

#include <QObject>
#include <QDateTime>

/**
 * @brief The Task class
 */
class Task : public QObject
{
    Q_OBJECT

public:
    enum ETaskType
    {
        taskOnce,
        taskRepeat,
        taskUnknown,
    };

protected:
    ETaskType   type;

public:
    explicit Task(QObject *parent = 0);
    virtual void processTask(const QDateTime& dateTime) = 0;
    ETaskType getType();
    void setType(const ETaskType& t);
    
signals:
    
public slots:
    
};

#endif // TASK_H
