#include "oobwizardwidget.h"
#include "ui_oobwizardwidget.h"

#include <QStateMachine>
#include <QFinalState>

#include "wizardcontext.h"
#include "welcomestepwidget.h"
#include "controllerstepwidget.h"
#include "connectiontypestepwidget.h"
#include "networksettingsstepwidget.h"
#include "wirelesssettingsstepwidget.h"
#include "systemconfigurationstepwidget.h"
#include "enduserregistrationstepwidget.h"
#include "networksettingssummarystepwidget.h"
#include "workflowfinishedstepwidget.h"
#include "enduserregistrationsummarystep.h"

OobWizardWidget::OobWizardWidget(QWidget *parent) :
    QWidget(parent)
{
    setupUi(this);

    m_stateMachine = new QStateMachine(this);

    m_welcomeStepWidget = new WelcomeStepWidget(this);
    stackedWidget->insertWidget(WelcomeStepWidgetIndex, m_welcomeStepWidget);
    m_controllerStepWidget = new ControllerStepWidget(this);
    stackedWidget->insertWidget(ControllerStepWidgetIndex,
                                m_controllerStepWidget);
    m_systemConfigurationStepWidget = new SystemConfigurationStepWidget(this);
    stackedWidget->insertWidget(SystemConfigurationStepWidgetIndex,
                                m_systemConfigurationStepWidget);
    m_connectionTypeStepWidget = new ConnectionTypeStepWidget(this);
    stackedWidget->insertWidget(ConnectionTypeStepWidgetIndex,
                                m_connectionTypeStepWidget);
    m_wirelessSettingsStepWidget = new WirelessSettingsStepWidget(this);
    stackedWidget->insertWidget(WirelessSettingsStepWidgetIndex,
                                m_wirelessSettingsStepWidget);

    m_networkSettingsStepWidget = new NetworkSettingsStepWidget(this);
    stackedWidget->insertWidget(NetworkSettingsStepWidgetIndex,
                                m_networkSettingsStepWidget);

    m_networkSettingsSummaryStepWidget = new NetworkSettingsSummaryStepWidget(this);
    stackedWidget->insertWidget(NetworkSettingsSummaryStepWidgetIndex, m_networkSettingsSummaryStepWidget);

    m_endUserRegistrationSummaryStepWidget = new endUserRegistrationSummaryStep(this);
    stackedWidget->insertWidget(EndUserRegistrationSummaryStepWidgetIndex,
                                m_endUserRegistrationSummaryStepWidget);

    m_endUserRegistrationStepWidget = new EndUserRegistrationStepWidget(m_endUserRegistrationSummaryStepWidget,this);
    stackedWidget->insertWidget(EndUserRegistrationStepWidgetIndex,
                                m_endUserRegistrationStepWidget);

    m_workflowFinidshedStepWidget = new WorkflowFinishedStepWidget(this);
    stackedWidget->insertWidget(WorkflowFisnishedStepWidgetIndex, m_workflowFinidshedStepWidget);

    setupStateMachine();
}

QState *OobWizardWidget::createState(int index, const QString &title)
{
    QState *state = new QState(m_stateMachine);

    state->assignProperty(stackedWidget, "currentIndex", index);
    state->assignProperty(titleLabel, "text", title);
    return state;
}

void OobWizardWidget::setupStateMachine()
{
    m_welcomeState = createState(WelcomeStepWidgetIndex, "Bluu Systems");
    m_controllerState = createState(ControllerStepWidgetIndex,
                                    "Bluu Systems Controller");
    m_systemConfigurationState = createState(SystemConfigurationStepWidgetIndex,
                                             "System Configuration");
    m_connectionTypeState = createState(ConnectionTypeStepWidgetIndex,
                                        "System Connection Type");
    m_wirelessSettingsState = createState(WirelessSettingsStepWidgetIndex,
                                          "Wireless Settings");
    m_networkSettingsState = createState(NetworkSettingsStepWidgetIndex,
                                         "Network Settings");
    m_networkSettingsStateL = createState(NetworkSettingsStepWidgetIndex,
                                         "Network Settings");


    m_networkSettingsSummaryStateL = createState(NetworkSettingsSummaryStepWidgetIndex,
                                                 "Network Configuration Summary");
    m_endUserRegistrationStateL    = createState(EndUserRegistrationStepWidgetIndex,
                                                 "End User Registration");
    m_endUserRegistrationSummaryStateL =  createState(EndUserRegistrationSummaryStepWidgetIndex,
                                                      "End User Registration Summary");

    m_networkSettingsSummaryState = createState(NetworkSettingsSummaryStepWidgetIndex,
                                         "Network Configuration Summary");
    m_endUserRegistrationState = createState(EndUserRegistrationStepWidgetIndex,
                                             "End User Registration");
    m_endUserRegistrationSummaryState = createState(EndUserRegistrationSummaryStepWidgetIndex,
                                             "End User Registration Summary");
    m_workflowFisnishedState  = createState(WorkflowFisnishedStepWidgetIndex,
                                          "Finish");



    m_systemConfigurationStateR = createState(SystemConfigurationStepWidgetIndex,
                                             "System Configuration");
    m_connectionTypeStateR = createState(ConnectionTypeStepWidgetIndex,
                                        "System Connection Type");
    m_wirelessSettingsStateR = createState(WirelessSettingsStepWidgetIndex,
                                          "Wireless Settings");
    m_networkSettingsStateR = createState(NetworkSettingsStepWidgetIndex,
                                         "Network Settings");
    m_networkSettingsSummaryStateR = createState(NetworkSettingsSummaryStepWidgetIndex,
                                         "Network Configuration Summary");

    m_networkSettingsStateRL = createState(NetworkSettingsStepWidgetIndex,
                                         "Network Settings");
    m_networkSettingsSummaryStateRL = createState(NetworkSettingsSummaryStepWidgetIndex,
                                         "Network Configuration Summary");

    m_endUserRegistrationStateR = createState(EndUserRegistrationStepWidgetIndex,
                                             "End User Registration");
    m_endUserRegistrationSummaryStateR = createState(EndUserRegistrationSummaryStepWidgetIndex,
                                             "End User Registration Summary");


    m_welcomeState->addTransition(m_welcomeStepWidget, SIGNAL(next()),
                                  m_controllerState);

    m_controllerState->addTransition(m_controllerStepWidget, SIGNAL(back()),
                                     m_welcomeState);
    m_controllerState->addTransition(m_controllerStepWidget, SIGNAL(next()),
                                   m_systemConfigurationState);

    m_systemConfigurationState->addTransition(m_systemConfigurationStepWidget, SIGNAL(back()),
                                              m_controllerState);
    m_systemConfigurationState->addTransition(m_systemConfigurationStepWidget, SIGNAL(networkConfiguration()),
                                              m_connectionTypeState);
    m_systemConfigurationState->addTransition(m_systemConfigurationStepWidget, SIGNAL(endUserRegistration()),
                                              m_endUserRegistrationStateR);
    m_connectionTypeState->addTransition(m_connectionTypeStepWidget, SIGNAL(back()),
                                         m_systemConfigurationState);
    m_connectionTypeState->addTransition(m_connectionTypeStepWidget, SIGNAL(wirelessConnection()),
                                         m_wirelessSettingsState);
    m_connectionTypeState->addTransition(m_connectionTypeStepWidget, SIGNAL(wiredConnection()),
                                             m_networkSettingsState);

    m_wirelessSettingsState->addTransition(m_wirelessSettingsStepWidget, SIGNAL(back()),
                                           m_connectionTypeState);
    m_wirelessSettingsState->addTransition(m_wirelessSettingsStepWidget, SIGNAL(next()),
                                           m_networkSettingsStateL);

    m_networkSettingsStateL->addTransition(m_networkSettingsStepWidget, SIGNAL(back()),
                                          m_wirelessSettingsState);
    m_networkSettingsStateL->addTransition(m_networkSettingsStepWidget, SIGNAL(next()),
                                          m_networkSettingsSummaryStateL);

    m_networkSettingsSummaryStateL->addTransition(m_networkSettingsSummaryStepWidget, SIGNAL(back()),
                                          m_networkSettingsStateL);

    m_networkSettingsSummaryStateL->addTransition(m_networkSettingsSummaryStepWidget, SIGNAL(next()),
                                          m_endUserRegistrationStateL);

    m_endUserRegistrationStateL->addTransition(m_endUserRegistrationStepWidget, SIGNAL(back()),
                                              m_networkSettingsSummaryStateL);

    m_endUserRegistrationStateL->addTransition(m_endUserRegistrationStepWidget, SIGNAL(next()),
                                                 m_endUserRegistrationSummaryStateL);

    m_endUserRegistrationSummaryStateL->addTransition(m_endUserRegistrationSummaryStepWidget, SIGNAL(back()),
                                                 m_endUserRegistrationStateL);

    m_endUserRegistrationSummaryStateL->addTransition(m_endUserRegistrationSummaryStepWidget, SIGNAL(next()),
                                                 m_workflowFisnishedState);

    m_networkSettingsState->addTransition(m_networkSettingsStepWidget, SIGNAL(next()),
                                          m_networkSettingsSummaryState);

    m_networkSettingsState->addTransition(m_networkSettingsStepWidget, SIGNAL(back()),
                                          m_connectionTypeState);
    m_networkSettingsState->addTransition(m_networkSettingsStepWidget, SIGNAL(next()),
                                          m_networkSettingsSummaryState);

    m_networkSettingsSummaryState->addTransition(m_networkSettingsSummaryStepWidget, SIGNAL(back()),
                                          m_networkSettingsState);

    m_networkSettingsSummaryState->addTransition(m_networkSettingsSummaryStepWidget, SIGNAL(next()),
                                          m_endUserRegistrationState);

    m_endUserRegistrationState->addTransition(m_endUserRegistrationStepWidget, SIGNAL(back()),
                                              m_networkSettingsSummaryState);

    m_endUserRegistrationState->addTransition(m_endUserRegistrationStepWidget, SIGNAL(next()),
                                                 m_endUserRegistrationSummaryState);

    m_endUserRegistrationSummaryState->addTransition(m_endUserRegistrationSummaryStepWidget, SIGNAL(back()),
                                                 m_endUserRegistrationState);

    m_endUserRegistrationSummaryState->addTransition(m_endUserRegistrationSummaryStepWidget, SIGNAL(next()),
                                                 m_workflowFisnishedState);

    m_endUserRegistrationStateR->addTransition(m_endUserRegistrationStepWidget, SIGNAL(back()),
                                              m_systemConfigurationState);

    m_endUserRegistrationStateR->addTransition(m_endUserRegistrationStepWidget, SIGNAL(next()),
                                                 m_endUserRegistrationSummaryStateR);

    m_endUserRegistrationSummaryStateR->addTransition(m_endUserRegistrationSummaryStepWidget, SIGNAL(back()),
                                                 m_endUserRegistrationStateR);

    m_endUserRegistrationSummaryStateR->addTransition(m_endUserRegistrationSummaryStepWidget, SIGNAL(next()),
                                                 m_connectionTypeStateR);

    m_connectionTypeStateR->addTransition(m_connectionTypeStepWidget, SIGNAL(back()),
                                         m_endUserRegistrationSummaryStateR);
    m_connectionTypeStateR->addTransition(m_connectionTypeStepWidget, SIGNAL(wirelessConnection()),
                                         m_wirelessSettingsStateR);
    m_connectionTypeStateR->addTransition(m_connectionTypeStepWidget, SIGNAL(wiredConnection()),
                                             m_networkSettingsStateR);

    m_wirelessSettingsStateR->addTransition(m_wirelessSettingsStepWidget, SIGNAL(back()),
                                           m_connectionTypeStateR);
    m_wirelessSettingsStateR->addTransition(m_wirelessSettingsStepWidget, SIGNAL(next()),
                                           m_networkSettingsStateRL);

    m_networkSettingsStateRL->addTransition(m_networkSettingsStepWidget, SIGNAL(back()),
                                          m_wirelessSettingsStateR);
    m_networkSettingsStateRL->addTransition(m_networkSettingsStepWidget, SIGNAL(next()),
                                          m_networkSettingsSummaryStateRL);

    m_networkSettingsSummaryStateRL->addTransition(m_networkSettingsSummaryStepWidget, SIGNAL(back()),
                                          m_networkSettingsStateRL);

    m_networkSettingsSummaryStateRL->addTransition(m_networkSettingsSummaryStepWidget, SIGNAL(next()),
                                          m_workflowFisnishedState);

    m_networkSettingsStateR->addTransition(m_networkSettingsStepWidget, SIGNAL(back()),
                                          m_connectionTypeStateR);

    m_networkSettingsStateR->addTransition(m_networkSettingsStepWidget, SIGNAL(next()),
                                          m_networkSettingsSummaryStateR);


    m_networkSettingsSummaryStateR->addTransition(m_networkSettingsSummaryStepWidget, SIGNAL(back()),
                                          m_networkSettingsStateR);

    m_networkSettingsSummaryStateR->addTransition(m_networkSettingsSummaryStepWidget, SIGNAL(next()),
                                          m_workflowFisnishedState);


    m_stateMachine->setInitialState(m_welcomeState);
    m_stateMachine->start();
}
