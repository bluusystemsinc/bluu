#ifndef NETWORKSETTINGSSUMMARYSTEPWIDGET_H
#define NETWORKSETTINGSSUMMARYSTEPWIDGET_H

#include <QWidget>
#include <ui_networkSettingsSummaryStep.h>
#include "networksettingsstepwidget.h"

class NetworkSettingsSummaryStepWidget : public QWidget,
        private Ui::NetworkSettingsSummaryStepWidget
{
    Q_OBJECT
public:
    explicit NetworkSettingsSummaryStepWidget(QWidget *parent = 0);
    
signals:
    void back();
    void next();
public slots:
    void removeConnectionScript();
    void testConnection();
    void testRouter(int exitCode);
    void testInternet(int exitCode);
    void testBluuServer(int exitCode);
};

#endif // NETWORKSETTINGSSUMMARYSTEPWIDGET_H
