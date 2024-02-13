import psutil
import time
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel

class NetworkMonitor(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.monitoring = False

    def initUI(self):
        self.setWindowTitle('Network Monitor')

        self.label = QLabel('Monitoring network bandwidth.')
        self.start_button = QPushButton('Start', self)
        self.stop_button = QPushButton('Stop', self)
        self.stop_button.setEnabled(False)

        vbox = QVBoxLayout()
        vbox.addWidget(self.label)
        vbox.addWidget(self.start_button)
        vbox.addWidget(self.stop_button)
        self.setLayout(vbox)

        self.start_button.clicked.connect(self.start_monitoring)
        self.stop_button.clicked.connect(self.stop_monitoring)

    def get_network_usage(self):
        net_stats = psutil.net_io_counters()
        return net_stats.bytes_sent, net_stats.bytes_recv

    def convert_bytes(self, byte_size):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if byte_size < 1024:
                return f"{byte_size:.2f} {unit}"
            byte_size /= 1024

    def monitor_network(self):
        prev_sent, prev_recv = self.get_network_usage()

        while self.monitoring:
            time.sleep(1)
            sent, recv = self.get_network_usage()

            sent_speed = self.convert_bytes(sent - prev_sent) + "/s"
            recv_speed = self.convert_bytes(recv - prev_recv) + "/s"

            self.label.setText(f"Sent: {self.convert_bytes(sent)} | Speed: {sent_speed} || "
                                f"Received: {self.convert_bytes(recv)} | Speed: {recv_speed}")

            prev_sent, prev_recv = sent, recv
            QApplication.processEvents()

    def start_monitoring(self):
        self.monitoring = True
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.monitor_network()

    def stop_monitoring(self):
        self.monitoring = False
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

def main():
    app = QApplication(sys.argv)
    monitor = NetworkMonitor()
    monitor.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
