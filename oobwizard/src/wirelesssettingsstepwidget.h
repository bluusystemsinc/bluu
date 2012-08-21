#ifndef WIRELESSSETTINGSSTEPWIDGET_H
#define WIRELESSSETTINGSSTEPWIDGET_H

#include <QWidget>
#include <ui_wirelessSettingsStep.h>

class WirelessSettingsStepWidget : public QWidget,
        private Ui::WirelessSettingsStepWidget
{
    Q_OBJECT
public:
    explicit WirelessSettingsStepWidget(QWidget *parent = 0);
    
signals:
    void back();
    void next();
};

#endif // WIRELESSSETTINGSSTEPWIDGET_H
