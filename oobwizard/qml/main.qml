import QtQuick 1.1
import QtDesktop 0.1

Window {
    id: root

    property int margin: 10
    property bool firstStep: true
    property bool lastStep: false

    width: 480; height: 232

    SystemPalette { id: syspal; }

    Rectangle {
        id: topRectangle

        anchors {
            top: parent.top
            left: parent.left
            right: parent.right
        }
        height: 40
        color: "lightblue"

        Label {
            anchors {
                fill: parent
                rightMargin: margin
            }

            horizontalAlignment: Text.AlignRight
            text: "Bluu Systems"
            color: "white"
            font.pixelSize: parent.height - margin
        }
    }

    Rectangle {
        id: bodyRectangle

        anchors {
            top: topRectangle.bottom
            left: parent.left
            right: parent.right
            bottom: bottomRectangle.top
        }

        color: syspal.button

        Loader {
            id: loader

            anchors.fill: parent
            source: context.currentUrl

            onItemChanged: {
                if(item && item.show)
                    item.show();
            }
        }
    }

    Rectangle {
        id: bottomRectangle

        height: buttonRow.height + margin * 2

        anchors {
            left: parent.left
            right: parent.right
            bottom: parent.bottom
        }

        ButtonRow {
            id: buttonRow

            width: childrenRect.width
            height: childrenRect.height
            anchors {
                right: parent.right
                rightMargin: root.margin
                verticalCenter: parent.verticalCenter
            }
            spacing: root.margin

            Button {
                id: backButton

                enabled: context.isBackEnabled
                text: "&Back"

                onClicked: context.backClicked();
            }

            Button {
                id: nextButton

                enabled: context.isNextEnabled
                text: "&Next"

                onClicked: context.nextClicked();
            }
        }
    }
}
