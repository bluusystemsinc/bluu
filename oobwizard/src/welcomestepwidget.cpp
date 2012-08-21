#include "welcomestepwidget.h"

#include <QTextStream>

WelcomeStepWidget::WelcomeStepWidget(QWidget *parent) :
    QWidget(parent)
{
    QFile file("text/eula");
    QString eula;

    setupUi(this);

    if(file.open(QIODevice::ReadOnly))
    {
        QTextStream stream(&file);

        eula = stream.readAll();
    }
    else
        qFatal("eula file not found");

    eulaTextEdit->setPlainText(eula);

    connect(nextButton, SIGNAL(clicked()), SIGNAL(next()));
}
