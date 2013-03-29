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
    QString      webRequestAddress;
    QString      siteId;
    QString      userId;
    QString      userPassword;

public:
    explicit SettingsManager(QObject *parent = 0);
    void getMacAdresses();
    void obtainWebRequestAddress();
    void obtainSiteId();
    void obtainUserId();
    void obtainUserPassword();
    QSettings* getSettings();
    QString getWebRequestAddress();
    QString getSiteId();
    QString getUserId();
    QString getUserPassword();
    
signals:
    
public slots:
    
};

typedef CBluuSingleton<SettingsManager>     CBluuSettingsManager;

#endif // SETTINGSMANAGER_H
