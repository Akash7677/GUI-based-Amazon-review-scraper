from PyQt5 import QtCore, QtGui, QtWidgets
import sys


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
        self.dateEdit.setDisplayFormat("dd-MM-yyyy")
        self.dateEdit.setObjectName("dateEdit")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(40, 170, 141, 17))
        self.label.setObjectName("label")

        # Connect UI elements to functions
        self.configBrowse.clicked.connect(self.browse_config)
        self.startBotBtn.clicked.connect(self.start_bot)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Digiklap - Telegram Review bot"))
        self.configFileInputBox.setToolTip(_translate("Dialog", "Path to the config file"))
        self.configLabel.setText(_translate("Dialog", "Config File Location"))
        self.configBrowse.setToolTip(_translate("Dialog", "Browse for config file"))
        self.configBrowse.setText(_translate("Dialog", "Browse"))
        self.consoleLabel.setText(_translate("Dialog", "Console:"))
        self.startBotBtn.setToolTip(_translate("Dialog", "Start the bot"))
        self.startBotBtn.setText(_translate("Dialog", "Start Bot"))
        self.label.setText(_translate("Dialog", "Select the date"))

    def browse_config(self):
        file_selected, _ = QtWidgets.QFileDialog.getOpenFileName(None, "Select Config File", "", "Config Files (*.ini)")
        self.configFileInputBox.setPlainText(file_selected)

    def start_bot(self):
        config_file = self.configFileInputBox.toPlainText()
        selected_date = self.dateEdit.date().toString("dd-MM-yyyy")

        if not config_file:
            self.write("Please enter the path to the config file.")
            return

            # Start the bot using QProcess
        self.bot_process = QtCore.QProcess()
        self.bot_process.setProcessChannelMode(QtCore.QProcess.MergedChannels)
        self.bot_process.readyReadStandardOutput.connect(self.read_bot_output)
        self.bot_process.finished.connect(self.bot_finished)

        # Run the bot in a separate process
        self.bot_process.start(f"python3 bot_code.py {selected_date} {config_file}")

    def read_bot_output(self):
        # Read and update the console with the output
        output = self.bot_process.readAllStandardOutput().data().decode('utf-8')
        self.write(output)

    def bot_finished(self, exit_code, exit_status):
        # Update the console when the bot process finishes
        self.write(f"Bot process finished with exit code: {exit_code}")


    def write(self, message):
        # Append the message to the console
        cursor = self.consolTextEdit.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(message)
        # Scroll to the end of the document
        scroll_bar = self.consolTextEdit.verticalScrollBar()
        scroll_bar.setValue(scroll_bar.maximum())

    def flush(self):
        # Process any pending events
        QtWidgets.QApplication.processEvents()
# --------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
