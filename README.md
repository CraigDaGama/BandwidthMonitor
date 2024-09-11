# Bandwidth Monitor

This is a simple Python-based bandwidth monitoring tool with a graphical interface using PyQt5. It displays real-time upload and download speeds, IP address information, and provides a system tray icon for easy access.

## Features
- Real-time monitoring of upload and download speeds.
- Graphical interface with a graph to display bandwidth usage over time.
- Display of network information such as IP address, subnet mask, and gateway.
- System tray icon with bandwidth information and a context menu for exiting the app.

## Requirements

- Python 3.x
- PyQt5
- psutil
- pyqtgraph

## Installation

1. **Clone the repository**:

    ```bash
    git clone https://github.com/your-repo/bandwidth-monitor.git
    cd bandwidth-monitor
    ```

2. **Install the required packages** using pip:

    ```bash
    pip install -r requirements.txt
    ```

   Alternatively, you can install the packages individually:

    ```bash
    pip install PyQt5 psutil pyqtgraph
    ```

3. **Running the Application**:

    After installing the required libraries, you can run the program with:

    ```bash
    python BandwidthMonitor.py
    ```

## Usage

1. When you run the program, there will be an icon in the system tray (taskbar)
2. When you hover over the icon you will get the real time upload and download speed of the network you are connected to.
3. If you click on the icon, a window will open displaying the network information and real-time bandwidth usage in a graph.
4. Select the network interface (e.g., Wi-Fi or Ethernet) from the dropdown to monitor.
5. The system tray icon shows real-time upload and download speeds.
6. You can close the window which minimizes it to the system tray.
7. Right-click the system tray icon to access the exit option.

## Notes

- The application automatically updates the network information and bandwidth usage every second.
- The graph displays upload and download speeds in megabytes per second (MB/s) over the last 60 seconds.

## License

This project is licensed under the MIT License.
