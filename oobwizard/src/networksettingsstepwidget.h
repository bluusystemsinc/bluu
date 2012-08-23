#ifndef NETWORKSETTINGSSTEPWIDGET_H
#define NETWORKSETTINGSSTEPWIDGET_H

#include <QWidget>
#include <ui_networkSettingsStep.h>

class NetworkSettingsStepWidget : public QWidget,
        private Ui::NetworkSettingsStepWidget
{
    Q_OBJECT
public:
    explicit NetworkSettingsStepWidget(QWidget *parent = 0);
    
signals:
    void back();
    void next();

};

#endif // NETWORKSETTINGSSTEPWIDGET_H
