# **MQTT Message Flow Visualizer**

## **Overview**

The MQTT Message Flow Visualizer is a graphical user interface (GUI) tool designed to visually demonstrate the message flow in an MQTT communication setup. This tool acts purely from the perspective of a **subscriber** and provides an intuitive way to observe incoming messages without prior knowledge of MQTT specifics.

This project was developed during a working student position and provides significant value in visually demonstrating message flows to third parties in an easy-to-understand manner.

**Installation & Execution**

**(1) Clone the Repository:** 
```
git clone https://github.com/tBuddy00/MQTT-Message-Flow-Visualizer
```

**Run the Program**

Execute the following command in the terminal of your preferred IDE (**e.g., Microsoft Visual Studio Code**): 
```
python main.py
```
After execution, the MQTT-GUI should open.

**(2) Usage**

Default Settings

* The application comes with pre-configured values for:

  * MQTT Broker

  * Port

  * Topic (default: **/toERP**, alternative: **/toMES**)

* You can modify the topic to /toMES for testing purposes.

* Once you click the **Connect** button, it will turn green for 3 minutes if the connection to the broker is successful.

* The internal GUI terminal will also display whether the connection was established successfully.

**Message Flow Visualization**

* The message flow can be visualized when publishing to the topics:

  * KU2UWdy8/toERP

  * KU2UWdy8/toMES

* Incoming messages, including their respective topics, will be displayed in the GUI.

## **Platform Compatibility**

  * The application works on Windows and Linux.

  * On Linux, image paths may need to be adjusted for proper functionality.

## **Possible Enhancements**

  * Introduce automated updates, ensuring users always receive the latest version.

