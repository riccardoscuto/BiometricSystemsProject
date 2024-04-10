import cv2
import os
import numpy as np
from PIL import Image
import dlib
import tkinter as tk
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow,QTableWidget,QInputDialog, QPushButton, QHBoxLayout, QTextEdit, QFormLayout, QListWidget, QDialogButtonBox, QListWidgetItem, QApplication, QWidget, QLabel, QGridLayout, QVBoxLayout, QCalendarWidget, QDialog, QComboBox, QLineEdit, QMessageBox
import datetime
from functools import partial
import cv2 as cv
from EyeBlinkCount import checkBlink
centroid = (0, 0)
radius = 0
current_eye = 0
eyes_list = []

class InputDialog_Register(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Register User")
        self.first = QLineEdit(self)
        self.second = QLineEdit(self)
        self.third = QLineEdit(self)
        self.fourth = QLineEdit(self)
        self.imageLabel = QLabel(self)
        self.imageLabel.setText("")
        self._r_in=None
        self._r_out=None
        self.imageLabel.setObjectName("label")
        self.imageLabel2 = QLabel(self)
        self.imageLabel2.setText("")
        self.imageLabel2.setPixmap(QtGui.QPixmap("bgLabel1.png"))
        self.imageLabel2.setObjectName("label2")
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self);
        layout = QFormLayout(self)
        layout.addRow("ID:", self.first)
        layout.addRow("Name:", self.second)
        layout.addRow("Age:", self.third)
        layout.addRow("blink:", self.fourth)
        layout.addRow("", self.imageLabel)
        layout.addWidget(buttonBox)
        self.imageLabel2.hide()
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
    def accept(self):
        eyeimage = self.imageLabel2.pixmap().toImage()
        width = eyeimage.width()
        height = eyeimage.height()
        s = eyeimage.bits().asstring(width * height * 4)  # 4 per RGBA
        eyeArray = np.frombuffer(s, dtype=np.uint8).reshape((height, width, 4))
        im = Image.fromarray(eyeArray).convert('RGBA')
        # im = cv.imread("S1001L01.jpg")
        open_cv_image = np.array(im)
        open_cv_image = open_cv_image[:, :, :3]  
        irideSegmentata, _x, _y, _r = segmenta_iride(open_cv_image)
        if irideSegmentata is None or _x is None or _y is None or _r is None:
            self.showError("No iris found. Please make sure the image is clear and try again.")
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText(" occhio fallito")
            msg.setInformativeText(f"occhio nuovo #{self.first.text()} has been registered to the database.")
            msg.setWindowTitle("User user uyser")
            msg.setStandardButtons(QMessageBox.Ok)
            retval = msg.exec_()
            self.done(0)
            return

        polar_iris = get_polar_to_cart_img(irideSegmentata, (_x, _y), 20, _r, _r*2, _r*2 )
        save_path = f"database/{self.first.text()}-{self.second.text()}-{self.third.text()}-{self.fourth.text()}.png"
        cv2.imwrite(save_path,  polar_iris)  # Assumendo che 'features' sia un'immagine
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Registered")
        msg.setInformativeText(f"User #{self.first.text()} has been registered to the database.")
        msg.setWindowTitle("User Registration")
        msg.setStandardButtons(QMessageBox.Ok)
        password_dialog = PasswordDialog(self.first.text(), self)
        password_dialog.exec_()
        retval = msg.exec_()
        self.done(0)

    def set_image(self, image_frame, image_frame2):
        self.imageLabel2.setPixmap(QtGui.QPixmap(image_frame2))
        self.imageLabel.setPixmap(QtGui.QPixmap(image_frame))

class InputDialog_Verify(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("User Information")
        self.first = QLineEdit(self)
        self.second = QLineEdit(self)
        self.third = QLineEdit(self)
        self.fourth = QLineEdit(self)
        self.first.setDisabled(True)
        self.second.setDisabled(True)
        self.third.setDisabled(True)
        self.fourth.setDisabled(True)
        self.imageLabel = QLabel(self)
        self.imageLabel.setText("")
        self.imageLabel.setPixmap(QtGui.QPixmap("bgLabel1.png"))
        self.imageLabel.setObjectName("label")
        self.imageLabel2 = QLabel(self)
        self.imageLabel2.setText("")
        self.imageLabel2.setPixmap(QtGui.QPixmap("bgLabel1.png"))
        self.imageLabel2.setObjectName("label2")
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok, self);
        layout = QFormLayout(self)
        layout.addRow("ID:", self.first)
        layout.addRow("Name:", self.second)
        layout.addRow("Age:", self.third)
        layout.addRow("blink:", self.fourth)
        layout.addRow("", self.imageLabel)
        layout.addWidget(buttonBox)
        self.imageLabel2.hide()
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
    def accept(self):
        #end
        self.done(0)
    def set_image(self, image_frame, image_frame2, idnum, namen, agen, blinkn):
        self.imageLabel2.setPixmap(QtGui.QPixmap(image_frame2))
        self.imageLabel.setPixmap(QtGui.QPixmap(image_frame))
        self.first.setText(idnum)
        self.second.setText(namen)
        self.third.setText(agen)
        self.fourth.setText(blinkn)
class Ui_IrisWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(456, 330)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setGeometry(QtCore.QRect(0, 0, 451, 331))
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap("bgLabel1.png"))
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.pushButton = QtWidgets.QPushButton(self.groupBox)
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout.addWidget(self.pushButton)
        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton.setText(_translate("MainWindow", "Register"))
        
class PasswordDialog(QDialog):
    def __init__(self, user_id, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.setWindowTitle("Password Manager")
        self.textEdit = QTextEdit(self)
        saveButton = QPushButton("Save", self)
        layout = QVBoxLayout(self)
        layout.addWidget(self.textEdit)
        layout.addWidget(saveButton)
        saveButton.clicked.connect(self.save_passwords)
    def save_passwords(self):
        passwords = self.textEdit.toPlainText()
        self.encrypt_and_save_passwords(self.user_id, passwords)
        QMessageBox.information(self, "Success", "Passwords saved successfully!")
        self.accept()
    def encrypt_and_save_passwords(self, user_id, passwords):
        with open(f"passwords_{user_id}.txt", "w") as file:
            file.write(passwords)
        
class PasswordsShow(QDialog):
    def __init__(self, user_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Your Passwords")
        layout = QVBoxLayout(self)
        self.passwordsList = QTextEdit()
        self.passwordsList.setReadOnly(True)
        layout.addWidget(self.passwordsList)
        self.load_and_display_passwords(user_id)
    def load_and_display_passwords(self, user_id):
        try:
            with open(f"passwords_{user_id}.txt", "r") as file:
                passwords = file.read()
                self.passwordsList.setText(passwords)
        except FileNotFoundError:
            QMessageBox.warning(self, "Error", "No passwords found for this user.")


class Ui_MainWindow(QWidget):
    is_register = 0 
    is_verify = 0 
    cap = None  
    root = None 
    popup_window = None
    uiiris = None
    popup_register_window = None
    popup_verify_window = None
    uiregis = None
    uiverify = None
    image_frame = None
    image_frame2 = None
    verify_id = ""
    def popup_setup(self):
        global popup_window
        global uiiris
        self.popup_window = QtWidgets.QMainWindow()
        self.uiiris = Ui_IrisWindow()
        self.uiiris.setupUi(self.popup_window)
        self.popup_window.setWindowFlags(Qt.FramelessWindowHint)
    def register_dialog_setup(self):
        global popup_register_window
        global uiregis
        self.popup_register_window = QtWidgets.QMainWindow()
        self.uiregis = InputDialog_Register()

    def verify_dialog_setup(self):
        global popup_verify_window
        global uiverify
        self.popup_verify_window = QtWidgets.QMainWindow()
        self.uiverify = InputDialog_Verify()

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1140, 700)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout_2.addWidget(self.pushButton)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.pushButton_7 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_7.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_7.sizePolicy().hasHeightForWidth())
        self.pushButton_7.setSizePolicy(sizePolicy)
        self.pushButton_7.setAutoFillBackground(False)
        self.pushButton_7.setCheckable(False)
        self.pushButton_7.setDefault(False)
        self.pushButton_7.setFlat(True)
        self.pushButton_7.setObjectName("pushButton_7")
        self.verticalLayout_4.addWidget(self.pushButton_7)
        self.RegisterUserButton = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.RegisterUserButton.sizePolicy().hasHeightForWidth())
        self.RegisterUserButton.setSizePolicy(sizePolicy)
        self.RegisterUserButton.setObjectName("RegisterUserButton")
        self.verticalLayout_4.addWidget(self.RegisterUserButton)
        self.VerifyUserButton = QtWidgets.QPushButton(self.centralwidget)
        self.VerifyUserButton.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.VerifyUserButton.sizePolicy().hasHeightForWidth())
        self.VerifyUserButton.setSizePolicy(sizePolicy)
        self.VerifyUserButton.setObjectName("VerifyUserButton")
        self.verticalLayout_4.addWidget(self.VerifyUserButton)
        self.ShowRegisteredUsers = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ShowRegisteredUsers.sizePolicy().hasHeightForWidth())
        self.ShowRegisteredUsers.setSizePolicy(sizePolicy)
        self.ShowRegisteredUsers.setObjectName("ShowRegisteredUsers")
        self.verticalLayout_4.addWidget(self.ShowRegisteredUsers)
        self.CloseProgramButton = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.CloseProgramButton.sizePolicy().hasHeightForWidth())
        self.CloseProgramButton.setSizePolicy(sizePolicy)
        self.CloseProgramButton.setObjectName("CloseProgramButton")
        self.verticalLayout_4.addWidget(self.CloseProgramButton)
        self.horizontalLayout_2.addLayout(self.verticalLayout_4)
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setContentsMargins(0, -1, -1, -1)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.statusPrompt = QtWidgets.QPushButton(self.centralwidget)
        self.statusPrompt.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.statusPrompt.sizePolicy().hasHeightForWidth())
        self.statusPrompt.setSizePolicy(sizePolicy)
        self.statusPrompt.setCheckable(False)
        self.statusPrompt.setAutoDefault(False)
        self.statusPrompt.setDefault(False)
        self.statusPrompt.setFlat(False)
        self.statusPrompt.setObjectName("statusPrompt")
        self.gridLayout_3.addWidget(self.statusPrompt, 4, 0, 1, 3)
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setText("")
        self.label_3.setPixmap(QtGui.QPixmap("bgLabel1.png"))
        self.label_3.setScaledContents(True)
        self.label_3.setObjectName("label_3")
        self.gridLayout_3.addWidget(self.label_3, 3, 2, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setText("")
        self.label_2.setPixmap(QtGui.QPixmap("bgLabel1.png"))
        self.label_2.setScaledContents(True)
        self.label_2.setObjectName("label_2")
        self.gridLayout_3.addWidget(self.label_2, 0, 2, 2, 1)
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap("bgLabel1.png"))
        self.label.setScaledContents(True)
        self.label.setObjectName("label")
        self.gridLayout_3.addWidget(self.label, 0, 0, 4, 1)
        self.horizontalLayout_2.addLayout(self.gridLayout_3)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.toolBar = QtWidgets.QToolBar(MainWindow)
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.actionClose = QtWidgets.QAction(MainWindow)
        self.actionClose.setObjectName("actionClose")
        self.actionClose_2 = QtWidgets.QAction(MainWindow)
        self.actionClose_2.setObjectName("actionClose_2")
        self.actionAbout = QtWidgets.QAction(MainWindow)
        self.actionAbout.setShortcutVisibleInContextMenu(False)
        self.actionAbout.setObjectName("actionAbout")
        self.actionRegister = QtWidgets.QAction(MainWindow)
        self.actionRegister.setObjectName("actionRegister")
        self.actionVerify = QtWidgets.QAction(MainWindow)
        self.actionVerify.setObjectName("actionVerify")
        self.actionShow_All = QtWidgets.QAction(MainWindow)
        self.actionShow_All.setObjectName("actionShow_All")
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Iris Recognition Registration Database"))
        self.pushButton.setText(_translate("MainWindow", "Iris Registered Database"))
        self.pushButton_7.setText(_translate("MainWindow", "Registered ID: XXXXXXX"))
        self.RegisterUserButton.setText(_translate("MainWindow", "Register User"))
        self.VerifyUserButton.setText(_translate("MainWindow", "Verify User"))
        self.ShowRegisteredUsers.setText(_translate("MainWindow", "Show Registered Users"))
        self.CloseProgramButton.setText(_translate("MainWindow", "Close"))
        self.statusPrompt.setText(_translate("MainWindow", "Registered. OK."))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar"))
        self.actionClose.setText(_translate("MainWindow", "Close"))
        self.actionClose_2.setText(_translate("MainWindow", "Close"))
        self.actionAbout.setText(_translate("MainWindow", "About"))
        self.actionRegister.setText(_translate("MainWindow", "Register"))
        self.actionVerify.setText(_translate("MainWindow", "Verify"))
        self.actionShow_All.setText(_translate("MainWindow", "Show All"))        
        
    def iris_match_res(self, image_1, image_2):
        orb = cv2.ORB_create(fastThreshold=0, edgeThreshold=0)
        keypoints_img1, des1 = orb.detectAndCompute(image_1, None)
        keypoints_img2, des2 = orb.detectAndCompute(image_2, None) 
        brute_f = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matchesOriginal = brute_f.match(des1, des1)  
        matchesNew = brute_f.match(des1, des2)  
        matching_result = cv2.drawMatches(image_1, keypoints_img1, image_2, keypoints_img2, matchesNew, None)

        if len(matchesOriginal) != 0:
            match_rate = (len(matchesNew)/len(matchesOriginal))*100
        else:
            match_rate = 0
            print("Image Quality is low definition, unable to verify. please use a stronger camera.")
        if match_rate > 18:
            print("IRIS MATCH FOUND IN DATABASE.")
            print("il mr è ", match_rate)
            cv2.imshow("matching", cv2.resize(matching_result, (700, 700)))

            return True
        else:
            print("NO IRIS MATCH FOUND IN DATABASE.")
            print("il mr è ", match_rate)
            return False
        
    def register_dialog_open_verify(self):
        inp = QtWidgets.QInputDialog(self)
        inp.setInputMode(QtWidgets.QInputDialog.TextInput)
        inp.setFixedSize(600, 100)
        inp.setWindowTitle('Confirmation')
        inp.setLabelText('Enter Identification Number')
        if inp.exec_() == QtWidgets.QDialog.Accepted:
            global verify_id
            verify_id = inp.textValue()
            ui.show_user_verification_info()
        else:
            print('cancel')
        inp.deleteLater()
    def show_user_verification_info(self):
        is_matched = False 
        iris_f_name = ""
        iris_id = ""
        iris_name = ""
        iris_age = ""
        iris_blink = ""
        for f_name in os.listdir('database'):
            image_name = f_name
            get_id_from_database = image_name.split("-")
            if verify_id.strip() == get_id_from_database[0].strip():
                iris_f_name = f_name
                iris_id = get_id_from_database[0].strip()
                iris_name = get_id_from_database[1].strip()
                iris_age = get_id_from_database[2].strip()
                iris_blink = get_id_from_database[3].strip().split(".")[0].strip()
                break
        incomingImage = self.image_frame2.convertToFormat(4)
        print(incomingImage)
        width = incomingImage.width()
        height = incomingImage.height()
        ptr = incomingImage.bits()
        ptr.setsize(incomingImage.byteCount())
        arr = np.array(ptr).reshape(height, width, 4)
        irideSegmentata, _x, _y, _r = segmenta_iride(arr)
        if irideSegmentata is None or _x is None or _y is None or _r is None:
            print("Errore.")
            return

        polar_iris = get_polar_to_cart_img(irideSegmentata, (_x, _y), 20, _r, _r*2, _r*2 )
        cv2.imwrite('database\\tempfile.png', polar_iris)
        # image_1 = cv2.imread('database\\tempfile.jpg')
        image_1 = cv2.imread('database\\tempfile.png')
        image_2 = cv2.imread('database\\' + iris_f_name) 
        # os.remove('database\\tempfile.png')
        is_matched = ui.iris_match_res(image_1, image_2)
        
        if is_matched == True:
            if iris_id:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText("Results:")
                msg.setInformativeText("IRIS MATCH FOUND IN DATABASE.")
                msg.setWindowTitle("User Confirmation")    
                msg.setStandardButtons(QMessageBox.Ok)
                retval = msg.exec_()
                if checkBlink(iris_blink):
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Information)
                    msg.setText("Identificazione Riuscita")
                    msg.setInformativeText("Blink Corrispontedenti ")
                    msg.setWindowTitle("")
                    msg.setStandardButtons(QMessageBox.Ok)
                    retval = msg.exec_()
                    passwords_dialog = PasswordsShow(iris_id)  
                    passwords_dialog.exec_()
                    self.uiverify.set_image('database\\' + iris_f_name, 'database\\' + iris_f_name, iris_id, iris_name, iris_age, iris_blink) 
                    self.uiverify.exec()
                    
                else:
                            
                            msg = QMessageBox()
                            msg.setIcon(QMessageBox.Warning)
                            msg.setText("Blink non corrispontendi")
                            msg.setInformativeText("Autenticazione fallita.")
                            msg.setWindowTitle("Error")
                            msg.setStandardButtons(QMessageBox.Ok)
                            retval = msg.exec_()
            else:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText("Verification Failed")
                msg.setInformativeText("No matching iris ID found in database.")
                msg.setWindowTitle("Verification Error")
                msg.setStandardButtons(QMessageBox.Ok)
                retval = msg.exec_()
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Results:")
            msg.setInformativeText("NO IRIS MATCH FOUND IN DATABASE.")
            msg.setWindowTitle("User Confirmation")
            msg.setStandardButtons(QMessageBox.Ok)
            retval = msg.exec_()
    def register_dialog_open_register(self):
        if self.image_frame is not None:
            self.uiregis.set_image(self.image_frame, self.image_frame2)
        self.uiregis.exec()
    def CloseProgram(self):
        if self.root is not None:
            self.root.destroy()
            self.root = None
        if self.cap is not None:
            self.cap.release()
        cv2.destroyAllWindows()
        self.popup_window.close()
        QCoreApplication.quit()
    def RegisterEyes(self):
        if self.is_verify == 0:
            self.uiiris.pushButton.setText('Register')
            if self.is_register == 0:
                self.uiiris.pushButton.clicked.disconnect()
                self.uiiris.pushButton.clicked.connect(ui.register_dialog_open_register)
                self.is_register = 1
            elif self.is_register == 1:
                self.is_register = 0
            if self.is_register == 1:
                if self.root is None:
                    self.root = tk.Tk()
                self.RegisterUserButton.setStyleSheet('QPushButton {background-color: #A3C1DA}')
                self.RegisterUserButton.setText('STOP')
                self.cap = cv2.VideoCapture(1)
                show_poly = 1 
                show_align_text = 1 
                detector = dlib.get_frontal_face_detector()  
                predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat") 
                numid = 0
                id = 1
                ret,frame = self.cap.read(); 
                self.popup_window.show()
                screen_width = self.root.winfo_screenwidth()
                screen_height = self.root.winfo_screenheight()
                self.popup_window.move(int(screen_width/2),int(screen_height/4))
                while(self.is_register == 1):
                    ret,frame = self.cap.read(); 
                    height, width, channel = frame.shape
                    bytesPerLine = 3 * width
                    offset = 100 
                    cv2.rectangle(frame, (offset+40,offset), (int(width)-offset-40,int(height)-offset), (255,255,255), 1) 
                    if show_align_text == 1:
                        cv2.putText(frame, 'Align Face in Center. Tracking...', (offset+40, offset-30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2) #show text
                    cv2.cvtColor(frame,cv2.COLOR_BGR2RGB, frame) 
                    tempframe = frame.copy()
                    overlay = frame.copy()
                    output = frame.copy()
                    height, width, channel = frame.shape
                    alpha = 0
                    cv2.rectangle(overlay, (0, 0), (width, height), (102,178,250), -1)
                    cv2.addWeighted(overlay, alpha, output, 1 - alpha, 0, output)
                    tempframe = output
                    overlay = frame.copy()
                    output = frame.copy()
                    height, width, channel = frame.shape
                    alpha = 0.5
                    cv2.rectangle(overlay, (0, 0), (width, height), (102,178,250), -1)
                    cv2.addWeighted(overlay, alpha, output, 1 - alpha, 0, output)
                    frame = output
                    qImg = QtGui.QImage(frame.data, width, height, bytesPerLine, QtGui.QImage.Format_RGB888)
                    self.label.setPixmap(QtGui.QPixmap(qImg))
                    gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY) 
                    faces = detector(gray)
                    for face in faces:
                        x, y  = face.left(), face.top() 
                        x1, y1 = face.right(), face.bottom() 
                        cv2.rectangle(frame, (x-20,y-20), (x1+20,y1+20), (255,255,255), 1) 
                        cv2.line(frame, (x+10, y-20), (x+65, y-55), (255,255,255), 1)
                        cv2.putText(frame, 'REGISTER USER', (x+70, y-60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2) 
                        poslandmarkpoints = predictor(gray, face)
                        global image_frame
                        global image_frame2
                        self.image_frame2 = begin_iristracking(tempframe, poslandmarkpoints, self.uiiris.label, False)
                        self.image_frame = begin_iristracking(frame, poslandmarkpoints, self.uiiris.label, True) 
                        ret,frame = self.cap.read(); 
                        height, width, channel = frame.shape
                        bytesPerLine = 3 * width
                        offset = 100 
                        cv2.rectangle(frame, (offset+40,offset), (int(width)-offset-40,int(height)-offset), (255,255,255), 1) 
                        if show_align_text == 1:
                            cv2.putText(frame, 'Align Face in Center. Tracking...', (offset+40, offset-30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2) 
                        cv2.cvtColor(frame,cv2.COLOR_BGR2RGB, frame) 
                        qImg = QtGui.QImage(frame.data, width, height, bytesPerLine, QtGui.QImage.Format_RGB888)
                        self.label.setPixmap(QtGui.QPixmap(qImg))
                        gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY) 
                        faces = detector(gray) 
                        x, y  = face.left(), face.top() 
                        x1, y1 = face.right(), face.bottom()
                        cv2.rectangle(frame, (x-20,y-20), (x1+20,y1+20), (255,255,255), 1) 
                        cv2.line(frame, (x+10, y-20), (x+65, y-55), (255,255,255), 1)
                        cv2.putText(frame, 'REGISTER USER', (x+70, y-60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)                    
                        poslandmarkpoints = predictor(gray, face)      
                        overlay = frame.copy()
                        output = frame.copy()
                        height, width, channel = frame.shape
                        alpha = 0.5
                        cv2.rectangle(overlay, (0, 0), (width, height), (102,178,250), -1)
                        cv2.addWeighted(overlay, alpha, output, 1 - alpha, 0, output)
                        frame = output
                        begin_eyetracking(frame, poslandmarkpoints, self.label_2, self.label_3, self.root)
                        ret,frame = self.cap.read(); 
                        height, width, channel = frame.shape
                        bytesPerLine = 3 * width
                        offset = 100 
                        cv2.rectangle(frame, (offset+40,offset), (int(width)-offset-40,int(height)-offset), (255,255,255), 1) 
                        if show_align_text == 1:
                            cv2.putText(frame, 'Align Face in Center. Tracking...', (offset+40, offset-30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2) 
                        cv2.cvtColor(frame,cv2.COLOR_BGR2RGB, frame) 
                        qImg = QtGui.QImage(frame.data, width, height, bytesPerLine, QtGui.QImage.Format_RGB888)
                        self.label.setPixmap(QtGui.QPixmap(qImg))
                        gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY) 
                        faces = detector(gray) 
                        x, y  = face.left(), face.top() 
                        x1, y1 = face.right(), face.bottom() 
                        cv2.rectangle(frame, (x-20,y-20), (x1+20,y1+20), (255,255,255), 1)
                        cv2.line(frame, (x+10, y-20), (x+65, y-55), (255,255,255), 1)
                        cv2.putText(frame, 'REGISTER USER', (x+70, y-60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)              
                        poslandmarkpoints = predictor(gray, face)
                        overlay = frame.copy()
                        output = frame.copy()
                        height, width, channel = frame.shape
                        alpha = 0.5
                        cv2.rectangle(overlay, (0, 0), (width, height), (102,178,250), -1)
                        cv2.addWeighted(overlay, alpha, output, 1 - alpha, 0, output)
                        frame = output
                        if show_poly == 1:
                            show_polyface(frame, poslandmarkpoints)
                        height, width, channel = frame.shape
                        bytesPerLine = 3 * width
                        qImg = QtGui.QImage(frame.data, width, height, bytesPerLine, QtGui.QImage.Format_RGB888)
                        self.label.setPixmap(QtGui.QPixmap(qImg))
                    if not faces:
                        show_align_text = 1
                    if faces:
                        show_align_text = 0
                    cv2.waitKey(1)
            else:
                if self.root is not None:
                    self.root.destroy()
                    self.root = None
                self.cap.release() 
                self.cap = None
                cv2.destroyAllWindows()
                if self.root is not None:
                    self.root.destroy()
                self.popup_window.close()
                self.RegisterUserButton.setStyleSheet('QPushButton {background-color: #E1E1E1}')
                self.RegisterUserButton.setText('Register User')
    def VerifyEyes(self):
        if self.is_register == 0:
            self.uiiris.pushButton.setText('Verify')
            if self.is_verify == 0:
                self.uiiris.pushButton.clicked.disconnect()
                self.uiiris.pushButton.clicked.connect(ui.register_dialog_open_verify)
                self.is_verify = 1
            elif self.is_verify == 1:
                self.is_verify = 0
            if self.is_verify == 1:
                if self.root is None:
                    self.root = tk.Tk()
                self.VerifyUserButton.setStyleSheet('QPushButton {background-color: #A3C1DA}')
                self.VerifyUserButton.setText('STOP')
                self.cap = cv2.VideoCapture(1); 
                show_poly = 1 
                show_align_text = 1 
                detector = dlib.get_frontal_face_detector() 
                predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
                numid = 0;
                id = 1;
                ret,frame = self.cap.read(); 
                self.popup_window.show()
                screen_width = self.root.winfo_screenwidth()
                screen_height = self.root.winfo_screenheight()
                self.popup_window.move(int(screen_width/2),int(screen_height/4))
                while(self.is_verify == 1):
                                    
                    ret,frame = self.cap.read(); 
                    if frame is  None:
                        self.is_verify=0
                        break
                    height, width, channel = frame.shape
                    bytesPerLine = 3 * width
                    offset = 100 
                    cv2.rectangle(frame, (offset+40,offset), (int(width)-offset-40,int(height)-offset), (255,255,255), 1) 
                    if show_align_text == 1:
                        cv2.putText(frame, 'Align Face in Center. Tracking...', (offset+40, offset-30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2) 
                    cv2.cvtColor(frame,cv2.COLOR_BGR2RGB, frame)
                    tempframe = frame.copy()
                    overlay = frame.copy()
                    output = frame.copy()
                    height, width, channel = frame.shape
                    alpha = 0
                    cv2.rectangle(overlay, (0, 0), (width, height), (102,178,250), -1)
                    cv2.addWeighted(overlay, alpha, output, 1 - alpha, 0, output)
                    tempframe = output    
                    overlay = frame.copy()
                    output = frame.copy()
                    height, width, channel = frame.shape
                    alpha = 0.5
                    cv2.rectangle(overlay, (0, 0), (width, height), (102,178,250), -1)
                    cv2.addWeighted(overlay, alpha, output, 1 - alpha, 0, output)
                    frame = output
                    qImg = QtGui.QImage(frame.data, width, height, bytesPerLine, QtGui.QImage.Format_RGB888)
                    self.label.setPixmap(QtGui.QPixmap(qImg))
                    gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY) 
                    faces = detector(gray) 
                    for face in faces:
                        x, y  = face.left(), face.top() 
                        x1, y1 = face.right(), face.bottom() 
                        cv2.rectangle(frame, (x-20,y-20), (x1+20,y1+20), (255,255,255), 1) 
                        cv2.line(frame, (x+10, y-20), (x+65, y-55), (255,255,255), 1)
                        cv2.putText(frame, 'REGISTER USER', (x+70, y-60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2) 
                        poslandmarkpoints = predictor(gray, face)
                        global image_frame
                        global image_frame2
                        self.image_frame2 = begin_iristracking(tempframe, poslandmarkpoints, self.uiiris.label, False) 
                        self.image_frame = begin_iristracking(frame, poslandmarkpoints, self.uiiris.label, True) 
                        ret,frame = self.cap.read(); 
                        height, width, channel = frame.shape
                        bytesPerLine = 3 * width
                        offset = 100
                        cv2.rectangle(frame, (offset+40,offset), (int(width)-offset-40,int(height)-offset), (255,255,255), 1) 
                        if show_align_text == 1:
                            cv2.putText(frame, 'Align Face in Center. Tracking...', (offset+40, offset-30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2) 
                        cv2.cvtColor(frame,cv2.COLOR_BGR2RGB, frame) 
                        qImg = QtGui.QImage(frame.data, width, height, bytesPerLine, QtGui.QImage.Format_RGB888)
                        self.label.setPixmap(QtGui.QPixmap(qImg))
                        gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY) 
                        faces = detector(gray) 
                        x, y  = face.left(), face.top() 
                        x1, y1 = face.right(), face.bottom() 
                        cv2.rectangle(frame, (x-20,y-20), (x1+20,y1+20), (255,255,255), 1) 
                        cv2.line(frame, (x+10, y-20), (x+65, y-55), (255,255,255), 1)
                        cv2.putText(frame, 'REGISTER USER', (x+70, y-60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)                     
                        poslandmarkpoints = predictor(gray, face)    
                        overlay = frame.copy()
                        output = frame.copy()
                        height, width, channel = frame.shape
                        alpha = 0.5
                        cv2.rectangle(overlay, (0, 0), (width, height), (102,178,250), -1)
                        cv2.addWeighted(overlay, alpha, output, 1 - alpha, 0, output)
                        frame = output
                        begin_eyetracking(frame, poslandmarkpoints, self.label_2, self.label_3, self.root)
                        ret,frame = self.cap.read(); 
                        height, width, channel = frame.shape
                        bytesPerLine = 3 * width
                        offset = 100 
                        cv2.rectangle(frame, (offset+40,offset), (int(width)-offset-40,int(height)-offset), (255,255,255), 1) 
                        if show_align_text == 1:
                            cv2.putText(frame, 'Align Face in Center. Tracking...', (offset+40, offset-30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2) 
                        cv2.cvtColor(frame,cv2.COLOR_BGR2RGB, frame) 
                        qImg = QtGui.QImage(frame.data, width, height, bytesPerLine, QtGui.QImage.Format_RGB888)
                        self.label.setPixmap(QtGui.QPixmap(qImg))
                        gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY) 
                        faces = detector(gray) 
                        x, y  = face.left(), face.top() 
                        x1, y1 = face.right(), face.bottom() 
                        cv2.rectangle(frame, (x-20,y-20), (x1+20,y1+20), (255,255,255), 1) 
                        cv2.line(frame, (x+10, y-20), (x+65, y-55), (255,255,255), 1)
                        cv2.putText(frame, 'REGISTER USER', (x+70, y-60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)                    
                        poslandmarkpoints = predictor(gray, face)    
                        overlay = frame.copy()
                        output = frame.copy()
                        height, width, channel = frame.shape
                        alpha = 0.5
                        cv2.rectangle(overlay, (0, 0), (width, height), (102,178,250), -1)
                        cv2.addWeighted(overlay, alpha, output, 1 - alpha, 0, output)
                        frame = output
                        if show_poly == 1:
                            show_polyface(frame, poslandmarkpoints)
                        height, width, channel = frame.shape
                        bytesPerLine = 3 * width
                        qImg = QtGui.QImage(frame.data, width, height, bytesPerLine, QtGui.QImage.Format_RGB888)
                        self.label.setPixmap(QtGui.QPixmap(qImg))
                    if not faces:
                        show_align_text = 1
                    if faces:
                        show_align_text = 0
                    cv2.waitKey(1)
            else:
                if self.root is not None:
                    self.root.destroy()
                    self.root = None
                self.cap.release() 
                self.cap = None
                cv2.destroyAllWindows()
                if self.root is not None:
                    self.root.destroy()
                #close popup
                self.popup_window.close()
                self.VerifyUserButton.setStyleSheet('QPushButton {background-color: #E1E1E1}')
                self.VerifyUserButton.setText('Verify User')
    def ShowAllRegisteredUsers(self): 
        iris_f_name = ""
        iris_id = ""
        iris_name = ""
        iris_age = ""
        iris_blink = ""
        iris_date = ""
        path, dirs, files = next(os.walk('database'))
        num_users = len(files)  
        self.table = QTableWidget()
        self.table.setRowCount(num_users+30)
        self.table.setColumnCount(7)
        self.table.resize(1624, 800)
        self.table.setWindowTitle("REGISTERED USERS DATABASE")
        self.table.horizontalHeader().setStretchLastSection(True)
        col_headers = ['IDENTIF. #', 'NAME.', 'AGE.', 'blink.', 'DATE REGIST.', 'CURRENT REGIST.', 'INFO.']
        self.table.setHorizontalHeaderLabels(col_headers)
        self.table.show()
        row = 0
        for f_name in os.listdir('database'):
            image_name = f_name
            get_id_from_database = image_name.split("-")
            if len(get_id_from_database) < 4:  # Assicurati che ci siano abbastanza parti
                print(f"Il nome del file {f_name} non è nel formato previsto.")
                continue 
            iris_f_name = f_name
            iris_id = get_id_from_database[0].strip()
            iris_name = get_id_from_database[1].strip()
            iris_age = get_id_from_database[2].strip()
            iris_blink = get_id_from_database[3].strip().split(".")[0].strip()
            t = os.path.getmtime("database\\" + image_name)
            d = datetime.datetime.fromtimestamp(t)
            iris_date = d.strftime('%d-%m-%Y %H:%M:%S')
            if iris_id == ".png":
                iris_id = ""
            if iris_name == ".png":
                iris_name = ""
            if iris_age == ".png":
                iris_age = ""
            if iris_blink == ".png":
                iris_blink = ""
            if iris_date == ".png":
                iris_date = ""
            item = QtWidgets.QTableWidgetItem()
            item.setText(iris_id)
            self.table.setItem(row, 0, item)
            item = QtWidgets.QTableWidgetItem()
            item.setText(iris_name)
            self.table.setItem(row, 1, item)
            item = QtWidgets.QTableWidgetItem()
            item.setText(iris_age)
            self.table.setItem(row, 2, item)
            item = QtWidgets.QTableWidgetItem()
            item.setText(iris_blink)
            self.table.setItem(row, 3, item)
            item = QtWidgets.QTableWidgetItem()
            item.setText(iris_date)
            self.table.setItem(row, 4, item)
            item = QtWidgets.QTableWidgetItem()
            d = datetime.datetime.today()
            item.setText(d.strftime('%d-%m-%Y %H:%M:%S'))
            self.table.setItem(row, 5, item)
            infobutton = QPushButton("INFO")
            infobutton.clicked.connect(partial(self.open_info_dialog,iris_id))
            self.table.setCellWidget(row, 6, infobutton)
            row = row+1
    def open_info_dialog(self, selected_ID):
        temp_id = selected_ID
        iris_f_name = ""
        iris_id = ""
        iris_name = ""
        iris_age = ""
        iris_blink = ""
        for f_name in os.listdir('database'):
            image_name = f_name
            get_id_from_database = image_name.split("-")
            if temp_id == get_id_from_database[0].strip():
                iris_f_name = f_name
                iris_id = get_id_from_database[0].strip()
                iris_name = get_id_from_database[1].strip()
                iris_age = get_id_from_database[2].strip()
                iris_blink = get_id_from_database[3].strip().split(".")[0].strip()
                break
        self.uiverify.set_image('database\\' + iris_f_name, 'database\\' + iris_f_name, iris_id, iris_name, iris_age, iris_blink) 
        self.uiverify.exec()
def get_iris(frame):
        iris = []
        copy_img = frame.copy()
        res_img = frame.copy()
        gray_img = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        mask = np.zeros_like(gray_img)
        edges = cv.Canny(gray_img, 5, 70, 3)
        circles = get_circles(edges)
        iris.append(res_img)
        for circle in circles:
            rad = int(circle[0][2])
            global radius
            radius = rad
            cv.circle(mask, centroid, rad, (255, 255, 255), cv.FILLED)
            mask = cv.bitwise_not(mask)
            cv.subtract(frame, copy_img, res_img, mask)
            x = int(centroid[0] - rad)
            y = int(centroid[1] - rad)
            w = int(rad * 2)
            h = w
            crop_img = res_img[y:y + h, x:x + w].copy()
            return crop_img
        return res_img

def get_circles(image):
            i = 80
            while i < 151:
                circles = cv.HoughCircles(image, cv.HOUGH_GRADIENT, 2, 100.0,param1=30, param2=i, minRadius=100, maxRadius=140)
                if circles is not None and len(circles) == 1:
                    return circles
                i += 1
            return []
    

def segmenta_iride(im):
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    cerchi = cv2.HoughCircles(gray,cv2.HOUGH_GRADIENT,dp=1,minDist=20,param1=50,param2=30,minRadius=5,maxRadius=80,)
    print("cerchi", cerchi)
    if cerchi is not None:
        cerchi = np.round(cerchi[0, :]).astype("int")
        x, y, r = cerchi[0]
        maschera = np.zeros_like(gray)
        cv2.circle(maschera, (x, y), r, (255, 255, 255), -1)
        iride_segmentata = cv2.bitwise_and(im, im, mask=maschera)
        return iride_segmentata, x, y, r
    else:
        return None, None, None, None


def preprocess_image_for_recognition(image):
    # Converti l'immagine in scala di grigi
    # gray_image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
    
    # Migliora il contrasto dell'immagine
    # contrast_enhanced_image = cv2.convertScaleAbs(image, alpha=1.5, beta=10)
    # contrast_enhanced_image = cv2.equalizeHist(image)

    
    # Applica un filtro gaussiano per ridurre il rumore e migliorare il riconoscimento dei bordi
    # filtered_image = cv2.GaussianBlur(image, (1, 1), 0)
    
    return image

def daugman_normalization(image, center, r_in, r_out, width, height):
    thetas = np.linspace(0, 2 * np.pi, width)
    r = np.linspace(r_in, r_out, height)
    theta, radius = np.meshgrid(thetas, r)
    X = center[0] + radius * np.cos(theta)
    Y = center[1] + radius * np.sin(theta)
    polar_to_cartesian = cv.remap(image, X.astype(np.float32), Y.astype(np.float32), cv.INTER_LINEAR)
    return polar_to_cartesian

def get_polar_to_cart_img(image, center, r_in, r_out, width=360, height=60):
    normalized_iris = daugman_normalization(image, center, r_in, r_out, width, height)
    return normalized_iris
def show_polyface (frame, poslandmarkpoints):
    drawlinethickness = 1
    facetracking_color = (255,255,255)
    right_eye1x = poslandmarkpoints.part(38).x
    right_eye1y = poslandmarkpoints.part(38).y
    right_eye2x = poslandmarkpoints.part(41).x
    right_eye2y = poslandmarkpoints.part(41).y
    left_eye1x = poslandmarkpoints.part(44).x
    left_eye1y = poslandmarkpoints.part(44).y
    left_eye2x = poslandmarkpoints.part(47).x
    left_eye2y = poslandmarkpoints.part(47).y
    for p in range(0, 16):
        cv2.line(frame, (poslandmarkpoints.part(p).x, poslandmarkpoints.part(p).y), (poslandmarkpoints.part(p+1).x, poslandmarkpoints.part(p+1).y), facetracking_color, drawlinethickness)
    cv2.line(frame, (poslandmarkpoints.part(0).x, poslandmarkpoints.part(0).y), (poslandmarkpoints.part(17).x, poslandmarkpoints.part(17).y), facetracking_color, drawlinethickness)
    cv2.line(frame, (poslandmarkpoints.part(0).x, poslandmarkpoints.part(0).y), (poslandmarkpoints.part(36).x, poslandmarkpoints.part(36).y), facetracking_color, drawlinethickness)
    cv2.line(frame, (poslandmarkpoints.part(0).x, poslandmarkpoints.part(0).y), (poslandmarkpoints.part(31).x, poslandmarkpoints.part(31).y), facetracking_color, drawlinethickness)
    for p in range(36, 41):
        cv2.line(frame, (poslandmarkpoints.part(p).x, poslandmarkpoints.part(p).y), (poslandmarkpoints.part(p+1).x, poslandmarkpoints.part(p+1).y), facetracking_color, drawlinethickness)
    cv2.line(frame, (poslandmarkpoints.part(41).x, poslandmarkpoints.part(41).y), (poslandmarkpoints.part(36).x, poslandmarkpoints.part(36).y), facetracking_color, drawlinethickness) #close off line for left eye
    cv2.line(frame, (poslandmarkpoints.part(39).x, poslandmarkpoints.part(39).y), (poslandmarkpoints.part(27).x, poslandmarkpoints.part(27).y), facetracking_color, drawlinethickness) 
    cv2.line(frame, (poslandmarkpoints.part(39).x, poslandmarkpoints.part(39).y), (poslandmarkpoints.part(31).x, poslandmarkpoints.part(31).y), facetracking_color, drawlinethickness) 
    cv2.rectangle(frame, (left_eye1x-40,left_eye1y-20), (left_eye2x+40,left_eye2y+20), (255,0,0), 2)
    for p in range(42, 47):
        cv2.line(frame, (poslandmarkpoints.part(p).x, poslandmarkpoints.part(p).y), (poslandmarkpoints.part(p+1).x, poslandmarkpoints.part(p+1).y), facetracking_color, drawlinethickness)
    cv2.line(frame, (poslandmarkpoints.part(47).x, poslandmarkpoints.part(47).y), (poslandmarkpoints.part(42).x, poslandmarkpoints.part(42).y), facetracking_color, drawlinethickness) #close off line for right eye
    cv2.line(frame, (poslandmarkpoints.part(42).x, poslandmarkpoints.part(42).y), (poslandmarkpoints.part(27).x, poslandmarkpoints.part(27).y), facetracking_color, drawlinethickness) #close off line for left eye
    cv2.line(frame, (poslandmarkpoints.part(42).x, poslandmarkpoints.part(42).y), (poslandmarkpoints.part(35).x, poslandmarkpoints.part(35).y), facetracking_color, drawlinethickness) 
    cv2.rectangle(frame, (right_eye1x-40,right_eye1y-20), (right_eye2x+40,right_eye2y+20), (255,0,0), 2)
    for p in range(27, 35):
        cv2.line(frame, (poslandmarkpoints.part(p).x, poslandmarkpoints.part(p).y), (poslandmarkpoints.part(p+1).x, poslandmarkpoints.part(p+1).y), facetracking_color, drawlinethickness)
    cv2.line(frame, (poslandmarkpoints.part(35).x, poslandmarkpoints.part(35).y), (poslandmarkpoints.part(30).x, poslandmarkpoints.part(30).y), facetracking_color, drawlinethickness) #close off line for nose
    cv2.line(frame, (poslandmarkpoints.part(27).x, poslandmarkpoints.part(27).y), (poslandmarkpoints.part(31).x, poslandmarkpoints.part(31).y), facetracking_color, drawlinethickness) 
    cv2.line(frame, (poslandmarkpoints.part(27).x, poslandmarkpoints.part(27).y), (poslandmarkpoints.part(35).x, poslandmarkpoints.part(35).y), facetracking_color, drawlinethickness) 
    cv2.line(frame, (poslandmarkpoints.part(30).x, poslandmarkpoints.part(30).y), (poslandmarkpoints.part(32).x, poslandmarkpoints.part(32).y), facetracking_color, drawlinethickness) 
    cv2.line(frame, (poslandmarkpoints.part(30).x, poslandmarkpoints.part(30).y), (poslandmarkpoints.part(33).x, poslandmarkpoints.part(33).y), facetracking_color, drawlinethickness) 
    cv2.line(frame, (poslandmarkpoints.part(30).x, poslandmarkpoints.part(30).y), (poslandmarkpoints.part(34).x, poslandmarkpoints.part(34).y), facetracking_color, drawlinethickness) 
    cv2.line(frame, (poslandmarkpoints.part(33).x, poslandmarkpoints.part(33).y), (poslandmarkpoints.part(51).x, poslandmarkpoints.part(51).y), facetracking_color, drawlinethickness) 
    cv2.line(frame, (poslandmarkpoints.part(35).x, poslandmarkpoints.part(35).y), (poslandmarkpoints.part(54).x, poslandmarkpoints.part(54).y), facetracking_color, drawlinethickness) 
    cv2.line(frame, (poslandmarkpoints.part(31).x, poslandmarkpoints.part(31).y), (poslandmarkpoints.part(48).x, poslandmarkpoints.part(48).y), facetracking_color, drawlinethickness) 

    for p in range(48, 59):
        cv2.line(frame, (poslandmarkpoints.part(p).x, poslandmarkpoints.part(p).y), (poslandmarkpoints.part(p+1).x, poslandmarkpoints.part(p+1).y), facetracking_color, drawlinethickness)
    cv2.line(frame, (poslandmarkpoints.part(59).x, poslandmarkpoints.part(59).y), (poslandmarkpoints.part(48).x, poslandmarkpoints.part(48).y), facetracking_color, drawlinethickness) #close off line for right eye
    for p in range(60, 67):
        cv2.line(frame, (poslandmarkpoints.part(p).x, poslandmarkpoints.part(p).y), (poslandmarkpoints.part(p+1).x, poslandmarkpoints.part(p+1).y), facetracking_color, drawlinethickness)
    cv2.line(frame, (poslandmarkpoints.part(60).x, poslandmarkpoints.part(60).y), (poslandmarkpoints.part(67).x, poslandmarkpoints.part(67).y), facetracking_color, drawlinethickness) #close off line for right eye
    cv2.line(frame, (poslandmarkpoints.part(58).x, poslandmarkpoints.part(58).y), (poslandmarkpoints.part(7).x, poslandmarkpoints.part(7).y), facetracking_color, drawlinethickness)
    cv2.line(frame, (poslandmarkpoints.part(56).x, poslandmarkpoints.part(56).y), (poslandmarkpoints.part(9).x, poslandmarkpoints.part(9).y), facetracking_color, drawlinethickness) 
    cv2.line(frame, (poslandmarkpoints.part(48).x, poslandmarkpoints.part(48).y), (poslandmarkpoints.part(3).x, poslandmarkpoints.part(3).y), facetracking_color, drawlinethickness) 
    cv2.line(frame, (poslandmarkpoints.part(48).x, poslandmarkpoints.part(48).y), (poslandmarkpoints.part(6).x, poslandmarkpoints.part(6).y), facetracking_color, drawlinethickness) 
    cv2.line(frame, (poslandmarkpoints.part(2).x, poslandmarkpoints.part(2).y), (poslandmarkpoints.part(31).x, poslandmarkpoints.part(31).y), facetracking_color, drawlinethickness) 
    cv2.line(frame, (poslandmarkpoints.part(54).x, poslandmarkpoints.part(54).y), (poslandmarkpoints.part(13).x, poslandmarkpoints.part(13).y), facetracking_color, drawlinethickness) 
    cv2.line(frame, (poslandmarkpoints.part(54).x, poslandmarkpoints.part(54).y), (poslandmarkpoints.part(10).x, poslandmarkpoints.part(10).y), facetracking_color, drawlinethickness) 
    cv2.line(frame, (poslandmarkpoints.part(35).x, poslandmarkpoints.part(35).y), (poslandmarkpoints.part(14).x, poslandmarkpoints.part(14).y), facetracking_color, drawlinethickness) 
    cv2.line(frame, (poslandmarkpoints.part(35).x, poslandmarkpoints.part(35).y), (poslandmarkpoints.part(16).x, poslandmarkpoints.part(16).y), facetracking_color, drawlinethickness) 
    cv2.line(frame, (poslandmarkpoints.part(16).x, poslandmarkpoints.part(16).y), (poslandmarkpoints.part(45).x, poslandmarkpoints.part(45).y), facetracking_color, drawlinethickness) 
    cv2.line(frame, (poslandmarkpoints.part(16).x, poslandmarkpoints.part(16).y), (poslandmarkpoints.part(26).x, poslandmarkpoints.part(26).y), facetracking_color, drawlinethickness)
    for p in range(17, 21):
        cv2.line(frame, (poslandmarkpoints.part(p).x, poslandmarkpoints.part(p).y), (poslandmarkpoints.part(p+1).x, poslandmarkpoints.part(p+1).y), facetracking_color, drawlinethickness)
    for p in range(22, 26):
        cv2.line(frame, (poslandmarkpoints.part(p).x, poslandmarkpoints.part(p).y), (poslandmarkpoints.part(p+1).x, poslandmarkpoints.part(p+1).y), facetracking_color, drawlinethickness)
    cv2.line(frame, (poslandmarkpoints.part(21).x, poslandmarkpoints.part(21).y), (poslandmarkpoints.part(22).x, poslandmarkpoints.part(22).y), facetracking_color, drawlinethickness)
    cv2.line(frame, (poslandmarkpoints.part(19).x, poslandmarkpoints.part(19).y), (poslandmarkpoints.part(24).x, poslandmarkpoints.part(24).y), facetracking_color, drawlinethickness)
    cv2.line(frame, (poslandmarkpoints.part(18).x, poslandmarkpoints.part(18).y), (poslandmarkpoints.part(37).x, poslandmarkpoints.part(37).y), facetracking_color, drawlinethickness)
    cv2.line(frame, (poslandmarkpoints.part(21).x, poslandmarkpoints.part(21).y), (poslandmarkpoints.part(38).x, poslandmarkpoints.part(38).y), facetracking_color, drawlinethickness)
    cv2.line(frame, (poslandmarkpoints.part(21).x, poslandmarkpoints.part(21).y), (poslandmarkpoints.part(27).x, poslandmarkpoints.part(27).y), facetracking_color, drawlinethickness)
    cv2.line(frame, (poslandmarkpoints.part(22).x, poslandmarkpoints.part(22).y), (poslandmarkpoints.part(43).x, poslandmarkpoints.part(43).y), facetracking_color, drawlinethickness)
    cv2.line(frame, (poslandmarkpoints.part(25).x, poslandmarkpoints.part(25).y), (poslandmarkpoints.part(44).x, poslandmarkpoints.part(44).y), facetracking_color, drawlinethickness)
    cv2.line(frame, (poslandmarkpoints.part(22).x, poslandmarkpoints.part(22).y), (poslandmarkpoints.part(27).x, poslandmarkpoints.part(27).y), facetracking_color, drawlinethickness)

def begin_eyetracking (frame, poslandmarkpoints, label_2, label_3, root):

    left_eye1x = poslandmarkpoints.part(44).x
    left_eye1y = poslandmarkpoints.part(44).y
    left_eye2x = poslandmarkpoints.part(47).x
    left_eye2y = poslandmarkpoints.part(47).y
    right_eye1x = poslandmarkpoints.part(38).x
    right_eye1y = poslandmarkpoints.part(38).y
    right_eye2x = poslandmarkpoints.part(41).x
    right_eye2y = poslandmarkpoints.part(41).y
    leftEyeTrack = np.array([(left_eye1x-40,left_eye1y-20),(left_eye1x-40,left_eye2y+20),(left_eye2x+40,left_eye2y-20),(left_eye2x+40,left_eye2y+20)],np.int32)
    lemin_x = np.min(leftEyeTrack[:, 0])
    lemax_x = np.max(leftEyeTrack[:, 0])
    lemin_y = np.min(leftEyeTrack[:, 1])
    lemax_y = np.max(leftEyeTrack[:, 1])
    left_eye = frame[lemin_y : lemax_y, lemin_x : lemax_x]
    left_eye = cv2.resize(left_eye, None, fx = 5, fy = 5) 
    cv2.rectangle(frame, (left_eye1x-40,left_eye1y-20), (left_eye2x+40,left_eye2y+20), (255,0,0), 1)
    height, width, channel = left_eye.shape
    bytesPerLine = 3 * width
    qImg = QtGui.QImage(left_eye.data, width, height, bytesPerLine, QtGui.QImage.Format_RGB888)
    label_2.setPixmap(QtGui.QPixmap(qImg))

    rightEyeTrack = np.array([(right_eye1x-40,right_eye1y-20),(right_eye1x-40,right_eye2y+20),(right_eye2x+40,right_eye2y-20),(right_eye2x+40,right_eye2y+20)],
                            np.int32)
    remin_x = np.min(rightEyeTrack[:, 0])
    remax_x = np.max(rightEyeTrack[:, 0])
    remin_y = np.min(rightEyeTrack[:, 1])
    remax_y = np.max(rightEyeTrack[:, 1])
    cv2.putText(frame, 'RIGHT EYE', (right_eye2x-15 , right_eye2y+17), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255,255,255), 1) #show text
    right_eye = frame[remin_y : remax_y, remin_x : remax_x]
    right_eye = cv2.resize(right_eye, None, fx = 5, fy = 5) #fx and fy is the scale factor for frame
    cv2.rectangle(frame, (right_eye1x-40,right_eye1y-20), (right_eye2x+40,right_eye2y+20), (255,0,0), 1)
    height, width, channel = right_eye.shape
    bytesPerLine = 3 * width
    qImg = QtGui.QImage(right_eye.data, width, height, bytesPerLine, QtGui.QImage.Format_RGB888)
    label_3.setPixmap(QtGui.QPixmap(qImg))
def begin_iristracking(frame, poslandmarkpoints, popup, show_trackobj):
    right_eye1x = poslandmarkpoints.part(38).x
    right_eye1y = poslandmarkpoints.part(38).y
    right_eye2x = poslandmarkpoints.part(41).x
    right_eye2y = poslandmarkpoints.part(41).y
    remin_x2 = right_eye1x - 50
    remax_x2 = right_eye2x + 50
    remin_y2 = right_eye1y - 20
    remax_y2 = right_eye2y + 20
    right_eye_region = frame[remin_y2:remax_y2, remin_x2:remax_x2]
    preprocessed_eye = preprocess_image_for_recognition(right_eye_region)
    right_eye_resized = cv2.resize(preprocessed_eye, None, fx=5, fy=5)
    print("MIA", right_eye_resized.shape)
    height2, width2, level = right_eye_resized.shape
    bytesPerLine2 = width2
    qImg2 = QtGui.QImage(right_eye_resized.data, width2, height2, bytesPerLine2*level, QtGui.QImage.Format_RGB888)#qui prima era Greyqualcosa
    popup.setPixmap(QtGui.QPixmap(qImg2))
    return qImg2

def load_and_decrypt_passwords(user_id):
    try:
        with open(f"passwords_{user_id}.txt", "r") as file:
            encrypted_passwords = file.read()
        decrypted_passwords = decrypt_passwords(encrypted_passwords)
        return decrypted_passwords
    except FileNotFoundError:
        print(f"No passwords found for user ID {user_id}")
        return None

def decrypt_passwords(encrypted_passwords):
    decrypted_passwords = encrypted_passwords 
    return decrypted_passwords

def show_passwords_after_verification(user_id):
    passwords = load_and_decrypt_passwords(user_id)
    if passwords:
        print(passwords) 
    
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    ui.popup_setup() 
    ui.register_dialog_setup() 
    ui.verify_dialog_setup() 
    ui.RegisterUserButton.clicked.connect(ui.RegisterEyes)
    ui.VerifyUserButton.clicked.connect(ui.VerifyEyes)
    ui.CloseProgramButton.clicked.connect(ui.CloseProgram)
    ui.ShowRegisteredUsers.clicked.connect(ui.ShowAllRegisteredUsers)
    ui.uiiris.pushButton.clicked.connect(ui.register_dialog_open_register)
    MainWindow.showMaximized()
    sys.exit(app.exec_())