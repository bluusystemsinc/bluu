#ifndef BTDEVICE_H
#define BTDEVICE_H

#include <QObject>

/**
 * @brief The BtDevice class
 */
class BtDevice : public QObject
{
    Q_OBJECT
public:
    explicit BtDevice(QObject *parent = 0);
    
signals:
    
public slots:
    
};

#endif // BTDEVICE_H
