import sys
import psutil
import time
import socket
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QSystemTrayIcon, QMenu, QAction, QComboBox, QGridLayout, QFrame, QHBoxLayout
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
        self.resize(800, 600)  # Use resize instead of setGeometry for better default size
        self.setWindowIcon(QIcon("icon2.png"))

        # Apply Dark Theme
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
            }
            QLabel {
                font-weight: bold;
                padding: 5px;
            }
            QFrame#StatsFrame {
                background-color: #3c3f41;
                border: 1px solid #5a5a5a;
                border-radius: 8px;
            }
            QComboBox {
                background-color: #3c3f41;
                color: #ffffff;
                border: 1px solid #5a5a5a;
                border-radius: 4px;
                padding: 5px;
                font-weight: bold;
            }
            QComboBox:hover {
                background-color: #4b4e50;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: url(down_arrow.png);
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                background-color: #3c3f41;
                color: #ffffff;
                selection-background-color: #2b2b2b;
                outline: 0px;
            }
        """)

        # Create a dropdown for selecting network interface (WiFi/Ethernet)
        self.interface_combo = QComboBox(self)
        self.interfaces = [iface for iface in psutil.net_if_addrs().keys()]
        self.interface_combo.addItems(self.interfaces)

        # Set WiFi as the default interface if available
        default_interface = next((iface for iface in self.interfaces if "Wi-Fi" in iface or "wlan" in iface.lower()), None)
        if default_interface:
            self.interface_combo.setCurrentText(default_interface)

        # Create labels to display network information
        self.ip_label = QLabel('IP: N/A')
        # Removed Gateway Label as requested
        self.subnet_mask_label = QLabel('Mask: N/A')
        self.data_sent_label = QLabel('Sent: 0 MB')
        self.data_recv_label = QLabel('Recv: 0 MB')

        # Create a frame for the stats
        stats_frame = QFrame()
        stats_frame.setObjectName("StatsFrame")
        
        # Main stats layout (vertical container for rows)
        stats_layout = QVBoxLayout()
        stats_layout.setSpacing(5)
        
        # Row 1: Interface selection
        row1_layout = QHBoxLayout()
        row1_layout.addWidget(QLabel('Interface:'))
        row1_layout.addWidget(self.interface_combo)
        row1_layout.addStretch()
        
        # Row 2: Network Details (IP, Subnet)
        row2_layout = QHBoxLayout()
        row2_layout.addWidget(self.ip_label)
        row2_layout.addSpacing(20)
        row2_layout.addWidget(self.subnet_mask_label)
        row2_layout.addStretch()
        
        # Row 3: Data Usage
        row3_layout = QHBoxLayout()
        row3_layout.addWidget(self.data_sent_label)
        row3_layout.addSpacing(20)
        row3_layout.addWidget(self.data_recv_label)
        row3_layout.addStretch()
        
        stats_layout.addLayout(row1_layout)
        stats_layout.addLayout(row2_layout)
        stats_layout.addLayout(row3_layout)
        
        stats_frame.setLayout(stats_layout)

        # Create a real-time graph for network speed
        self.graph_widget = pg.PlotWidget(self)
        self.graph_widget.setBackground('#2b2b2b')  # Dark background
        self.graph_widget.showGrid(x=True, y=True, alpha=0.3)
        self.graph_widget.setYRange(0, 10)  # Y-axis: 0 to 10 MB
        
        # Disable mouse interaction to prevent scrolling/zooming/messing up axis
        self.graph_widget.setMouseEnabled(x=False, y=False)
        
        # Style the axes
        styles = {'color': '#ffffff', 'font-size': '12px'}
        self.graph_widget.setLabel('left', 'Speed (MB/s)', **styles)
        self.graph_widget.setLabel('bottom', 'Time (s)', **styles)
        self.graph_widget.setTitle('Real Time Network Usage', color='#ffffff', size='12pt')
        self.graph_widget.getAxis('left').setPen('#ffffff')
        self.graph_widget.getAxis('bottom').setPen('#ffffff')

        # Add a legend to the graph with abbreviations for upload and download speeds
        self.graph_widget.addLegend(offset=(-10, 10))  # Adjust legend position as needed

        # Data storage for graph (Fixed 60 second window)
        self.x_data = list(range(61))
        self.upload_speed_data = [0] * 61
        self.download_speed_data = [0] * 61
        
        # Main layout to arrange network info and graph
        main_layout = QVBoxLayout()
        main_layout.addWidget(stats_frame)
        main_layout.addWidget(self.graph_widget) # This will stretch to take available space
        
        self.setLayout(main_layout)

        # Connect the interface dropdown change event to update network info
        self.interface_combo.currentTextChanged.connect(self.update_network_info)

        # Immediately populate network info with data for the selected interface
        self.update_network_info()

    # Get network interface details like IP address and subnet mask.
    def get_interface_details(self, interface):
        details = psutil.net_if_addrs().get(interface, [])
        ip_address = "N/A"
        subnet_mask = "N/A"

        for info in details:
            if info.family == socket.AF_INET:  # IPv4
                ip_address = info.address
                subnet_mask = info.netmask

        return ip_address, subnet_mask

    # Update network information based on the selected interface
    def update_network_info(self):
        interface = self.interface_combo.currentText()
        ip_address, subnet_mask = self.get_interface_details(interface)

        self.ip_label.setText(f"IP: {ip_address}")
        self.subnet_mask_label.setText(f"Mask: {subnet_mask}")


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
        self.data_sent_label.setText(f"Sent: {self.convert_bytes(sent)}")
        self.data_recv_label.setText(f"Recv: {self.convert_bytes(recv)}")

        # Update tray icon tooltip text with current speeds
        self.tray_icon.setToolTip(f"↑ {upload_speed}/s | ↓ {download_speed}/s")

        # Update data arrays (sliding window)
        self.upload_speed_data.pop(0)
        self.download_speed_data.pop(0)
        
        self.upload_speed_data.append(sent_speed / (1024 * 1024))  # Convert to MB
        self.download_speed_data.append(recv_speed / (1024 * 1024))  # Convert to MB

        # Update the graph with upload and download data
        self.graph_widget.clear()
        
        # Plot Download (Cyan, filled)
        self.graph_widget.plot(self.x_data, self.download_speed_data, pen=pg.mkPen(color='#00e5ff', width=2), brush=(0, 229, 255, 50), fillLevel=0, name='DL')
        
        # Plot Upload (Magenta, filled)
        self.graph_widget.plot(self.x_data, self.upload_speed_data, pen=pg.mkPen(color='#ff00ff', width=2), brush=(255, 0, 255, 50), fillLevel=0, name='UL')

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
