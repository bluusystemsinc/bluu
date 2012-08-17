#include <QApplication>
#include <QtDeclarative>

#include "wizardcontext.h"

int main(int argc, char **argv)
{
    QApplication app(argc, argv);
    QDeclarativeView view;
    WizardContext *wizardContext = new WizardContext(&view);
    QDeclarativeContext *context = view.engine()->rootContext();

    view.engine()->addImportPath("../lib/imports");

    context->setContextProperty("context", wizardContext);
    view.setSource(QUrl::fromLocalFile("qml/main.qml"));

    view.setResizeMode(QDeclarativeView::SizeRootObjectToView);
    view.setFixedSize(480, 232);
    view.show();
    return app.exec();
}
