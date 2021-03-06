#ifndef ENDUSERREGISTRATIONSUMMARYSTEP_H
#define ENDUSERREGISTRATIONSUMMARYSTEP_H

#include <QWidget>
#include "ui_enduserregistrationsummarystep.h"

namespace Ui {
class endUserRegistrationSummaryStep;
}

class endUserRegistrationSummaryStep : public QWidget, public Ui::endUserRegistrationSummaryStep
{
    Q_OBJECT
    
public:
    explicit endUserRegistrationSummaryStep(QWidget *parent = 0);
signals:
    void back();
    void next();
public slots:
    void saveInfoToFile();

private:
    Ui::endUserRegistrationSummaryStep *ui;
};

#endif // ENDUSERREGISTRATIONSUMMARYSTEP_H
