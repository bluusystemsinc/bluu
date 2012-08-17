#include <QApplication>
#include <QtDeclarative>

#include "wizardcontext.h"

int main(int argc, char **argv)
{
    QApplication app(argc, argv);
    QDeclarativeView view;
    WizardContext *wizardContext = new WizardContext(&view);
    QDeclarativeContext *context = view.engine()->rootContext();

    //TODO  hostname object value must be initialized with a parameter from ui or else
    QString hostname("192.168.2.107");

    wizardContext->runConnectionTest(hostname);

    context->setContextProperty("context", wizardContext);
    view.setSource(QUrl::fromLocalFile("qml/main.qml"));

    view.setResizeMode(QDeclarativeView::SizeRootObjectToView);
    view.setFixedSize(480, 232);
    view.show();
    return app.exec();
}
