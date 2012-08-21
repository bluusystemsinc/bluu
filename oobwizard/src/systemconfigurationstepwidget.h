#ifndef SYSTEMCONFIGURATIONSTEPWIDGET_H
#define SYSTEMCONFIGURATIONSTEPWIDGET_H

#include <QWidget>
#include <ui_systemConfigurationStep.h>

class QButtonGroup;

class SystemConfigurationStepWidget : public QWidget,
        private Ui::SystemConfigurationStepWidget
{
    Q_OBJECT
public:
    explicit SystemConfigurationStepWidget(QWidget *parent = 0);

signals:
    void back();
    void networkConfiguration();
    void endUserRegistration();

protected slots:
    void on_nextButton_clicked();

private:
    enum {
        NetworkConfiguration = 0,
        EndUserRegistration
    };

    QButtonGroup *m_buttonGroup;
};

#endif // SYSTEMCONFIGURATIONSTEPWIDGET_H
