#ifndef OOBWIZARDWIDGET_H
#define OOBWIZARDWIDGET_H

#include <QWidget>
#include "ui_oobwizardwidget.h"

class QState;
class QFinalState;
class QStateMachine;
class WizardContext;
class WelcomeStepWidget;
class ControllerStepWidget;
class ConnectionTypeStepWidget;
class NetworkSettingsStepWidget;
class WirelessSettingsStepWidget;
class SystemConfigurationStepWidget;
class EndUserRegistrationStepWidget;
class endUserRegistrationSummaryStep;
class NetworkSettingsSummaryStepWidget;
class WorkflowFinishedStepWidget;

class OobWizardWidget : public QWidget, private Ui::OobWizardWidget
{
    Q_OBJECT

public:
    explicit OobWizardWidget(QWidget *parent = 0);

protected:
    QState* createState(int index, const QString &title);
    void setupStateMachine();

private:
    enum {
        WelcomeStepWidgetIndex = 0,
        ControllerStepWidgetIndex,
        SystemConfigurationStepWidgetIndex,
        ConnectionTypeStepWidgetIndex,
        WirelessSettingsStepWidgetIndex,
        NetworkSettingsStepWidgetIndex,
        NetworkSettingsSummaryStepWidgetIndex,
        EndUserRegistrationStepWidgetIndex,
        EndUserRegistrationSummaryStepWidgetIndex,
        WorkflowFisnishedStepWidgetIndex
    };

    QStateMachine *m_stateMachine;
    QState *m_welcomeState, *m_endUserRegistrationState,*m_endUserRegistrationSummaryState,
            *m_controllerState,
            *m_systemConfigurationState, *m_connectionTypeState,
            *m_wirelessSettingsState, *m_networkSettingsState,
            *m_networkSettingsSummaryState,*m_workflowFisnishedState;

    QState  *m_networkSettingsStateL, *m_networkSettingsSummaryStateL,
    *m_endUserRegistrationStateL,*m_endUserRegistrationSummaryStateL;

    QState  *m_networkSettingsStateRL, *m_networkSettingsSummaryStateRL;


    QState  *m_endUserRegistrationStateR,*m_endUserRegistrationSummaryStateR,
            *m_systemConfigurationStateR, *m_connectionTypeStateR,
            *m_wirelessSettingsStateR, *m_networkSettingsStateR,
            *m_networkSettingsSummaryStateR;

    WelcomeStepWidget *m_welcomeStepWidget;
    ControllerStepWidget *m_controllerStepWidget;
    SystemConfigurationStepWidget *m_systemConfigurationStepWidget;
    ConnectionTypeStepWidget *m_connectionTypeStepWidget;
    WirelessSettingsStepWidget *m_wirelessSettingsStepWidget;
    NetworkSettingsStepWidget *m_networkSettingsStepWidget;
    NetworkSettingsSummaryStepWidget *m_networkSettingsSummaryStepWidget;
    EndUserRegistrationStepWidget *m_endUserRegistrationStepWidget;
    endUserRegistrationSummaryStep *m_endUserRegistrationSummaryStepWidget;
    WorkflowFinishedStepWidget *m_workflowFinidshedStepWidget;
};

#endif // OOBWIZARDWIDGET_H
