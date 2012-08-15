#include <QApplication>
#include <QtDeclarative>

#include "wizardcontext.h"

int main(int argc, char **argv)
{
    QApplication app(argc, argv);
    QDeclarativeView view;
    WizardContext *wizardContext = new WizardContext(&view);
    QDeclarativeContext *context = view.engine()->rootContext();

    context->setContextProperty("context", wizardContext);
    view.setSource(QUrl::fromLocalFile("qml/main.qml"));

    view.setResizeMode(QDeclarativeView::SizeRootObjectToView);
    view.resize(640, 480);
    view.show();
    return app.exec();
}
