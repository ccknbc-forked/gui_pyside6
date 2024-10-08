# from PySide6 import QtWidgets
# from PySide6.QtUiTools import QUiLoader
# from PySide6.QtCore import QFile, QIODevice, Qt, QTimer
# from PySide6.QtGui import QPixmap, QImage

import PySide6

import sys, os
import cv2
import json
import re
from utils.ScreenKeyboard import InputHandler
from utils import UtilsVariables

# print(os.getcwd())
style = None
with open("ui/style/style_form.qss", "r") as file:
    style = file.read()



class EventSetting(PySide6.QtWidgets.QMainWindow):
    def __init__(self, w):
        super().__init__()
        self.w = w
        self.setCentralWidget(w)
        self.setWindowTitle("Event Settings")
        self.setStyleSheet(style)
        self.w.close_btn.clicked.connect(self.close)
        
        self.w.obj_track_btn.clicked.connect(lambda:self.show_popup(ObjTracking))

    def show_popup(self, PopupClass):
        print("Success!")
        loader = PySide6.QtUiTools.QUiLoader()
        ui_file = PySide6.QtCore.QFile("ui/admgui/all_ui/event_setting/object_realtime.ui")
        if not ui_file.open(PySide6.QtCore.QIODevice.ReadOnly):
            print(f"Cannot open UI file: {ui_file.errorString()}")
            return
        
        dialog = loader.load(ui_file, self)
        ui_file.close()
        self.popup = PopupClass(dialog)
        self.popup.show()
        self.close()
        


class ObjTracking(PySide6.QtWidgets.QMainWindow):
    def __init__(self, w):
        super().__init__()
        self.w = w
        self.setCentralWidget(w)
        self.setWindowTitle("Object Real-Time Tracking")
        self.setStyleSheet(style)
        self.w.close_btn.clicked.connect(self.close)
        self.w.person_select_btn.clicked.connect(self.select_form)
        self.w.person_newReg_btn.clicked.connect(self.new_registPerson)
        
        self.w.vehicle_select_btn.clicked.connect(self.select_form)
        self.w.vehicle_newReg_btn.clicked.connect(self.new_registVehicle)
        
        self.w.reset_btn.clicked.connect(self.reset_input)

        if UtilsVariables.keyboard_active and UtilsVariables.key_widget is not None:
            self.input_handler1 = InputHandler(UtilsVariables.key_widget)
            UtilsVariables.key_widget.key_pressed.connect(self.input_handler1.on_key_pressed)
            input_widgets = self.findChildren(PySide6.QtWidgets.QLineEdit) + self.findChildren(PySide6.QtWidgets.QTextEdit)
            for widget in input_widgets:
                widget.installEventFilter(self.input_handler1)
        
        self.cameralist = {
            "vid1": "vid/test1.mp4", 
            "vid2": "vid/test2.mp4", 
            "vid3": "vid/test3.mp4",
            "Channel 1 (IP: 192.168.45.166)": "rtsp://admin:aery2021!@192.168.45.166:554/cam/realmonitor?channel=1&subtype=0&unaicast=true&proto=Onvif",
            "Channel 2 (IP: 192.168.45.167)": "rtsp://admin:aery2021!@192.168.45.167:554/cam/realmonitor?channel=1&subtype=0&unaicast=true&proto=Onvif" 
        }
        self.cam_usage = None

        if not os.path.exists("./imgs/profile"):
            os.mkdir("./imgs/profile")
        self.imlen = len(os.listdir("./imgs/profile"))

        self.datas = dict()
        self.datas1 = []
        self.datas2 = []
        
        if os.path.exists('./datas/objTracking.json'):
            f = open('./datas/objTracking.json')
            self.datas = json.load(f)
        self.datas1 = self.datas["person"]
        self.datas2 = self.datas["vehicle"]

        self.filtered_datas = []
        
        completer_cam = PySide6.QtWidgets.QCompleter(list(self.cameralist.keys()))
        completer_cam.setCaseSensitivity(PySide6.QtCore.Qt.CaseInsensitive)
        self.w.camera_edit.setCompleter(completer_cam)
        completer_cam.popup().setStyleSheet("color:#37383E;")

        names = [item["name"] for item in self.datas1]
        completer_name = PySide6.QtWidgets.QCompleter(names)
        completer_name.setCaseSensitivity(PySide6.QtCore.Qt.CaseInsensitive)
        self.w.personName.setCompleter(completer_name)
        completer_name.popup().setStyleSheet("color:#37383E;")
        
        vahicles = [item["vehicle_no"] for item in self.datas2]
        completer_vahicle = PySide6.QtWidgets.QCompleter(vahicles)
        completer_vahicle.setCaseSensitivity(PySide6.QtCore.Qt.CaseInsensitive)
        self.w.noVehicle.setCompleter(completer_vahicle)
        completer_vahicle.popup().setStyleSheet("color:#37383E;")

        self.w.selectCam_btn.clicked.connect(self.selct_camera)
        self.w.startSearch_btn.clicked.connect(self.handle_filter)
        self.w.searchResult_btn.clicked.connect(self.show_filter)

        self.last_radiobutton_checked = None
        # self.w.groupbtnForm.buttonClicked.connect(self.check_button)
        
        # def check_button(self):
        #     self.last_radiobutton_checked = "Person" if self.w.person_radiobtn.isChecked() else "Vehicle" if self.w.vehicle_radiobtn.isChecked() else None


    def selct_camera(self):
        cam_id = self.w.camera_edit.text()
        if cam_id == "" or cam_id == " ":
            PySide6.QtWidgets.QMessageBox.critical(self, "Empty Fields", "All fields must be filled out.")
        elif cam_id not in list(self.cameralist.keys()):
            PySide6.QtWidgets.QMessageBox.critical(self, "Invalid Input", f"{cam_id} not exist")
        else:
            self.cam_usage = self.cameralist[cam_id]
            PySide6.QtWidgets.QMessageBox.information(self, "Success", f"Camera selected {cam_id}")


    def select_form(self):
        button = self.sender()

        loader = PySide6.QtUiTools.QUiLoader()
        ui_file = PySide6.QtCore.QFile("ui/admgui/all_ui/event_setting/select_data_dialog.ui")
        if not ui_file.open(PySide6.QtCore.QIODevice.ReadOnly):
            print(f"Cannot open UI file: {ui_file.errorString()}")
            return
        dialog = loader.load(ui_file, self)
        ui_file.close()
        self.popup = dialog
        self.popup.cancel_btn.clicked.connect(self.popup.close)
        self.popup.setWindowTitle("Select item")
        tb_show = self.popup.tb_show1

        # print(self.popup.frame_tb.layout())
        
        data_to_show = {}
        self.form = ""
        if button == self.w.person_select_btn:
            self.popup.label_head1.setText("Data Person")
            tb_show.setRowCount(len(self.datas1))
            tb_show.setColumnCount(len(self.datas1[0]))
            
            header = tb_show.horizontalHeader()
            header.setMinimumHeight(34)
            header.setDefaultAlignment(PySide6.QtCore.Qt.AlignCenter | PySide6.QtCore.Qt.Alignment(PySide6.QtCore.Qt.TextWordWrap))

            header_items = ["No.", "Name", "Img", "Gender", "Hairstyle", "attribute", "vehicle"]
            for i in range(tb_show.columnCount()):
                hItem = PySide6.QtWidgets.QTableWidgetItem(header_items[i])
                tb_show.setHorizontalHeaderItem(i, hItem)
                if i==0:
                    tb_show.setColumnWidth(0, 20)
                else:
                    header.setSectionResizeMode(i, PySide6.QtWidgets.QHeaderView.Stretch)
            data_to_show = self.datas1
            self.form = "Person"

            if data_to_show:
                for idx, data_num in enumerate(range(len(data_to_show))):
                    for i, (key, value) in enumerate(data_to_show[data_num].items()):
                        if key == "id":
                            it = PySide6.QtWidgets.QTableWidgetItem(str(idx+1))
                            it.setTextAlignment(PySide6.QtCore.Qt.AlignCenter)
                            tb_show.setItem(int(idx), 0, it)
                        elif key == "vehicles":
                            if value is not False:
                                it = PySide6.QtWidgets.QTableWidgetItem(str(value))
                                it.setTextAlignment(PySide6.QtCore.Qt.AlignCenter)
                                tb_show.setItem(int(idx), i, it)
                                tb_show.cellClicked.connect(self.selected_row)
                        else:
                            it = PySide6.QtWidgets.QTableWidgetItem(str(value))
                            it.setTextAlignment(PySide6.QtCore.Qt.AlignCenter)
                            tb_show.setItem(int(idx), i, it)
                            tb_show.cellClicked.connect(self.selected_row)
                            

        elif button == self.w.vehicle_select_btn:
            self.popup.label_head1.setText("Data Vehicle")
            tb_show.setRowCount(len(self.datas2))
            tb_show.setColumnCount(len(self.datas2[0])+1)
            
            header = tb_show.horizontalHeader()
            header.setMinimumHeight(34)
            header.setDefaultAlignment(PySide6.QtCore.Qt.AlignCenter | PySide6.QtCore.Qt.Alignment(PySide6.QtCore.Qt.TextWordWrap))

            header_items = ["No.", "Vehicle No", "Car Type", "Brand", "Model", "Color", "Person"]
            for i in range(tb_show.columnCount()):
                hItem = PySide6.QtWidgets.QTableWidgetItem(header_items[i])
                tb_show.setHorizontalHeaderItem(i, hItem)
                if i==0:
                    tb_show.setColumnWidth(0, 20)
                else:
                    header.setSectionResizeMode(i, PySide6.QtWidgets.QHeaderView.Stretch)
            data_to_show = self.datas2
            self.form = "Vehicle"

        
            if data_to_show:
                for idx, data_num in enumerate(range(len(data_to_show))):
                    it = PySide6.QtWidgets.QTableWidgetItem(str(idx+1))
                    it.setTextAlignment(PySide6.QtCore.Qt.AlignCenter)
                    tb_show.setItem(int(idx), 0, it)
                    for i, (key, value) in enumerate(data_to_show[data_num].items()):
                        if key == "person_id":
                            if value is not False:
                                it = PySide6.QtWidgets.QTableWidgetItem(str(self.datas1[value]["name"]))
                                it.setTextAlignment(PySide6.QtCore.Qt.AlignCenter)
                                tb_show.setItem(int(idx), i+1, it)
                                tb_show.cellClicked.connect(self.selected_row)
                        else:
                            it = PySide6.QtWidgets.QTableWidgetItem(str(value))
                            it.setTextAlignment(PySide6.QtCore.Qt.AlignCenter)
                            tb_show.setItem(int(idx), i+1, it)
                            tb_show.cellClicked.connect(self.selected_row)

        self.popup.exec()


    def selected_row(self, row_id, col_id):
        if self.form == "Person":
            datatoform = self.datas1[row_id]

            name = datatoform["name"]
            self.w.personName.setText(name)

            profile_file = datatoform["img"]
            pixmap = PySide6.QtGui.QPixmap(profile_file)  
            scaled_pixmap = pixmap.scaled(self.w.label_foto.size(), PySide6.QtCore.Qt.KeepAspectRatio, PySide6.QtCore.Qt.SmoothTransformation)
            self.w.label_foto.setPixmap(scaled_pixmap)

            gender = datatoform["gender"]
            if self.w.Gmale_radiobtn.text() == gender:
                self.w.Gmale_radiobtn.setChecked(True)
            elif self.w.Gfemale_radiobtn.text() == gender:
                self.w.Gfemale_radiobtn.setChecked(True)

            hair = datatoform["hairstyle"]
            if self.w.Hlong_radiobtn.text() == hair:
                self.w.Hlong_radiobtn.setChecked(True)
            elif self.w.Hshort_radiobtn.text() == hair:
                self.w.Hshort_radiobtn.setChecked(True)

            attrs = datatoform["attribute"]
            checkboxes = self.w.attr_checkboxGroup.parentWidget().findChildren(PySide6.QtWidgets.QCheckBox)
            for chbx in checkboxes:
                if chbx.text() in attrs:
                    chbx.setChecked(True)
                else:
                    chbx.setChecked(False)

        elif self.form == "Vehicle":
            datatoform = self.datas2[row_id]

            vehicle_no = datatoform["vehicle_no"]
            self.w.noVehicle.setText(vehicle_no)

            cartype = datatoform["type"]
            for i in range(self.w.car_comboBox.count()):
                if cartype == str(self.w.car_comboBox.itemText(i)):
                    self.w.car_comboBox.setCurrentIndex(i)
                    break

            brand = datatoform["brand"]
            for i in range(self.w.brand_comboBox.count()):
                if brand == str(self.w.brand_comboBox.itemText(i)):
                    self.w.brand_comboBox.setCurrentIndex(i)
                    break
            
            model = datatoform["model"]
            for i in range(self.w.model_comboBox.count()):
                if model == str(self.w.model_comboBox.itemText(i)):
                    self.w.model_comboBox.setCurrentIndex(i)
                    break
            
            color = datatoform["color"]
            for i in range(self.w.color_comboBox.count()):
                if color == str(self.w.color_comboBox.itemText(i)):
                    self.w.color_comboBox.setCurrentIndex(i)
                    break

        self.popup.close()


    def new_registVehicle(self):
        if self.w.noVehicle.text() == "":
            PySide6.QtWidgets.QMessageBox.critical(self, "Alert", f"Please enter the Vehicle No field")
            return
        
        noVehicle = self.w.noVehicle.text()
        cartype = self.w.car_comboBox.currentText()
        brand = self.w.brand_comboBox.currentText()
        model = self.w.model_comboBox.currentText()
        color = self.w.color_comboBox.currentText()
        qm = PySide6.QtWidgets.QMessageBox
        ret = qm.question(self,'Data Confirmation', "Save data registration?", qm.Yes | qm.No)
        if ret == qm.Yes:
            self.datas2.append({
                "vehicle_no": noVehicle,
                "type": cartype,
                "brand": brand,
                "model": model,
                "color": color,
                "person_id": False
            })
            self.datas["vehicle"] = self.datas2
            with open("./datas/objTracking.json", "w") as outfile: 
                json.dump(self.datas, outfile, indent=4) 
            print("success")

    def new_registPerson(self):
        if self.sender() != self.w.person_newReg_btn:
            return
        
        if self.w.personName.text() == "":
            PySide6.QtWidgets.QMessageBox.critical(self, "Alert", f"Please enter the name field")
            return
        if self.cam_usage is None and self.cam_usage not in list(self.cameralist.keys()):
            PySide6.QtWidgets.QMessageBox.critical(self, "Alert", "Please select the camera channel")
            return

        loader = PySide6.QtUiTools.QUiLoader()
        ui_file = PySide6.QtCore.QFile("ui/admgui/all_ui/event_setting/camera_confirm_dialog.ui")
        if not ui_file.open(PySide6.QtCore.QIODevice.ReadOnly):
            print(f"Cannot open UI file: {ui_file.errorString()}")
            return
        dialog = loader.load(ui_file, self)
        ui_file.close()
        self.popup = dialog
        self.popup.confirm_btn.clicked.connect(self.confirm_newPerson)
        self.popup.cancel_btn.clicked.connect(self.close_form)
        self.popup.setWindowTitle("Confirmation registration")

        self.popup.camname.setText(f"Camera ch : {self.cam_usage}")

        self.popup.activateWindow()     ## https://www.geeksforgeeks.org/pyqt5-qcalendarwidget-checking-if-it-is-active-window-or-not/

        name = self.w.personName.text()
        self.popup.name_label.setText(name)
        
        gender = "-"
        if self.w.Gmale_radiobtn.isChecked():
            gender = self.w.Gmale_radiobtn.text()
        elif self.w.Gfemale_radiobtn.isChecked():
            gender = self.w.Gfemale_radiobtn.text()
        self.popup.gender_label.setText(gender)
        
        hair = "-"
        if self.w.Hlong_radiobtn.isChecked():
            hair = self.w.Hlong_radiobtn.text()
        elif self.w.Hshort_radiobtn.isChecked():
            hair = self.w.Hshort_radiobtn.text()
        self.popup.hairstyle_label.setText(hair)
        
        attrs = []
        attr_string = "-"
        for chbx in self.w.attr_checkboxGroup.parentWidget().findChildren(PySide6.QtWidgets.QCheckBox):
            if chbx.isChecked():
                attrs.append(chbx.text())
                if attr_string == "-":
                    attr_string = str(chbx.text())
                else:
                    attr_string += f", {str(chbx.text())}"
                    
        self.popup.attr_label.setText(attr_string)
        
        self.filename = "-"
        self.update_data = {}
        
        self.camera = cv2.VideoCapture(self.cam_usage)
        self.frame = None
        self.timer = PySide6.QtCore.QTimer()
        self.timer.timeout.connect(lambda n=name, g=gender, h=hair, a=attrs:self.display_vid(n,g,h,a))
        self.timer.start(40)

        self.popup.exec()
        

    def display_vid(self, name, gender, hair, attrs):
        if self.popup.isActiveWindow() == False:
            self.close_form()
        # print("FORM :", self.popup.isActiveWindow())
        button = self.sender()
        if button is not self.w.person_newReg_btn:
            self.close_form()
        elif self.popup is None:
            self.close_form()    
        elif self.popup.capture_btn.isChecked():
            self.popup.capture_btn.setText("save image")
            ret, self.frame = self.camera.read()
            if ret:
                print(self.frame.shape)
                self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                image = PySide6.QtGui.QImage(self.frame, self.frame.shape[1], self.frame.shape[0], PySide6.QtGui.QImage.Format_RGB888)
                pixmap = PySide6.QtGui.QPixmap.fromImage(image)
                self.popup.label_cam.setPixmap(pixmap)
                self.popup.label_cam.setScaledContents(True)
                self.popup.confirm_btn.setEnabled(False)
        else:
            self.popup.capture_btn.setText("start video capture")
            if self.frame is not None:
                self.filename = f"./imgs/profile/p_{self.imlen}.jpg"
                self.frame = cv2.cvtColor(self.frame, cv2.COLOR_RGB2BGR)
                cv2.imwrite(self.filename, self.frame)
                print("Image captured!")
                self.frame = None
                self.popup.img_label.setText(self.filename)
            else:
                if self.filename != "-":
                    self.popup.confirm_btn.setEnabled(True)
                    self.update_data = {
                        "id": 12,
                        "name": name,
                        "img": self.filename,
                        "gender": gender,
                        "hairstyle": hair,
                        "attribute": attrs,
                        "vehicles": False
                    }

    def confirm_newPerson(self):
        self.datas1.append(self.update_data)
        self.datas["person"] = self.datas1
        with open("./datas/objTracking.json", "w") as outfile: 
            json.dump(self.datas, outfile, indent=4) 
        pixmap = PySide6.QtGui.QPixmap(self.update_data["img"])  
        scaled_pixmap = pixmap.scaled(self.w.label_foto.size(), PySide6.QtCore.Qt.KeepAspectRatio, PySide6.QtCore.Qt.SmoothTransformation)
        self.w.label_foto.setPixmap(scaled_pixmap)

        self.imlen = len(os.listdir("./imgs/profile"))
        self.close_form()



    def handle_filter(self):
        name_filter = self.w.personName.text()
        gender_fliter = "Male" if self.w.Gmale_radiobtn.isChecked() else "Female" if self.w.Gfemale_radiobtn.isChecked() else None
        hairstyle_fliter = "Long" if self.w.Hlong_radiobtn.isChecked() else "Short" if self.w.Hshort_radiobtn.isChecked() else None
        attrs_filter = []
        for chbx in self.w.attr_checkboxGroup.parentWidget().findChildren(PySide6.QtWidgets.QCheckBox):
            if chbx.isChecked():
                attrs_filter.append(chbx.text())

        vehicle_filter = self.w.noVehicle.text()
        type_fliter = self.w.car_comboBox.currentText()
        brand_fliter = self.w.brand_comboBox.currentText()
        model_fliter = self.w.model_comboBox.currentText()
        color_fliter = self.w.color_comboBox.currentText()
        # print(type_fliter, type_fliter=="")

        print(f"Filter person: {name_filter}, {gender_fliter}, {hairstyle_fliter}")
        print(f"Filter vehicle: {vehicle_filter}, {type_fliter}, {brand_fliter}, {model_fliter}, {color_fliter}")
        
        nameIsset = bool(re.search(r'[^\s]', name_filter))
        genderIsset = gender_fliter is not None
        hairIsset = hairstyle_fliter is not None
        attrIsset = len(attrs_filter) > 0

        vehicleIsset = bool(re.search(r'[^\s]', vehicle_filter))
        typeIsset = type_fliter != ''
        brandIsset = brand_fliter != ''
        modelIsset = model_fliter != ''
        colorIsset = color_fliter != ''

        self.filtered_datas = []
        filtered1 = []
        isDataFiltered1 = False
        filtered2 = []
        isDataFiltered2 = False

        if (nameIsset or genderIsset or hairIsset or attrIsset) :
            # and not (vehicleIsset and typeIsset and brandIsset):
            for d1 in self.datas1:
                name_match = name_filter == '' or d1["name"] == name_filter
                gender_match = gender_fliter is None or d1["gender"] == gender_fliter
                hair_match = hairstyle_fliter is None or d1["hairstyle"] == hairstyle_fliter
                attrs_match = set(attrs_filter).issubset(set(d1["attribute"]))
                if (name_match and gender_match and hair_match and attrs_match):
                    filtered1.append(d1)
            isDataFiltered1 = True
        # elif not (nameIsset and genderIsset and hairIsset) \
        if (vehicleIsset or typeIsset or brandIsset or modelIsset or colorIsset):    
            for d2 in self.datas2:
                vehicle_match = vehicle_filter == '' or d2["vehicle_no"] == vehicle_filter
                type_match = type_fliter == '' or d2["type"] == type_fliter
                brand_match = brand_fliter == '' or d2["brand"] == brand_fliter
                model_match = model_fliter == '' or d2["model"] == model_fliter
                color_match = color_fliter == '' or d2["color"] == color_fliter
                if (vehicle_match and type_match and brand_match and model_match and color_match):
                    filtered2.append(d2)
            isDataFiltered2 = True

        print(isDataFiltered1, "  ", isDataFiltered2)

        if isDataFiltered1 and isDataFiltered2:
            for fil1 in filtered1:
                filter_d2 = dict()
                if fil1["vehicles"]:
                    for fil2 in filtered2:
                        if fil2["vehicle_no"] in fil1["vehicles"]:
                            vehicle_match = vehicle_filter == '' or vehicle_filter in fil1["vehicles"] 
                            type_match = type_fliter == '' or type_fliter == fil2["type"] 
                            brand_match = brand_fliter == '' or brand_fliter == fil2["brand"] 
                            model_match = model_fliter == '' or model_fliter == fil2["model"] 
                            color_match = color_fliter == '' or color_fliter == fil2["color"] 
                
                            if vehicle_match and type_match and brand_match and model_match and color_match:
                                filter_d1 = fil1.copy()
                                filter_d1["vehicles"] = fil2["vehicle_no"]
                                filter_d1["car_type"] = fil2["type"]
                                filter_d1["car_brand"] = fil2["brand"]
                                filter_d1["car_model"] = fil2["model"]
                                filter_d1["color"] = fil2["color"]
                                self.filtered_datas.append(filter_d1)
            print(f"Filter Data: {self.filtered_datas}")
        elif (isDataFiltered1) and (not isDataFiltered2):
            for fil1 in filtered1:
                filter_d1 = fil1.copy()
                filter_d1["vehicles"] = filter_d1["vehicles"] if filter_d1["vehicles"] is not False else "None"
                self.filtered_datas.append(filter_d1)
            print(f"Filter Data: {self.filtered_datas}")
        elif (not isDataFiltered1) and (isDataFiltered2):
            for fil2 in filtered2:
                filter_d1 = dict()
                filter_d2 = fil2.copy()
                if fil2["person_id"] is not False:
                    for d1 in self.datas1:
                        if d1["id"] == fil2["person_id"]:
                            filter_d1 = d1.copy()
                            del filter_d1["vehicles"]
                            break
                else:
                    filter_d1 = {
                        "id":"",
                        "name": "None",
                        "img": "None",
                        "gender": "None",
                        "hairstyle": "None",
                        "attribute": "None",
                    }

                filter_d1.update(filter_d2)
                del filter_d1["person_id"]
                self.filtered_datas.append(filter_d1)
            print(f"Filter Data: {self.filtered_datas}")


        if self.filtered_datas:
            PySide6.QtWidgets.QMessageBox.information(self, "Searching info", f"filtered data : {len(self.filtered_datas)}")
        else:
            PySide6.QtWidgets.QMessageBox.critical(self, "Searching info", f"filtered data : {len(self.filtered_datas)}")


    def show_filter(self):
        loader = PySide6.QtUiTools.QUiLoader()
        ui_file = PySide6.QtCore.QFile("ui/admgui/all_ui/event_setting/select_data_dialog.ui")
        if not ui_file.open(PySide6.QtCore.QIODevice.ReadOnly):
            print(f"Cannot open UI file: {ui_file.errorString()}")
            return
        dialog = loader.load(ui_file, self)
        ui_file.close()
        self.popup = dialog
        self.popup.cancel_btn.clicked.connect(self.popup.close)
        self.popup.setWindowTitle("Select item")
        tb_show = self.popup.tb_show1
        
        self.popup.label_head1.setText("All Data Filter Results")
        data_to_show = self.filtered_datas
        if data_to_show:
            ## define table header
            header_items = []
            if len(data_to_show[0]) == 7:
                header_items = ["No.", "Name", "Img", "Gender", "Hairstyle", "Attribute", "Vehicle No"]
            else:
                header_items = ["No.", "Name", "Img", "Gender", "Hairstyle", "Attribute", "Vehicle No", "Car Type", "Brand", "Model", "Color"]
            tb_show.setRowCount(len(data_to_show))
            tb_show.setColumnCount(len(header_items))
            
            header = tb_show.horizontalHeader()
            header.setMinimumHeight(34)
            header.setDefaultAlignment(PySide6.QtCore.Qt.AlignCenter | PySide6.QtCore.Qt.Alignment(PySide6.QtCore.Qt.TextWordWrap))

            for i in range(tb_show.columnCount()):
                hItem = PySide6.QtWidgets.QTableWidgetItem(header_items[i])
                tb_show.setHorizontalHeaderItem(i, hItem)
                if i==0:
                    tb_show.setColumnWidth(i, 20)
                elif i==1:
                    tb_show.setColumnWidth(i, 100)
                elif i==5:
                    tb_show.setColumnWidth(i, 120)
                elif i==6:
                    tb_show.setColumnWidth(i, 120)
                else:
                    header.setSectionResizeMode(i, PySide6.QtWidgets.QHeaderView.Stretch)

            ## show data
            for idx, data_num in enumerate(range(len(data_to_show))):
                for i, (key, value) in enumerate(data_to_show[data_num].items()):
                    if key == "id":
                        it = PySide6.QtWidgets.QTableWidgetItem(str(idx+1))
                        it.setTextAlignment(PySide6.QtCore.Qt.AlignCenter)
                        tb_show.setItem(int(idx), 0, it)
                    elif key == "vehicles":
                        if value is not False:
                            it = PySide6.QtWidgets.QTableWidgetItem(str(value))
                            it.setTextAlignment(PySide6.QtCore.Qt.AlignCenter)
                            tb_show.setItem(int(idx), i, it)
                    else:
                        it = PySide6.QtWidgets.QTableWidgetItem(str(value))
                        it.setTextAlignment(PySide6.QtCore.Qt.AlignCenter)
                        tb_show.setItem(int(idx), i, it)
        
        self.popup.exec()




    def reset_input(self):
        ## reset person name
        self.w.personName.setText("")
        ## reset vehicle no
        self.w.noVehicle.setText("")
        ## reset gender radiobutton
        self.w.genderbtngroup.setExclusive(False)
        self.w.Gmale_radiobtn.setChecked(False)
        self.w.Gfemale_radiobtn.setChecked(False)
        self.w.genderbtngroup.setExclusive(True)
        ## reset hairstyle radiobutton
        self.w.hairbtngroup.setExclusive(False)
        self.w.Hlong_radiobtn.setChecked(False)
        self.w.Hshort_radiobtn.setChecked(False)
        self.w.hairbtngroup.setExclusive(True)
        ## reset attributes
        checkboxes = self.w.attr_checkboxGroup.parentWidget().findChildren(PySide6.QtWidgets.QCheckBox)
        for chbx in checkboxes:
            chbx.setChecked(False)
        ## reset combobox
        self.w.car_comboBox.setCurrentIndex(-1)
        self.w.brand_comboBox.setCurrentIndex(-1)
        self.w.model_comboBox.setCurrentIndex(-1)
        self.w.color_comboBox.setCurrentIndex(-1)

    def close_form(self):
        if self.timer:
            self.timer.stop()
        if self.camera:
            self.camera.release()
            self.camera = None
            # cv2.destroyAllWindows()
        if self.popup:
            self.popup.close()
            self.popup = None

