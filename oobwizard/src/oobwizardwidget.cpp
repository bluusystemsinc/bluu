#include "oobwizardwidget.h"
#include "ui_oobwizardwidget.h"

#include <QStateMachine>

#include "wizardcontext.h"
#include "welcomestepwidget.h"
#include "controllerstepwidget.h"
#include "connectiontypestepwidget.h"
#include "networksettingsstepwidget.h"
#include "wirelesssettingsstepwidget.h"
#include "systemconfigurationstepwidget.h"
#include "enduserregistrationstepwidget.h"
#include "networksettingssummarystepwidget.h"

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
    m_networkSettingsSummaryStepWidget = new NetworkSettingsSummaryStepWidget(
                this);
    stackedWidget->insertWidget(NetworkSettingsSummaryStepWidgetIndex,
                                m_networkSettingsSummaryStepWidget);

    m_endUserRegistrationStepWidget = new EndUserRegistrationStepWidget(this);
    stackedWidget->insertWidget(EndUserRegistrationStepWidgetIndex,
                                m_endUserRegistrationStepWidget);

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
    m_welcomeState = createState(WelcomeStepWidgetIndex, "Welcome Step");
    m_controllerState = createState(ControllerStepWidgetIndex,
                                    "Controller Step");
    m_systemConfigurationState = createState(SystemConfigurationStepWidgetIndex,
                                             "System Configuration Step");
    m_connectionTypeState = createState(ConnectionTypeStepWidgetIndex,
                                        "Connection Type Step");
    m_wirelessSettingsState = createState(WirelessSettingsStepWidgetIndex,
                                          "Wireless Settings Step");
    m_networkSettingsState = createState(NetworkSettingsStepWidgetIndex,
                                         "Network Settings Step");
    m_networkSettingsSummaryState = createState(
                NetworkSettingsSummaryStepWidgetIndex,
                "Network Settings Summary Step");
    m_endUserRegistrationState = createState(EndUserRegistrationStepWidgetIndex,
                                             "End User Registration Step");

    m_welcomeState->addTransition(m_welcomeStepWidget, SIGNAL(next()),
                                  m_controllerState);

    m_controllerState->addTransition(m_controllerStepWidget, SIGNAL(back()),
                                     m_welcomeState);
    m_controllerState->addTransition(m_controllerStepWidget,
                                     SIGNAL(next()),
                                     m_systemConfigurationState);

    m_systemConfigurationState->addTransition(m_systemConfigurationStepWidget,
                                              SIGNAL(back()),
                                              m_controllerState);
    m_systemConfigurationState->addTransition(m_systemConfigurationStepWidget,
                                              SIGNAL(networkConfiguration()),
                                              m_connectionTypeState);
    m_systemConfigurationState->addTransition(m_systemConfigurationStepWidget,
                                              SIGNAL(endUserRegistration()),
                                              m_endUserRegistrationState);

    m_connectionTypeState->addTransition(m_connectionTypeStepWidget,
                                         SIGNAL(back()),
                                         m_systemConfigurationState);
    m_connectionTypeState->addTransition(m_connectionTypeStepWidget,
                                         SIGNAL(wirelessConnection()),
                                         m_wirelessSettingsState);
    m_connectionTypeState->addTransition(m_connectionTypeStepWidget,
                                         SIGNAL(wiredConnection()),
                                         m_networkSettingsState);

    m_wirelessSettingsState->addTransition(m_wirelessSettingsStepWidget,
                                           SIGNAL(back()),
                                           m_connectionTypeState);
    m_wirelessSettingsState->addTransition(m_wirelessSettingsStepWidget,
                                           SIGNAL(next()),
                                           m_networkSettingsState);

    m_networkSettingsState->addTransition(m_networkSettingsStepWidget,
                                          SIGNAL(next()),
                                          m_networkSettingsSummaryState);

    m_networkSettingsSummaryState->addTransition(
                m_networkSettingsSummaryStepWidget, SIGNAL(back()),
                m_networkSettingsState);

    m_endUserRegistrationState->addTransition(m_endUserRegistrationStepWidget,
                                              SIGNAL(back()),
                                              m_systemConfigurationState);

    m_stateMachine->setInitialState(m_welcomeState);
    m_stateMachine->start();
}
