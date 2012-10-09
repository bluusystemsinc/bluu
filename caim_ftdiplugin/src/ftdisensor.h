#ifndef FTDISENSOR_H
#define FTDISENSOR_H

#include <abstractsensor.h>

#ifdef CAIM_FTDISENSOR_USE_FILE
class QFile;
#else
class FtdiDevice;
#endif


class FtdiSensor : public AbstractSensor
{
    Q_OBJECT

public:
    explicit FtdiSensor(QObject *parent = 0);

public slots:
    virtual bool plug();
    virtual void serialize(QTextStream *stream);

private:
#ifdef CAIM_FTDISENSOR_USE_FILE
    QFile *m_file;
#else
    FtdiDevice *m_device;
#endif
};

#endif // FTDISENSOR_H
