#include "enduserregistrationsummarystep.h"
#include "ui_enduserregistrationsummarystep.h"
#include <QFile>
#include <QTextStream>

endUserRegistrationSummaryStep::endUserRegistrationSummaryStep(QWidget *parent) :
    QWidget(parent)
{
    setupUi(this);

    connect(backButton, SIGNAL(clicked()), SIGNAL(back()));
    connect(nextButton, SIGNAL(clicked()), SIGNAL(next()));
    connect(nextButton, SIGNAL(clicked()), this, SLOT(saveInfoToFile()));
}
void endUserRegistrationSummaryStep::saveInfoToFile()
{
    QString program("endUserRegistrationInfo.txt");

    QFile file(program);
    file.open(QIODevice::WriteOnly | QIODevice::Text);
    QTextStream out(&file);

    out << endFirstNameLabel->text() << "\n";
    out << endMiddleInitialLabel->text() << "\n";
    out << endLastNameLabel->text() << "\n";
    out << EndSiteStreetAddressLabel->text() << "\n";
    out << endSiteCityLabel->text() << "\n";
    out << endZIPCodeLabel->text() << "\n";
    out << endSiteCountryLabel->text() << "\n";
    out << endUserEmailAddressLabel->text() << "\n";
    out << endUserPhoneNumberLabel->text() << "\n";
    out << endDealerIDLabel->text() << "\n";

    file.close();



    //TODO
    // send the info saved in a file to the server
}
