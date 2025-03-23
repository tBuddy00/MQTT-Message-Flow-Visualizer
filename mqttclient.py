#############################################################################
# DESCRIPTION
#############################################################################
"""
Short description of the functionality: 'mqttclient.py' contains only the MQTT methods 
and class required for communication with an MQTT broker.
"""
#############################################################################
# IMPORTS
#############################################################################
import paho.mqtt.client as mqtt
import tkinter as tk
import ssl #For TLS certificates
import traceback #For error handling 

##############################################################################
# MQTT METHODS + CLASS
##############################################################################
class MQTTClient:
    """
    +++ Responsibilities of the MQTT class +++

    1. Establish connection to the MQTT broker
    2. Register callback functions for connection and message events
    3. Pass GUI updates back to the GUI instance
    """
    def __init__(self, gui): 
        """
        Input: gui (MQTTVisualizerGUI), 
        Output: None
        """
        self.gui = gui  # Reference to the GUI object
        self.client = mqtt.Client() # Create MQTT client instance
        # Callback-Funktionen
        self.client.on_connect = self.on_connect # Callback on successful connection
        self.client.on_message = self.on_message # Callback on incoming message
        self.topic = None

    def connect_to_broker(self):
        """
        Called when the user clicks the 'Connect' button in the GUI.

        Input: None,
        Output: None
    
        """
        broker = self.gui.broker_entry.get() # Broker address (HIVEMQ)
        port = int(self.gui.port_entry.get()) # Port as int
        self.topic = self.gui.topic_entry.get().strip() # #Topic - Remove leading/trailing spaces
                                                
        """
        Writes information, such as the possible absence of a topic,
        into the log field in the GUI and then locks it again with [...]tk.DISABLED --> otherwise it is an input field.

        Checks whether a topic has been entered.
        """
        if not self.topic:
            self.gui.log_text.config(state=tk.NORMAL)
            self.gui.log_text.insert("end", "Error: No topic specified.\n")
            self.gui.log_text.config(state=tk.DISABLED)
            return #Beendet Methode, falls Topic leer

        # Use WebSocket transport if enabled
        if self.gui.websocket_enabled.get():
            self.client = mqtt.Client(transport = "websockets")
        else:
            self.client = mqtt.Client() #default connection

        # Enable TLS if selected
        if self.gui.tls_enabled.get():
            self.client.tls_set(cert_reqs=ssl.CERT_NONE)
            self.client.tls_insecure_set(True)

        # Set callbacks and attempt connection
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        """
        Keep-Alive-Time: 180 Sec
        """
        try:
            self.client.connect(broker, port, 180) # Keep-Alive-Time
            self.client.loop_start()
        except Exception as e:
                self.gui.log_text.config(state=tk.NORMAL)
                self.gui.log_text.insert("end", f"\n+++ Error: Connection failed! - '{e}' +++ \n")
                self.gui.log_text.insert("end", f"\n+++ ERROR-TRACEBACK: {traceback.format_exc()} +++\n")
                self.gui.log_text.config(state=tk.DISABLED)
                return

        # On success: log to GUI
        self.gui.log_text.config(state=tk.NORMAL)
        self.gui.log_text.insert("end", f"\nConnected with broker '{broker}'\nSubscribing to topic: '{self.topic}'")
        self.gui.log_text.config(state=tk.DISABLED)

        # Connect' button turns green as long as Keep-Alive-Time is active -> currently 3 minutes
        connect_button = self.gui.top_frame.winfo_children()[-1]  # The last element in the frame is the button itself
        original_color = connect_button.cget("style") # Saves original button style
        connect_button.configure(style="success.TButton") #Temporarily green = connection established (for 3 minutes)
        
        # Timer for resetting the Connect button + Disconnected message
        self.gui.root.after(180 * 1000, lambda: connect_button.configure(style=original_color))

        # Removes the "No current connections" message
        self.gui.canvas.delete("no_connection")
        self.gui.canvas.delete("no_connection2")
        self.gui.draw_connection_arrows()

    def on_connect(self, client, userdata, flags, rc):
        """
        Callback function when MQTT client connects.

        Parameters:
        - client: the MQTT client instance
        - userdata: custom user data (not used)
        - flags: response flags from the broker
        - rc: result code (0 = success)

        Input: multiple MQTT-specific objects; 
        Output: None
        """
        # Successfull connection
        if rc == 0:
            self.gui.log_text.config(state=tk.NORMAL)
            self.gui.log_text.insert("end", " - Successfully connected.\n")
            self.gui.log_text.config(state=tk.DISABLED)
            client.subscribe(self.topic + "/#") #MQTT Wildecard -> subscribe to all subtopics
        
        # Error message
        else:
            self.gui.log_text.config(state=tk.NORMAL)
            self.gui.log_text.insert("end", f" -->  +++ Connection failed with error code '{rc}'. +++\n")
            self.gui.log_text.config(state=tk.DISABLED)

    def on_message(self, client, userdata, message):
        """
        Callback function triggered upon receiving an MQTT message.

        Depending on the subtopic, a different animation is triggered.

        Input: MQTT message components; 
        Output: None
        """
        incoming_message = f"\nTopic: '{message.topic}'  +++ Incoming message: '{message.payload.decode('utf-8')}' +++\n"
        self.gui.log_text.config(state=tk.NORMAL)
        self.gui.log_text.insert("end", incoming_message)
        self.gui.log_text.see("end")
        self.gui.log_text.config(state=tk.DISABLED)

        """
        Based on the subtopic, an animation is triggered as soon as the input message 
        contains one of the topics
        """
        subtopic = message.topic.split("/")[-1] # Filtering the subtopics
        
        # Differentiation of the input message to the animation
        if subtopic == 'toERP':
            self.gui.start_animation('toERP')
        elif subtopic == 'toMES':
            self.gui.start_animation('toMES')
        else:
            print(f"Unknown topic: '{message.topic}'.")
