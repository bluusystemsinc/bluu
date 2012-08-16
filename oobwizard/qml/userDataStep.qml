import QtQuick 1.1
import QtDesktop 0.1

Item {
    anchors.horizontalCenter: parent ? parent.horizontalCenter : undefined
    anchors.verticalCenter: parent ? parent.verticalCenter : undefined

    width: childrenRect.width
    height: childrenRect.height

    function show()
    {
        firstNameTextField.focus = true;
    }

    Grid {
        columns: 3
        rows: children.length / columns
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

        Image {
            width: firstNameTextField.height
            height: firstNameTextField.height
            source: firstNameTextField.acceptableInput
                    ? "../image/accepted_48.png"
                    : "../image/not_acceptable_48.png"
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

        Image {
            width: lastNameTextField.height
            height: lastNameTextField.height
            source: lastNameTextField.acceptableInput
                    ? "../image/accepted_48.png"
                    : "../image/not_acceptable_48.png"
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

        Image {
            width: emailTextField.height
            height: emailTextField.height
            source: emailTextField.acceptableInput
                    ? "../image/accepted_48.png"
                    : "../image/not_acceptable_48.png"
        }
    }
}
