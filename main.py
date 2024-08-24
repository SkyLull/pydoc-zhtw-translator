from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import Qt
from pytermgui import window
import polib
import pathlib
from translator import Prompter
import requests
from qtui_ui import Ui_MainWindow
import os
import sys


class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        self.columns = ["Tags", "Contents"]
        super(TableModel, self).__init__()
        self._data = [['T' if entry.translated() else '  ' + 'F' if entry.fuzzy else ' ', entry.msgid] for entry in data]

    def headerData(self, section: int, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.columns[section]
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return f"{section + 1}"

    def data(self, index, role):
        if role == Qt.DisplayRole:
            # See below for the nested-list data structure.
            # .row() indexes into the outer list,
            # .column() indexes into the sub-list
            return self._data[index.row()][index.column()]

    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self._data[0])


class FunctionFrame():
    def __init__(self, window, main_window) -> None:
        self.main_window = main_window
        self.window = window # duh
        self.current_row = None  # track the current row that's being edited
        self.working_file = None # indicate the .po file, which will later be used to fetch corresponding rst
        self.connect_ui() # duh
        self.data_model = None # store the dataframe of parsed .po file
        self.prompter = None
        self.pydoc_classes = ['c-api', 'distributing', 'extending', 
                            'faq', 'howto', 'includes', 'installing', 'library', 'reference',
                            'tutorial', 'using', 'whatsnew']
        self.working_doc = None


    def save_translation(self):
        if self.current_row is not None and self.working_file:
            # Get the edited translation text from the text editor widget
            new_translation = self.window.ipf_editText.toPlainText()

            # Update the corresponding entry in the .po file
            self.working_file[self.current_row].msgstr = new_translation
            self.data_model._data[self.current_row][0] = 'T' if new_translation else '  '
            # Save the .po file back to disk
            self.working_file.save()


    def load_po(self):
        filename, _ = QFileDialog.getOpenFileName()
        filepath = pathlib.Path(filename)
        if filename:
            print(filename)
        if filepath.suffix == '.po':
            self.main_window.setWindowTitle(f"pydoc ZH-TW Translate Helper - {filepath.name}")
            self.working_file = polib.pofile(filename)
            self.data_model = TableModel(self.working_file)
            self.window.tableView.setModel(self.data_model)
            self.window.tableView.horizontalHeader().resizeSection(0, 10)
            self.window.tableView.horizontalHeader().resizeSection(1, 690)
            self.window.tableView.resizeRowsToContents()
            self.window.tableView.clicked.connect(self.put_txt)

            if filepath.parts[-2] not in self.pydoc_classes:
                print("[Info] You seems not loading .po file from an officially"
                "structured repo, assuming this entry is from 'library'.")
            
            dir_name = filepath.parts[-2] if filepath.parts[-2] in self.pydoc_classes else 'library'
            
            doc_request = requests.get(f"https://raw.githubusercontent.com/python/cpython/main/Doc/{dir_name}/{filepath.stem}.rst", 
                                        timeout=5)

            if doc_request.status_code == 200:
                self.working_doc = doc_request.text
                self.prompter = Prompter(plain_doc=self.working_doc)
            else:
                print("[Error] Fail to fetch origianl .rst file, gpt helper diabled.")
                self.window.lab_connection_stat.setText("No RST.")
                self.prompter = None
                self.working_doc = None


    def put_txt(self, index):
        # Get the row index from the click event
        self.current_row = index.row()

        # Access the translation entry
        translation = self.working_file[self.current_row].msgstr

        # Set the translation text in the ipf_editText widget
        self.window.ipf_editText.setPlainText(translation)
        self.window.btn_dupe.setEnabled(True)
        self.window.btn_save.setEnabled(False) # only enable when text change is present


    def dupe_txt(self):
        if self.current_row is not None:
            original_text = self.working_file[self.current_row].msgid
            self.window.ipf_editText.setPlainText(original_text)


    def enable_save_button(self):
        if self.current_row is not None:
            self.window.btn_save.setEnabled(True)


    def put_translation(self):
        if self.prompter is not None and self.working_doc is not None:
            result = self.prompter.translate(self.working_file[self.current_row].msgid)
            self.window.ipf_editText.setPlainText(result)


    def try_api(self):
        if self.prompter is not None:
            status = self.prompter.init_connection(self.window.ipf_apikey.toPlainText())
            self.window.lab_connection_stat.setText(status)
            if status == "Connected.":
                self.window.btn_gpt.setEnabled(True)
        else:
            self.window.lab_connection_stat.setText("load a file first")


    def connect_ui(self):
        self.window.btn_openpo.clicked.connect(self.load_po)

        self.window.btn_save.clicked.connect(self.save_translation)
        self.window.btn_save.setEnabled(False)  # Disable by default

        self.window.btn_dupe.clicked.connect(self.dupe_txt)
        self.window.btn_dupe.setEnabled(False)

        self.window.btn_gpt.clicked.connect(self.put_translation)
        self.window.btn_dupe.setEnabled(False)

        self.window.btn_connect.clicked.connect(self.try_api)

        self.window.ipf_editText.textChanged.connect(self.enable_save_button) # only enable when change is present


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    os.environ['QT_IM_MODULE'] = 'fcitx'
    main_window = QtWidgets.QMainWindow()
    window = Ui_MainWindow()
    window.setupUi(main_window)
    funcs = FunctionFrame(window, main_window)
    main_window.show()
    sys.exit(app.exec_())
