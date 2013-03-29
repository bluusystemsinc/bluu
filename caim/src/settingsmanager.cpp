#include "settingsmanager.h"
#include <QNetworkInterface>
#include <QDebug>
#include <QTcpSocket>

QTcpSocket  a;

/**
 * @brief SettingsManager::SettingsManager
 * @param parent
 */
SettingsManager::SettingsManager(QObject *parent)
               : QObject(parent)
{
    settings = new QSettings("Bluu", "caim deamon");
    getMacAdresses();
    obtainWebRequestAddress();
}

/**
 * @brief SettingsManager::getMacAdresses
 */
void SettingsManager::getMacAdresses()
{
    QList<QNetworkInterface>    interfaces = QNetworkInterface::allInterfaces();

    if(0 < interfaces.size())
    {
        foreach(QNetworkInterface interface, interfaces)
        {
            if(0 == (QNetworkInterface::IsLoopBack & interface.flags()))
            {
                macAdresses.append(interface.hardwareAddress());

                qDebug() << interface.humanReadableName();
                qDebug() << interface.name();

                if(0 != (QNetworkInterface::IsUp & interface.flags()))
                    qDebug() << "QNetworkInterface::IsUp";

                if(0 != (QNetworkInterface::IsRunning & interface.flags()))
                {
                    qDebug() << "QNetworkInterface::IsRunning";
                    settings->setValue("mac", interface.hardwareAddress());
                }

                if(0 != (QNetworkInterface::CanBroadcast & interface.flags()))
                    qDebug() << "QNetworkInterface::CanBroadcast";

                if(0 != (QNetworkInterface::CanMulticast & interface.flags()))
                    qDebug() << "QNetworkInterface::CanMulticast";
            }
        }
    }
    else
        throw 0;
}

/**
 * @brief SettingsManager::obtainWebRequestAddress
 */
void SettingsManager::obtainWebRequestAddress()
{
    webRequestAddress = QString(qgetenv("BLUU_WEB_REQUEST"));
}

/**
 * @brief SettingsManager::obtainSiteId
 */
void SettingsManager::obtainSiteId()
{
    siteId = QString(qgetenv("BLUU_SITE_ID"));
}

/**
 * @brief SettingsManager::obtainUserId
 */
void SettingsManager::obtainUserId()
{
    userId = QString(qgetenv("BLUU_USER_ID"));
}

/**
 * @brief SettingsManager::obtainUserPassword
 */
void SettingsManager::obtainUserPassword()
{
    userPassword = QString(qgetenv("BLUU_USER_PASS"));
}

/**
 * @brief SettingsManager::getWebRequestAddress
 */
QString SettingsManager::getWebRequestAddress()
{
    return webRequestAddress;
}

/**
 * @brief SettingsManager::getSiteId
 * @return
 */
QString SettingsManager::getSiteId()
{
    return siteId;
}

/**
 * @brief SettingsManager::getUserId
 * @return
 */
QString SettingsManager::getUserId()
{
    return userId;
}

/**
 * @brief SettingsManager::getUserPassword
 * @return
 */
QString SettingsManager::getUserPassword()
{
    return userPassword;
}

/**
 * @brief SettingsManager::getSettings
 * @return
 */
QSettings* SettingsManager::getSettings()
{
    return settings;
}
