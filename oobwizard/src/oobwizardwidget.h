#ifndef OOBWIZARDWIDGET_H
#define OOBWIZARDWIDGET_H

#include <QWidget>
#include "ui_oobwizardwidget.h"

class WizardContext;

class OobWizardWidget : public QWidget, private Ui::OobWizardWidget
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
};

#endif // OOBWIZARDWIDGET_H
