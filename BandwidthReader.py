import sys
import psutil
import time
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QIcon

class BandwidthMonitor(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.monitoring = False

    def initUI(self):
        self.setWindowTitle('Bandwidth Monitor')
        self.setGeometry(100, 100, 600, 400)

        # Set window icon
        self.setWindowIcon(QIcon("icon2.png"))  

        self.label = QLabel('Bandwidth monitor window.', self)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

    def get_network_usage(self):
        net_stats = psutil.net_io_counters()
        return net_stats.bytes_sent, net_stats.bytes_recv

    def convert_bytes(self, byte_size):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if byte_size < 1024:
                return f"{byte_size:.2f} {unit}"
            byte_size /= 1024

    def update_network_speeds(self):
        sent, recv = self.get_network_usage()
        sent_speed = self.convert_bytes(sent - self.prev_sent)
        recv_speed = self.convert_bytes(recv - self.prev_recv)

        self.prev_sent, self.prev_recv = sent, recv

        upload_speed = f"↑ {sent_speed}/s"
        download_speed = f"↓ {recv_speed}/s"
        
        # Update tray icon tooltip text with the aesthetic speed display
        self.tray_icon.setToolTip(f"{upload_speed} | {download_speed}")

    def start_monitoring(self):
        # Initialize network stats for comparison
        self.prev_sent, self.prev_recv = self.get_network_usage()

        # Start a timer that calls the network speed update function every second
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_network_speeds)
        self.timer.start(1000)  # Update every 1 second

    def show_window(self):
        # Display the window when the tray icon is clicked
        self.show()

    def closeEvent(self, event):
        # Override close event to minimize to tray instead of closing
        event.ignore()
        self.hide()


class TrayApp(QSystemTrayIcon):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIcon(QIcon("icon.png"))
        self.setVisible(True)

        # Add a menu for exiting the application
        self.menu = QMenu(parent)
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.exit_app)
        self.menu.addAction(exit_action)
        self.setContextMenu(self.menu)

        # Connect the click on the tray icon to open the window
        self.activated.connect(self.icon_clicked)

    def icon_clicked(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.parent().show_window()

    def exit_app(self):
        QApplication.quit()


def main():
    app = QApplication(sys.argv)

    # Create the network monitor window (but hide it initially)
    monitor = BandwidthMonitor()

    # Create the system tray icon and associate it with the window
    tray_icon = TrayApp(monitor)
    monitor.tray_icon = tray_icon

    # Start monitoring network speeds
    monitor.start_monitoring()

    # Run the application
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
