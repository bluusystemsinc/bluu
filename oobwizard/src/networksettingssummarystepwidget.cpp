#include "networksettingssummarystepwidget.h"
#include <QFile>
#include <QProcess>
#include <QDebug>

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
//    QProcess *pingBluServer = new QProcess();

    connect(testPingRouter, SIGNAL(finished(int/*, QProcess::ExitStatus*/)), this, SLOT(testRouter(int)));
    connect(testPingRouter, SIGNAL(finished(int/*, QProcess::ExitStatus*/)), this, SLOT(testInternet(int)));


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
    QStringList arg;
    arg << "8.8.8.8";
    testInternet->start(testIpProgram,arg);


//    myProcess->start(program);
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

