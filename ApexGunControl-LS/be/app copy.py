from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtCore import Qt
import sys

def run():
    app = QApplication(sys.argv)

    form = QWidget()
    form.setWindowTitle("ApexGunControl")

    label = QLabel(form)
    label.setText("HelloWorld!")
    label.resize(300, 200)
    label.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)

    form.show()

    print("Running")

    return app.exec_()