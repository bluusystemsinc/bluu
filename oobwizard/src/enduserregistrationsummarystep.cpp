#include "enduserregistrationsummarystep.h"
#include "ui_enduserregistrationsummarystep.h"
#include <QFile>
#include <QTextStream>
#include "webRequest.h"
#include <QNetworkRequest>
#include <QMessageBox>
#include <QDebug>

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
     QVariantMap userInfoData;

     userInfoData.insert("first_name",endFirstNameLabel->text());
     userInfoData.insert("last_name", endLastNameLabel->text());
     userInfoData.insert("middle_initial", endMiddleInitialLabel->text());
     userInfoData.insert("email_address", endUserEmailAddressLabel->text());
     userInfoData.insert("phone_number", endUserPhoneNumberLabel->text());
     userInfoData.insert("serial_number", endDealerIDLabel->text());
     userInfoData.insert("site_city", endSiteCityLabel->text());
     userInfoData.insert("site_country", endSiteCountryLabel->text());
     userInfoData.insert("site_state", endSiteStateLabel->text());
     userInfoData.insert("site_street_address", EndSiteStreetAddressLabel->text());
     userInfoData.insert("zip_code", endZIPCodeLabel->text());

   // send data to the server
    webRequest *sendInfo = new webRequest(this,"http://127.0.0.1:800");
    sendInfo->sendDataToServer(userInfoData);
}
