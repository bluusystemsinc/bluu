#include <QApplication>

//#include "wizardcontext.h"
#include "oobwizardwidget.h"

int main(int argc, char **argv)
{
    QApplication app(argc, argv);
    OobWizardWidget widget;

#ifdef EMBEDDED
    widget.showFullScreen();
#else
    widget.show();
#endif
    return app.exec();
}
