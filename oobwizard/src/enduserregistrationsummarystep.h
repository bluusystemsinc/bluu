#ifndef ENDUSERREGISTRATIONSUMMARYSTEP_H
#define ENDUSERREGISTRATIONSUMMARYSTEP_H

#include <QWidget>
#include "ui_enduserregistrationsummarystep.h"

namespace Ui {
class endUserRegistrationSummaryStep;
}

class endUserRegistrationSummaryStep : public QWidget, private Ui::endUserRegistrationSummaryStep
{
    Q_OBJECT
    
public:
    explicit endUserRegistrationSummaryStep(QWidget *parent = 0);
    ~endUserRegistrationSummaryStep();
signals:
    void back();
    void next();


private:
    Ui::endUserRegistrationSummaryStep *ui;
};

#endif // ENDUSERREGISTRATIONSUMMARYSTEP_H
