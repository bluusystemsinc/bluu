#ifndef SETTINGSMANAGER_H
#define SETTINGSMANAGER_H

#include <QObject>
#include <QSettings>
#include <QStringList>
#include "singleton.h"

/**
 * @brief The SettingsManager class
 */
class SettingsManager : public QObject
{
    Q_OBJECT

protected:
    QSettings*   settings;
    QStringList  macAdresses;

public:
    explicit SettingsManager(QObject *parent = 0);
    void getMacAdresses();
    QSettings* getSettings();
    
signals:
    
public slots:
    
};

typedef CBluuSingleton<SettingsManager>     CBluuSettingsManager;

#endif // SETTINGSMANAGER_H
