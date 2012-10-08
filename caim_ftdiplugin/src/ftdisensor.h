#ifndef FTDISENSOR_H
#define FTDISENSOR_H

#include <abstractsensor.h>

#ifdef CAIM_FTDISENSOR_USE_FILE
class QFile;
#endif


class FtdiSensor : public AbstractSensor
{
    Q_OBJECT

public:
    explicit FtdiSensor(QObject *parent = 0);

public slots:
    virtual bool plug();
    virtual void serialize(QTextStream *stream);

#ifdef CAIM_FTDISENSOR_USE_FILE
private:
    QFile *m_file;
#endif
};

#endif // FTDISENSOR_H
