# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'email_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtWidgets

class Ui_AddEmailDialog(object):
    def setupUi(self, AddEmailDialog):
        AddEmailDialog.setObjectName("AddEmailDialog")
        AddEmailDialog.resize(668, 355)
        self.verticalLayout = QtWidgets.QVBoxLayout(AddEmailDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.emailGroupBox = QtWidgets.QGroupBox(AddEmailDialog)
        self.emailGroupBox.setEnabled(True)
        self.emailGroupBox.setObjectName("emailGroupBox")
        self.formLayout = QtWidgets.QFormLayout(self.emailGroupBox)
        self.formLayout.setObjectName("formLayout")
        self.toLabel = QtWidgets.QLabel(self.emailGroupBox)
        self.toLabel.setObjectName("toLabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.toLabel)
        self.toLineEdit = QtWidgets.QLineEdit(self.emailGroupBox)
        self.toLineEdit.setObjectName("toLineEdit")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.toLineEdit)
        self.subjectLabel = QtWidgets.QLabel(self.emailGroupBox)
        self.subjectLabel.setObjectName("subjectLabel")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.subjectLabel)
        self.subjectLineEdit = QtWidgets.QLineEdit(self.emailGroupBox)
        self.subjectLineEdit.setObjectName("subjectLineEdit")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.subjectLineEdit)
        self.bodyLabel = QtWidgets.QLabel(self.emailGroupBox)
        self.bodyLabel.setObjectName("bodyLabel")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.bodyLabel)
        self.bodyPlainTextEdit = QtWidgets.QPlainTextEdit(self.emailGroupBox)
        self.bodyPlainTextEdit.setReadOnly(False)
        self.bodyPlainTextEdit.setObjectName("bodyPlainTextEdit")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.bodyPlainTextEdit)
        self.verticalLayout.addWidget(self.emailGroupBox)
        self.widget_2 = QtWidgets.QWidget(AddEmailDialog)
        self.widget_2.setObjectName("widget_2")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.widget_2)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.fileGroupBox = QtWidgets.QGroupBox(self.widget_2)
        self.fileGroupBox.setObjectName("fileGroupBox")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.fileGroupBox)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.filePathLlineEdit = QtWidgets.QLineEdit(self.fileGroupBox)
        self.filePathLlineEdit.setObjectName("filePathLlineEdit")
        self.horizontalLayout.addWidget(self.filePathLlineEdit)
        self.browsePushButton = QtWidgets.QPushButton(self.fileGroupBox)
        self.browsePushButton.setObjectName("browsePushButton")
        self.horizontalLayout.addWidget(self.browsePushButton)
        self.horizontalLayout_4.addWidget(self.fileGroupBox)
        self.periodGroupBox = QtWidgets.QGroupBox(self.widget_2)
        self.periodGroupBox.setObjectName("periodGroupBox")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.periodGroupBox)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.widget = QtWidgets.QWidget(self.periodGroupBox)
        self.widget.setObjectName("widget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.periodLabel = QtWidgets.QLabel(self.widget)
        self.periodLabel.setObjectName("periodLabel")
        self.horizontalLayout_2.addWidget(self.periodLabel)
        self.periodSpinBox = QtWidgets.QSpinBox(self.widget)
        self.periodSpinBox.setMinimum(1)
        self.periodSpinBox.setMaximum(1000)
        self.periodSpinBox.setObjectName("periodSpinBox")
        self.horizontalLayout_2.addWidget(self.periodSpinBox)
        self.periodComboBox = QtWidgets.QComboBox(self.widget)
        self.periodComboBox.setObjectName("periodComboBox")
        self.periodComboBox.addItem("")
        self.periodComboBox.addItem("")
        self.periodComboBox.addItem("")
        self.periodComboBox.addItem("")
        self.periodComboBox.addItem("")
        self.periodComboBox.addItem("")
        self.horizontalLayout_2.addWidget(self.periodComboBox)
        self.horizontalLayout_3.addWidget(self.widget)
        self.horizontalLayout_4.addWidget(self.periodGroupBox)
        self.verticalLayout.addWidget(self.widget_2)
        self.buttonBox = QtWidgets.QDialogButtonBox(AddEmailDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(AddEmailDialog)
        self.periodComboBox.setCurrentIndex(2)
        self.buttonBox.accepted.connect(AddEmailDialog.accept)
        self.buttonBox.rejected.connect(AddEmailDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(AddEmailDialog)

    def retranslateUi(self, AddEmailDialog):
        _translate = QtCore.QCoreApplication.translate
        AddEmailDialog.setWindowTitle(_translate("AddEmailDialog", "Add a task"))
        self.emailGroupBox.setTitle(_translate("AddEmailDialog", "Email details"))
        self.toLabel.setText(_translate("AddEmailDialog", "To"))
        self.subjectLabel.setText(_translate("AddEmailDialog", "Subject"))
        self.bodyLabel.setText(_translate("AddEmailDialog", "Content"))
        self.fileGroupBox.setTitle(_translate("AddEmailDialog", "Attachment"))
        self.filePathLlineEdit.setPlaceholderText(_translate("AddEmailDialog", "File path"))
        self.browsePushButton.setText(_translate("AddEmailDialog", "Browse"))
        self.periodGroupBox.setTitle(_translate("AddEmailDialog", "Schedule"))
        self.periodLabel.setText(_translate("AddEmailDialog", "Send every"))
        self.periodComboBox.setItemText(0, _translate("AddEmailDialog", "Minutes"))
        self.periodComboBox.setItemText(1, _translate("AddEmailDialog", "Hours"))
        self.periodComboBox.setItemText(2, _translate("AddEmailDialog", "Days"))
        self.periodComboBox.setItemText(3, _translate("AddEmailDialog", "Weeks"))
        self.periodComboBox.setItemText(4, _translate("AddEmailDialog", "Months"))
        self.periodComboBox.setItemText(5, _translate("AddEmailDialog", "Years"))
