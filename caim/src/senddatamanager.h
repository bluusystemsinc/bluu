#ifndef SENDDATAMANAGER_H
#define SENDDATAMANAGER_H

#include <QHash>
#include <QObject>

class SendDataManager : public QObject
{
    Q_OBJECT

public:
    SendDataManager* instance();

public slots:
    void sendData(const QByteArray &data);

protected:
    explicit SendDataManager(QObject *parent = 0);
};

#endif // SENDDATAMANAGER_H
