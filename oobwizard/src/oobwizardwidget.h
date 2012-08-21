#ifndef OOBWIZARDWIDGET_H
#define OOBWIZARDWIDGET_H

#include <QWidget>

class WizardContext;

namespace Ui {
class OobWizardWidget;
}

class OobWizardWidget : public QWidget
{
    Q_OBJECT
    
public:
    explicit OobWizardWidget(QWidget *parent = 0);
    ~OobWizardWidget();

signals:
    void controllerStepValidated();

protected:
    void installValidators();

protected slots:
    void validateControlStep();

private:
    WizardContext *m_context;
    Ui::OobWizardWidget *m_ui;
};

#endif // OOBWIZARDWIDGET_H
