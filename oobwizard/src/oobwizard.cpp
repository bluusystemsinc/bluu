#include <QApplication>
#include <QtDeclarative>

int main(int argc, char **argv)
{
    QApplication app(argc, argv);
    QDeclarativeView view;

    view.setSource(QUrl::fromLocalFile("qml/main.qml"));

    view.resize(640, 480);
    view.show();
    return app.exec();
}
