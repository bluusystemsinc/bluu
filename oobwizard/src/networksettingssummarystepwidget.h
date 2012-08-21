#ifndef NETWORKSETTINGSSUMMARYSTEPWIDGET_H
#define NETWORKSETTINGSSUMMARYSTEPWIDGET_H

#include <QWidget>
#include <ui_networkSettingsSummaryStep.h>

class NetworkSettingsSummaryStepWidget : public QWidget,
        private Ui::NetworkSettingsSummaryStepWidget
{
    Q_OBJECT
public:
    explicit NetworkSettingsSummaryStepWidget(QWidget *parent = 0);
    
signals:
    void back();
    void next();
};

#endif // NETWORKSETTINGSSUMMARYSTEPWIDGET_H
