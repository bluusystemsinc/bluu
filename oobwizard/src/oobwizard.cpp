#include <QApplication>
#include <QtDeclarative>

//#include "wizardcontext.h"
#include "oobwizardwidget.h"

int main(int argc, char **argv)
{
    QApplication app(argc, argv);
    OobWizardWidget widget;

    widget.show();
    return app.exec();
}
