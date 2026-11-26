import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: win
    visible: true
    width: 380
    height: 420
    title: "Phone Webcam"

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 10

        Label { text: "Camera Settings"; font.bold: true; font.pixelSize: 16 }

        GridLayout {
            columns: 2
            columnSpacing: 12

            Label { text: "Width" }
            SpinBox {
                id: wSpin
                from: 320; to: 1920; stepSize: 16
                editable: true
                value: backend.width
            }

            Label { text: "Height" }
            SpinBox {
                id: hSpin
                from: 240; to: 1080; stepSize: 16
                editable: true
                value: backend.height
            }

            Label { text: "FPS" }
            SpinBox {
                id: fpsSpin
                from: 5; to: 30
                editable: true
                value: backend.fps
            }

            Label { text: "JPEG quality" }
            Slider {
                id: qSlider
                from: 0.3; to: 1.0
                value: backend.quality
                Layout.fillWidth: true
            }
        }

        Button {
            text: "Apply"
            onClicked: backend.applySettings(wSpin.value, hSpin.value,
                                             fpsSpin.value, qSlider.value)
        }

        Rectangle {
            Layout.fillWidth: true
            height: 44
            radius: 6
            color: "#222"
            Label {
                anchors.centerIn: parent
                color: "#eee"
                text: backend.lanUrl()
                font.family: "Consolas"
            }
        }

        Label { text: "Status: " + backend.status; color: "#8a8" }

        Button {
            text: "Open config folder"
            onClicked: backend.openConfigFolder()
        }

        Item { Layout.fillHeight: true }
    }
}