#ifndef SETTINGSMANAGER_H
#define SETTINGSMANAGER_H

#include <QObject>
#include "singleton.h"

/**
 * @brief The SettingsManager class
 */
class SettingsManager : public QObject
{
    Q_OBJECT

public:
    explicit SettingsManager(QObject *parent = 0);
    
signals:
    
public slots:
    
};

typedef CBluuSingleton<SettingsManager>     CBluuSettingsManager;

#endif // SETTINGSMANAGER_H
