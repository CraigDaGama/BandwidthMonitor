import sys
import psutil
import time
import socket
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QSystemTrayIcon, QMenu, QAction, QComboBox
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon
import pyqtgraph as pg

class BandwidthMonitor(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.monitoring = False

    def initUI(self):
        self.setWindowTitle('Bandwidth Monitor')
        self.setGeometry(100, 100, 600, 400)
        self.setWindowIcon(QIcon("icon2.png"))

        # Create a dropdown for selecting network interface (WiFi/Ethernet)
        self.interface_combo = QComboBox(self)
        self.interfaces = [iface for iface in psutil.net_if_addrs().keys()]
        self.interface_combo.addItems(self.interfaces)

        # Set WiFi as the default interface if available
        default_interface = next((iface for iface in self.interfaces if "Wi-Fi" in iface or "wlan" in iface.lower()), None)
        if default_interface:
            self.interface_combo.setCurrentText(default_interface)

        # Create labels to display network information
        self.ip_label = QLabel('IP Address: N/A')
        self.gateway_label = QLabel('Gateway: N/A')
        self.subnet_mask_label = QLabel('Subnet Mask: N/A')
        self.data_sent_label = QLabel('Total Data Sent: 0 MB')
        self.data_recv_label = QLabel('Total Data Received: 0 MB')

        # Create layout to organize the network information labels
        network_info_layout = QVBoxLayout()
        network_info_layout.addWidget(QLabel('Select Interface:'))
        network_info_layout.addWidget(self.interface_combo)
        network_info_layout.addWidget(self.ip_label)
        network_info_layout.addWidget(self.gateway_label)
        network_info_layout.addWidget(self.subnet_mask_label)
        network_info_layout.addWidget(self.data_sent_label)
        network_info_layout.addWidget(self.data_recv_label)

        # Create a real-time graph for network speed
        self.graph_widget = pg.PlotWidget(self)
        self.graph_widget.setBackground('w')  # Set graph background to white
        self.graph_widget.setYRange(0, 10)  # Y-axis: 0 to 10 MB
        self.graph_widget.setLabel('left', 'Speed (MB/s)')
        self.graph_widget.setLabel('bottom', 'Time (s)')
        self.graph_widget.setTitle('Real Time Network Usage')

        # Add a legend to the graph with abbreviations for upload and download speeds
        self.graph_widget.addLegend(offset=(-10, -80))  # Adjust legend position as needed

        # Data storage for graph
        self.time_data = []
        self.upload_speed_data = []
        self.download_speed_data = []

        # Main layout to arrange network info and graph
        main_layout = QVBoxLayout()
        main_layout.addLayout(network_info_layout)
        main_layout.addWidget(self.graph_widget)

        self.setLayout(main_layout)

        # Connect the interface dropdown change event to update network info
        self.interface_combo.currentTextChanged.connect(self.update_network_info)

        # Immediately populate network info with data for the selected interface
        self.update_network_info()

    # Get network interface details like IP address, subnet mask, and gateway.
    def get_interface_details(self, interface):
        details = psutil.net_if_addrs().get(interface, [])
        ip_address = "N/A"
        subnet_mask = "N/A"
        gateway = "N/A"

        for info in details:
            if info.family == socket.AF_INET:  # IPv4
                ip_address = info.address
                subnet_mask = info.netmask

        # Gateway (Finding gateway is complex; this is a placeholder)
        gateways = psutil.net_if_stats().get(interface)
        if gateways and gateways.isup:
            gateway = "Up"  # Placeholder, real gateway fetching might differ

        return ip_address, subnet_mask, gateway

    # Update network information based on the selected interface
    def update_network_info(self):
        interface = self.interface_combo.currentText()

        ip_address, subnet_mask, gateway = self.get_interface_details(interface)

        self.ip_label.setText(f"IP Address: {ip_address}")
        self.gateway_label.setText(f"Gateway: {gateway}")
        self.subnet_mask_label.setText(f"Subnet Mask: {subnet_mask}")

    # Get the current network usage (bytes sent and received) for the selected interface
    def get_network_usage(self):
        net_stats = psutil.net_io_counters(pernic=True).get(self.interface_combo.currentText(), None)
        if net_stats:
            return net_stats.bytes_sent, net_stats.bytes_recv
        return 0, 0

    # Convert byte size to the most appropriate unit (bytes, KB, MB)
    def convert_bytes(self, byte_size):
        for unit in ['B', 'KB', 'MB']:
            if byte_size < 1024:
                return f"{byte_size:.2f} {unit}"
            byte_size /= 1024

        return f"{byte_size:.2f} GB"

    # Update network speeds and update the graph
    def update_network_speeds(self):
        sent, recv = self.get_network_usage()
        sent_speed = sent - self.prev_sent
        recv_speed = recv - self.prev_recv

        self.prev_sent, self.prev_recv = sent, recv

        # Convert speeds to the most appropriate unit
        upload_speed = self.convert_bytes(sent_speed)
        download_speed = self.convert_bytes(recv_speed)

        # Update labels
        self.data_sent_label.setText(f"Total Data Sent: {self.convert_bytes(sent)}")
        self.data_recv_label.setText(f"Total Data Received: {self.convert_bytes(recv)}")

        # Update tray icon tooltip text with current speeds
        self.tray_icon.setToolTip(f"↑ {upload_speed}/s | ↓ {download_speed}/s")

        # Add data to the graph
        current_time = time.time()
        self.time_data.append(current_time)
        self.upload_speed_data.append(sent_speed / (1024 * 1024))  # Convert to MB
        self.download_speed_data.append(recv_speed / (1024 * 1024))  # Convert to MB

        # Limit the data to the last 60 seconds for performance
        if len(self.time_data) > 60:
            self.time_data = self.time_data[-60:]
            self.upload_speed_data = self.upload_speed_data[-60:]
            self.download_speed_data = self.download_speed_data[-60:]

        # Update the graph with upload and download data
        self.graph_widget.clear()
        self.graph_widget.plot(self.time_data, self.upload_speed_data, pen='orange', name='UL')  # UL in orange
        self.graph_widget.plot(self.time_data, self.download_speed_data, pen='b', name='DL')  # DL in blue

    # Start monitoring network speeds
    def start_monitoring(self):
        self.prev_sent, self.prev_recv = self.get_network_usage()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_network_speeds)
        self.timer.start(1000)  # Update every second

    def show_window(self):
        self.show()

    def closeEvent(self, event):
        event.ignore()
        self.hide()

class TrayApp(QSystemTrayIcon):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIcon(QIcon("icon.png"))
        self.setVisible(True)

        # Create a context menu for the tray icon
        self.menu = QMenu(parent)
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.exit_app)
        self.menu.addAction(exit_action)
        self.setContextMenu(self.menu)

        # Connect the tray icon click to show the main window
        self.activated.connect(self.icon_clicked)

    # Clicking the tray icon displays the window
    def icon_clicked(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.parent().show_window()

    def exit_app(self):
        QApplication.quit()

def main():
    app = QApplication(sys.argv)
    monitor = BandwidthMonitor()

    tray_icon = TrayApp(monitor)
    monitor.tray_icon = tray_icon

    monitor.start_monitoring()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
