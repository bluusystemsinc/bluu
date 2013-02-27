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
    QDateTime   currentDateTime;
    QDateTime   previousDateTime;
    ETaskType   type;
    bool        valid;
    bool        busy;
    bool        initial;

public:
    explicit Task(QObject *parent = 0);
    virtual bool validateTask(const QDateTime& dateTime);
    ETaskType getType();
    void setType(const ETaskType& t);
    
signals:
    
public slots:
    virtual void processTask() = 0;
};

#endif // TASK_H
