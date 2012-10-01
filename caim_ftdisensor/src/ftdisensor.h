#ifndef FTDISENSOR_H
#define FTDISENSOR_H

#include <abstractsensor.h>
#include <QTimer>

class FtdiSensor : public AbstractSensor
{
    Q_OBJECT
public:

    explicit FtdiSensor(int timeout, QObject *parent = 0);
    FtdiSensor(QObject *parent = 0);

    QTimer *timer;

    Q_INVOKABLE virtual void plug();

    virtual void serialize(QTextStream *stream);
public slots:
    void timerSlot();
};

#endif // FTDISENSOR_H
