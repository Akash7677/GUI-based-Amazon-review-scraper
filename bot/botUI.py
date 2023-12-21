from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1001, 883)
        self.configFileInputBox = QtWidgets.QPlainTextEdit(Dialog)
        self.configFileInputBox.setGeometry(QtCore.QRect(150, 100, 741, 31))
        self.configFileInputBox.setObjectName("configFileInputBox")
        self.configLabel = QtWidgets.QLabel(Dialog)
        self.configLabel.setGeometry(QtCore.QRect(10, 100, 151, 31))
        self.configLabel.setObjectName("configLabel")
        self.configBrowse = QtWidgets.QPushButton(Dialog)
        self.configBrowse.setGeometry(QtCore.QRect(900, 100, 89, 31))
        self.configBrowse.setObjectName("configBrowse")
        self.consoleLabel = QtWidgets.QLabel(Dialog)
        self.consoleLabel.setGeometry(QtCore.QRect(10, 260, 71, 20))
        self.consoleLabel.setObjectName("consoleLabel")
        self.consolTextEdit = QtWidgets.QTextEdit(Dialog)
        self.consolTextEdit.setGeometry(QtCore.QRect(10, 290, 981, 581))
        self.consolTextEdit.setObjectName("consolTextEdit")
        self.startBotBtn = QtWidgets.QPushButton(Dialog)
        self.startBotBtn.setGeometry(QtCore.QRect(440, 220, 111, 41))
        self.startBotBtn.setObjectName("startBotBtn")
        self.dateEdit = QtWidgets.QDateEdit(Dialog)
        self.dateEdit.setGeometry(QtCore.QRect(150, 160, 111, 41))
        self.dateEdit.setObjectName("dateEdit")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(40, 170, 141, 17))
        self.label.setObjectName("label")
        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Digiklap - Web Scraper UI"))
        self.configFileInputBox.setToolTip(_translate("Dialog", "Path to the config file"))
        self.configLabel.setText(_translate("Dialog", "Config File Location"))
        self.configBrowse.setToolTip(_translate("Dialog", "Browse for config file"))
        self.configBrowse.setText(_translate("Dialog", "Browse"))
        self.consoleLabel.setText(_translate("Dialog", "Console:"))
        self.startBotBtn.setToolTip(_translate("Dialog", "Start the bot"))
        self.startBotBtn.setText(_translate("Dialog", "Start Bot"))
        self.label.setText(_translate("Dialog", "Select the date"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
