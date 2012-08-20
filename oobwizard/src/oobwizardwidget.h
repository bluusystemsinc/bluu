#ifndef OOBWIZARDWIDGET_H
#define OOBWIZARDWIDGET_H

#include <QWidget>

namespace Ui {
class OobWizardWidget;
}

class OobWizardWidget : public QWidget
{
    Q_OBJECT
    
public:
    explicit OobWizardWidget(QWidget *parent = 0);
    ~OobWizardWidget();

private:
    Ui::OobWizardWidget *ui;
};

#endif // OOBWIZARDWIDGET_H
