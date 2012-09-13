#include "networksettingssummarystepwidget.h"
#include <QFile>
#include <QProcess>
#include <QDebug>
#include "webRequest.h"

NetworkSettingsSummaryStepWidget::NetworkSettingsSummaryStepWidget(QWidget *parent) :
    QWidget(parent)
{
    setupUi(this);

    connect(backButton, SIGNAL(clicked()), SIGNAL(back()));
    connect(nextButton, SIGNAL(clicked()), SIGNAL(next()));
    connect(backButton, SIGNAL(clicked()),this, SLOT(removeConnectionScript()));
    connect(testConnectionButton, SIGNAL(clicked()),this, SLOT(testConnection()));
}


void NetworkSettingsSummaryStepWidget::testConnection()
{
    QString setupIp("wiredConnectionScript.sh");
    QString testIpProgram("../scripts/testIp.sh");

    QProcess *testPingRouter = new QProcess();
    QProcess *testInternet = new QProcess();
    QProcess *pingBluServer = new QProcess();

    connect(testPingRouter, SIGNAL(finished(int/*, QProcess::ExitStatus*/)), this, SLOT(testRouter(int)));
    connect(testInternet, SIGNAL(finished(int/*, QProcess::ExitStatus*/)), this, SLOT(testInternet(int)));
    connect(pingBluServer, SIGNAL(finished(int/*, QProcess::ExitStatus*/)), this, SLOT(testBluuServer(int)));


//    if(QProcess::execute("/bin/chmod",QStringList() << "+x" << "wiredConnectionScript.sh") < 0)
//    {
//        return;
//    }
//    if(QProcess::execute(setupIp) < 0)
//    {
//        return;
//    }

    //router test
    testPingRouter->start(testIpProgram);

    //internet test
    QStringList arg,arg1;
    arg << "8.8.8.8";
    testInternet->start(testIpProgram,arg);

    //TODO  need to be added the address of the server
    arg1 << "127.0.0.1";
    pingBluServer->start(testIpProgram,arg1);


    //TODO
    // create a socket to test if the application is up ad working on the server
    webRequest *webAppTest = new webRequest(this,"http://127.0.0.1:8000/");
    webAppTest->sendRequest();

}
void NetworkSettingsSummaryStepWidget::testRouter(int exitCode)
{
    if(!exitCode)
    {
        //succesfully setup the ip address
        testConnectionTextEdit->setText("*** Setting the wired network is succesfull. ***\n");
    }
    else
        testConnectionTextEdit->setText("*** Setting the wired network is NOT succesfull!!! ***\n");
}

void NetworkSettingsSummaryStepWidget::testInternet(int exitCode)
{
    if(!exitCode)
    {
        //succesfully connect to internet
        testConnectionTextEdit->append("\n*** Connection to the internet is succesfull. ***\n");
    }
    else
        testConnectionTextEdit->append("\n*** Connection to the internet is NOT succesfull!!! ***\n");
}

void NetworkSettingsSummaryStepWidget::testBluuServer(int exitCode)
{
    if(!exitCode)
    {
        //succesfully connect to internet
        testConnectionTextEdit->append("\n*** Connection to the BluuServer is succesfull. ***\n");
    }
    else
        testConnectionTextEdit->append("\n*** Connection to the BluuServer is NOT succesfull!!! ***\n");
}

void NetworkSettingsSummaryStepWidget::removeConnectionScript()
{

    if(QFile::exists("wiredConnectionScript.sh"))
     {
        QFile::remove("wiredConnectionScript.sh");
     }
    if(QFile::exists("wirelessConnectionScript.sh"))
     {
        QFile::remove("wirelessConnectionScript.sh");
     }
}

