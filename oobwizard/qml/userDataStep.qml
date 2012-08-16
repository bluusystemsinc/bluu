import QtQuick 1.1
import QtDesktop 0.1

Item {
    anchors.horizontalCenter: parent ? parent.horizontalCenter : undefined
    anchors.verticalCenter: parent ? parent.verticalCenter : undefined

    width: childrenRect.width
    height: childrenRect.height

    Grid {
        rows: children.length / 2
        columns: 2
        spacing: margin

        Label {
            height: firstNameTextField.height
            text: "First Name:"
            verticalAlignment: Text.AlignVCenter
            horizontalAlignment: Text.AlignRight
        }

        TextField {
            id: firstNameTextField
        }

        Label {
            height: lastNameTextField.height
            text: "Last Name:"
            verticalAlignment: Text.AlignVCenter
            horizontalAlignment: Text.AlignRight
        }

        TextField {
            id: lastNameTextField
        }

        Label {
            height: emailTextField.height
            text: "E-mail address:"
            verticalAlignment: Text.AlignVCenter
            horizontalAlignment: Text.AlignRight
        }

        TextField {
            id: emailTextField
        }
    }
}
