import os
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog
from PyQt5.QtCore import Qt, QCoreApplication
import sys
from threading import Thread
from Scrapper import main as run_scraper
from paraphraser import main_para
from Scrapper import parse_config
from scrUI import Ui_Dialog
from PyQt5.QtCore import pyqtSignal, QObject

class CustomTextWidgetStream(QObject):
    message_written = pyqtSignal(str)

    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def write(self, message):
        self.message_written.emit(message)

    def append_text(self, message):
        cursor = self.text_widget.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.text_widget.append(message)

        # Scroll to the end of the document
        scroll_bar = self.text_widget.verticalScrollBar()
        scroll_bar.setValue(scroll_bar.maximum())

    def flush(self):
        QCoreApplication.processEvents()

class ReviewScraperGUI(QDialog):
    def __init__(self):
        super().__init__()

        # Load UI from file
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # Connect buttons to functions
        self.ui.configBrowse.clicked.connect(self.browse_config)
        self.ui.outputFolderBrowse.clicked.connect(self.browse_output)
        self.ui.scrappingBtn.clicked.connect(self.start_scraper)

        # Redirect console output
        self.custom_stream = CustomTextWidgetStream(self.ui.consolTextEdit)
        self.custom_stream.message_written.connect(self.append_console_text)
        # self.custom_stream.message_written.connect(lambda message: self.ui.consolTextEdit.insertPlainText(message))
        sys.stdout = self.custom_stream
    def append_console_text(self, message):
        self.ui.consolTextEdit.append(message)

    def browse_config(self):
        file_selected, _ = QFileDialog.getOpenFileName(self, "Select Config File", "", "Config Files (*.ini)")
        self.ui.configFileInputBox.setPlainText(file_selected)

    def browse_output(self):
        folder_selected = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        self.ui.outputFilePathInputBox.setPlainText(folder_selected)

    def start_scraper(self):
        config_file = self.ui.configFileInputBox.toPlainText()
        output_folder = self.ui.outputFilePathInputBox.toPlainText()

        if self.ui.selectByConfigBtn.isChecked():
            if not config_file or not output_folder:
                print("Please enter config file and select an output folder.")
                return

            if not os.path.exists(config_file):
                print("Invalid config file. Please select a valid file.")
                return

            if not os.path.exists(output_folder):
                print("Invalid output folder. Please select a valid folder.")
                return

            url_map = parse_config(config_file)
            # print(f"config map: {url_map}")

        elif self.ui.selectByProductBtn.isChecked():
            # Map product names and links based on user input
            product_name_link_map = {}

            # Check if at least one product is provided
            at_least_one_product = False

            for i in range(1, 6):  # Assuming a maximum of 5 products
                product_name = getattr(self.ui, f'productName{i}').toPlainText().strip()
                product_link = getattr(self.ui, f'productLink{i}').toPlainText().strip()

                if product_name and product_link:
                    at_least_one_product = True
                    product_name_link_map[product_name] = [product_link]

            if not at_least_one_product:
                print("Please provide at least one product name and link.")
                return
            if not output_folder:
                print("Please select an output folder.")
                return

            url_map = dict(product_name_link_map)
            # print(f"User map: {url_map}")

        else:
            print("Please select either 'Select By Config file' or 'Select By Product'.")
            return

        # Start the scraper and paraphrasing in a separate thread to avoid freezing the GUI
        scraper_thread = Thread(target=run_scrapper_and_paraphraser, args=(url_map, output_folder))
        scraper_thread.start()

def run_scrapper_and_paraphraser(config, output_folder):
    print("Scrapping...............")
    state_chk = run_scraper(config, output_folder)
    if state_chk:
        print("paraphrasing............")
        main_para(output_folder)
    else:
        print("Some error occured in scrapper.... Not starting Paraphrasing...")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = ReviewScraperGUI()
    gui.show()
    sys.exit(app.exec_())
