import QtQuick 1.1
import QtDesktop 0.1

Window {
    id: root

    property int margin: 10
    property bool firstStep: true
    property bool lastStep: false

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

        Flickable {
            anchors.fill: parent
            contentWidth: loader.item ? loader.item.width : 0
            contentHeight: loader.item ? loader.item.height : 0

            Loader {
                id: loader
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
                enabled: !firstStep
                text: "&Back"
            }

            Button {
                enabled: !lastStep
                text: "&Next"
            }
        }
    }
}
