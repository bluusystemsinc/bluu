#ifndef ENDUSERREGISTRATIONSUMMARYSTEP_H
#define ENDUSERREGISTRATIONSUMMARYSTEP_H

#include <QWidget>

namespace Ui {
class endUserRegistrationSummaryStep;
}

#include "enduserregistrationstepwidget.h"

class endUserRegistrationSummaryStep : public QWidget
{
    Q_OBJECT
    
public:
    explicit endUserRegistrationSummaryStep(QWidget *parent = 0);
    ~endUserRegistrationSummaryStep();
    
private:
    Ui::endUserRegistrationSummaryStep *ui;
};

#endif // ENDUSERREGISTRATIONSUMMARYSTEP_H
