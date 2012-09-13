#include "enduserregistrationsummarystep.h"
#include "ui_enduserregistrationsummarystep.h"
#include <QFile>
#include <QTextStream>
#include "webRequest.h"

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
    QString program("endUserRegistrationInfo.xml");

    QFile file(program);
    file.open(QIODevice::WriteOnly | QIODevice::Text);
    QTextStream out(&file);

//    out << "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n";
//    out << "<UserInfo>\n";
//    out << "\t<FirstName>" << endFirstNameLabel->text() << "</FirstName>\n";
//    out << "\t<MiddleName>" << endMiddleInitialLabel->text() << "</MiddleName>\n";
//    out << "\t<LastName>" << endLastNameLabel->text() << "</LastName>\n";
//    out << "\t<Address>" << EndSiteStreetAddressLabel->text() << "</Address>\n";
//    out << "\t<City>" << endSiteCityLabel->text() << "</City>\n";
//    out << "\t<ZipCode>" << endZIPCodeLabel->text() << "</ZipCode>\n";
//    out << "\t<Country>" << endSiteCountryLabel->text() << "</Country>\n";
//    out << "\t<Email>" << endUserEmailAddressLabel->text() << "</Email>\n";
//    out << "\t<PhoneNumber>" << endUserPhoneNumberLabel->text() << "</PhoneNumber>\n";
//    out << "\t<DealerId>" << endDealerIDLabel->text() << "</DealerId>\n";
//    out << "</UserInfo>\n";

//    out << endFirstNameLabel->text() << "\n";
//    out << endMiddleInitialLabel->text() << "\n";
//    out << endLastNameLabel->text() << "\n";
//    out << EndSiteStreetAddressLabel->text() << "\n";
//    out << endSiteCityLabel->text() << "\n";
//    out << endZIPCodeLabel->text() << "\n";
//    out << endSiteCountryLabel->text() << "\n";
//    out << endUserEmailAddressLabel->text() << "\n";
//    out << endUserPhoneNumberLabel->text() << "\n";
//    out  << endDealerIDLabel->text() << "\n";

    out << "\"first_name\": \"" << endFirstNameLabel->text() << "\",\n";
    out << "\"middle_initial\": \"" << endMiddleInitialLabel->text() << "\",\n";
    out << "\"last_name\": \"" << endLastNameLabel->text() << "\",\n";
    out << "\"site_street_address\": \"" << EndSiteStreetAddressLabel->text() << "\",\n";
    out << "\"cite_city\": \"" << endSiteCityLabel->text() << "\",\n";
    out << "\"zip_code\": \"" << endZIPCodeLabel->text() << "\",\n";
    out << "\"site_country\": \"" << endSiteCountryLabel->text() << "\",\n";
    out << "\"email_address\": \"" << endUserEmailAddressLabel->text() << "\",\n";
    out << "\"phone_number\": \"" << endUserPhoneNumberLabel->text() << "\",\n";
    out << "\"serial_number\": \"" << endDealerIDLabel->text() << "\"\n";

    file.close();



    //TODO
    // send the info saved in a file to the server

    webRequest *sendInfo = new webRequest(this,"http://127.0.0.1:8000/");
    sendInfo->sendFromFile(program);
}
