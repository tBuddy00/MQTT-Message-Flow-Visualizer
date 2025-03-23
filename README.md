# **MQTT Message Flow Visualizer**

## **Overview**

The MQTT Message Flow Visualizer is a graphical user interface (GUI) tool designed to visually demonstrate the message flow in an MQTT communication setup. This tool acts purely from the perspective of a **subscriber** and provides an intuitive way to observe incoming messages without prior knowledge of MQTT specifics.

This project was developed during a working student position and provides significant value in visually demonstrating message flows to third parties in an easy-to-understand manner.

**Installation & Execution:**

**1. Clone the Repository:** 
```
git clone https://github.com/tBuddy00/MQTT-Message-Flow-Visualizer
```

**2. Run the Program:**

Execute the following command in the terminal of your preferred IDE (**e.g., Microsoft Visual Studio Code**): 
```
python main.py
```
After execution, the MQTT-GUI should open.

## **Usage**

**Default Settings:**

The application comes preconfigured with the following defaults (configurable in `config.yaml`):

  * **MQTT Broker**: `broker.hivemq.com`

  * **Port**: `1883`

  * **Topic**: `/toERP` (or `/toMES` as an alternative)

You can modify the topic in the input field directly – try using `/toMES` for testing.

**Tip**: You can also use the **main topic**:
    
   * `KU2UWdy8/+`

This wildcard topic allows you to observe all subtopics under `KU2UWdy8/` (e.g. `KU2UWdy8/toERP`, `KU2UWdy8/toMES`) and visualize the full message flow automatically.

### Connecting to the Broker:

- Click the **Connect** button to initiate the connection.
- If successful, the button will temporarily turn **green** (for 3 minutes).
- A connection confirmation will also appear in the built-in GUI terminal.

The internal GUI terminal will also display whether the connection was established successfully.

### **Message Flow Visualization**

If messages are published to one of the following topics:

- `KU2UWdy8/toERP`
- `KU2UWdy8/toMES`

…the GUI will display:

- The **topic name**,
- The **payload**,
- A **corresponding animation** in the diagram to reflect the message direction

The animation depends on the subtopic (`toERP` or `toMES`) and visually represents the internal data flow.

#### TLS & WebSocket Options:

- You can enable **TLS encryption** and/or **WebSocket transport** via checkboxes.
- Upon toggling either option, a message will appear in the terminal window:

*Enabled WebSocket service. Enabled TLS service.*

This provides a clear visual cue that the selected service is active.

## **Platform Compatibility**

- ✅ Fully works on **Windows**
- ✅ Also works on **Linux** (you may need to adjust image paths under `pictures/`)

## Project Structure (Overview)
-------------------------------
- `main.py` – Launches the application
- `gui.py` – GUI logic & message flow visualizations
- `mqttclient.py` – Handles MQTT connectivity & messaging
- `config.yaml` – Configuration file (broker, port, topic)
- `pictures/` – All static and animated visual assets

## **Possible Enhancements**

- Add an **auto-update mechanism** to always deliver the latest version
- Support for **multiple simultaneous subscriptions**
- Optional **message publishing feature** for full MQTT interaction
