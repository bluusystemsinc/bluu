#ifndef CONNECTIONTYPESTEPWIDGET_H
#define CONNECTIONTYPESTEPWIDGET_H

#include <QWidget>
#include <ui_connectionTypeStep.h>

class QButtonGroup;

class ConnectionTypeStepWidget : public QWidget,
        private Ui::ConnectionTypeStepWidget
{
    Q_OBJECT
public:
    explicit ConnectionTypeStepWidget(QWidget *parent = 0);

signals:
    void back();
    void wiredConnection();
    void wirelessConnection();

protected slots:
    void on_nextButton_clicked();

private:
    enum {
        WiredConnection = 0,
        WirelessConnection
    };

    QButtonGroup *m_buttonGroup;
};

#endif // CONNECTIONTYPESTEPWIDGET_H
