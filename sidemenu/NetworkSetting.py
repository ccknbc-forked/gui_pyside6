from PySide6 import QtWidgets
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice, Qt
import sys, os
import socket
import psutil
import subprocess
import ipaddress

# print(os.getcwd())
style = None
with open("ui/style/style_form.qss", "r") as file:
    style = file.read()


class NetSetting(QtWidgets.QMainWindow):
    def __init__(self, w):
        super().__init__()
        self.w = w
        self.setCentralWidget(w)
        # self.setWindowModality(Qt.ApplicationModal)

        self.setWindowTitle("Network Setting")
        self.setStyleSheet(style)
        self.w.btn_cancel.clicked.connect(self.close)

        self.w.ifList_cb.addItems(psutil.net_if_addrs().keys())
        self.w.ipSetting_cb.addItems(["Manual (Static IP)", "Automatic (DHCP)"])
        self.w.ipSetting_cb.currentIndexChanged.connect(self.on_ip_setting_changed)
        self.w.ifList_cb.currentIndexChanged.connect(self.on_ip_setting_changed)
        self.on_ip_setting_changed()

    def on_ip_setting_changed(self):
        if self.w.ipSetting_cb.currentText() == "Automatic (DHCP)":
            self.updateDHCPInfo()
            self.set_manual_fields_enabled(False)
        else:
            self.w.ipAddr_edit.setText("")
            self.w.netMask_edit.setText("")
            self.w.gateaway_edit.setText("")
            self.w.dns1_edit.setText("")
            self.w.dns2_edit.setText("")
            self.set_manual_fields_enabled(True)
        self.update_network_speed()       

    def set_manual_fields_enabled(self, enabled):
        self.w.ipAddr_edit.setEnabled(enabled)
        self.w.netMask_edit.setEnabled(enabled)
        self.w.gateaway_edit.setEnabled(enabled)
        self.w.dns1_edit.setEnabled(enabled)
        self.w.dns2_edit.setEnabled(enabled)
        self.w.netSpeed_edit.setEnabled(False)
    

    def ping(self, ip):
        result = subprocess.run(['ping', '-c', '1', ip], stdout=subprocess.DEVNULL)
        return result.returncode == 0

    def update_network_speed(self):
        interface = self.w.ifList_cb.currentText()
        if interface in psutil.net_if_stats():
            stats = psutil.net_if_stats()[interface]
            speed = f"{stats.speed} Mbps"
            self.w.netSpeed_edit.setText(speed)
        else:
            self.w.netSpeed_edit.setText("N/A")


    def updateDHCPInfo(self):       # https://docs.python.org/3/howto/ipaddress.html
        interface = self.w.ifList_cb.currentText()
        if interface == "lo":
            self.w.ipAddr_edit.setText("")
            self.w.netMask_edit.setText("")
            self.w.gateaway_edit.setText("")
            self.w.dns1_edit.setText("")
            self.w.dns2_edit.setText("")
        else:
            command = f"ip a | grep 'inet ' | grep {interface}"
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
            result = process.communicate()[0].decode().strip()

            if result:
                ip_info = result.split()[1].split('/')
                self.w.ipAddr_edit.setText(ip_info[0])
                
                print(str(result.split()[1]))
                net4 = ipaddress.ip_network(str(result.split()[1]), False)
                self.w.netMask_edit.setText(str(net4.netmask))

                command_gateway = f"ip route | grep default | grep {interface}"
                process_gateway = subprocess.Popen(command_gateway, shell=True, stdout=subprocess.PIPE)
                gateway_result = process_gateway.communicate()[0].decode().strip()
                if gateway_result:
                    gateway_ip = gateway_result.split()[2]
                    self.w.gateaway_edit.setText(gateway_ip)

                self.w.dns1_edit.setText("8.8.8.8")  # DNS Google
                self.w.dns2_edit.setText("8.8.4.4")  # DNS Google

    def applyConfig(self):
        pass