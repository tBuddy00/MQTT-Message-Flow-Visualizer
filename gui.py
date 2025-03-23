#############################################################################
# DESCRIPTION
#############################################################################
"""
Brief explanation of the function: The 'gui.py' script creates and manages 
the graphical elements and the entire user interface of the GUI while visualizing 
the MQTT message flow.
"""
#############################################################################
# IMPORTS
#############################################################################
import tkinter as tk  # Basic structure of the GUI
from tkinter import *  # Import everything from tkinter
from tkinter import ttk  # Responsible for widgets
import ttkbootstrap as tb  # For GUI styling
from tkinter import Canvas
import paho.mqtt.client as mqtt  # MQTT library
import yaml


import label_name
from mqttclient import MQTTClient #Importing the MQTT client class for communication
#############################################################################


#############################################################################
# GUI CLASS + METHODS
#############################################################################
class MQTTVisualizerGUI:
    """
    +++ Responsibilities of the GUI Class +++

    The class manages the entire GUI and provides methods for MQTT connections and 
    animations.
    """
    def __init__(self):
        self.root = tb.Window(themename="superhero")  # Main window with Bootstrap design
        self.root.title(label_name.PROGRAM_NAME)  # Set GUI title
        self.root.iconphoto(False, tk.PhotoImage(file = "pictures/mqtt.png")) # Icon 

        # If 'load_config' does not exist -> load default values ​​for broker, port and topic
        self.config = self.load_config() or {"broker": "", "port": 1883, "topic": ""}
       
        self.mqtt_client = MQTTClient(self) #Reference to MQTT client class
        self.broker = self.config.get("broker", "broker.hivemq.com")  # 
        self.port = self.config.get("port", 1883)
        self.topic = self.config.get("topic")

        self.create_widgets()  # Create widgets
        self.connection_arrows = {}  # Connection arrows for message flow diagram

    #############################################################################
    # LOADING CONFIG YAML FILE (HIVEMQ)
    #############################################################################
    def load_config(self):
        """
        Loads the YAML file and returns the data
        """
        try:
            with open("config.yaml", "r") as file:
                config = yaml.safe_load(file)
                return config["data"]
        except FileNotFoundError:
            print("Error: 'config.yaml' had not been found.")
        except yaml.YAMLError as e:
            print(f"Error: parsing YAML file: '{e}'.")
            return None

    #############################################################################
    # GUI-DESIGN
    #############################################################################
    def create_widgets(self):
        """
        Creates GUI widgets (input fields, buttons, etc.) for user interaction.

        Input: None
        Output: None
        """
        # Main Frame
        self.top_frame = ttk.Frame(self.root, padding=10)
        self.top_frame.pack(fill="x")

        # MQTT Broker (Read-only input field)
        ttk.Label(self.top_frame, text=label_name.MQTT_BROKER).pack(side="left", padx=5)
        self.broker_entry = ttk.Entry(self.top_frame, width=30)
        self.broker_entry.insert(0, self.broker)
        self.broker_entry.pack(side="left", padx=5)

        # Port Input
        ttk.Label(self.top_frame, text=label_name.PORT).pack(side="left", padx=5)
        self.port_entry = ttk.Entry(self.top_frame, width=5)
        self.port_entry.insert(0, str(self.port))
        self.port_entry.pack(side="left", padx=5)

        # Topic Input
        ttk.Label(self.top_frame, text=label_name.TOPIC).pack(side="left", padx=5)
        self.topic_entry = ttk.Entry(self.top_frame, width=20)
        self.topic_entry.insert(0, self.topic)
        self.topic_entry.pack(side="left", padx=5)

        # Connect Button - Establishes connection to the broker
        self.connect_button = ttk.Button(self.top_frame, text=label_name.CONNECT_BUTTON, command=self.connect_to_broker)
        self.connect_button.pack(side="left", padx=5)
       
        # WebSockets Checkbox
        self.websocket_enabled = tk.BooleanVar(value = False) # Stores checkbox state
        self.websocket_button = tk.Checkbutton(self.top_frame, text="Use WebSocket", variable=self.websocket_enabled, command=self.websocket_status_message)
        self.websocket_button.pack(side = "left", padx = 5)

        # TLS Checkbox
        self.tls_enabled = tk.BooleanVar(value = False) 
        self.tls_button = tk.Checkbutton(self.top_frame, text="Enable TLS Service", variable=self.tls_enabled, command=self.tls_status_message)
        self.tls_button.pack(side = "left", padx = 5)

        # Representation of the message flow between the components (SAP, MQTT broker, MES)
        self.canvas_frame = ttk.LabelFrame(self.root, text=label_name.FRAME_NAME, padding=10)
        self.canvas_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.canvas = Canvas(self.canvas_frame, bg="white", height=400)
        self.canvas.pack(fill="both", expand=True)

        self.draw_static_diagram() # Draws the fixed structure of the components

        # Output all messages (message field in GUI)
        self.log_frame = ttk.LabelFrame(self.root, text="Messages", padding=10)
        self.log_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.log_text = tk.Text(self.log_frame, wrap="word", height=10, state=tk.DISABLED)
        self.log_text.pack(fill="both", expand=True)
        self.log_text.insert("end", "Currently no connections.\n")

    def draw_static_diagram(self):
        self.canvas.delete("all")
        """
        Draws the static diagram representing the MQTT message flow.
        This includes visualizing SAP, MES, the MQTT broker, data interfaces,
        and connection arrows.

        Input: None
        Output: None
        """
        # SAP
        self.sap_img = PhotoImage(file="pictures/sap-logo.png")
        resized_sap_img = self.sap_img.subsample(7, 7)
        self.canvas.create_image(115, 180, image=resized_sap_img)
        self.sap_img_resized = resized_sap_img
    
        # MQTT Broker as a rectangle
        self.canvas.create_rectangle(200, 100, 500, 300, fill="#FFD700", outline="black", width=2, tags="broker")
        self.canvas.create_text(350, 130, text=label_name.BROKER, font=("Arial", 12, "bold"))

        # Topics within the MQTT Broker (represented as smaller rectangles)
        self.canvas.create_rectangle(310, 160, 390, 190, fill="#FF9966", outline="black", width=1, tags="ucc")
        self.canvas.create_text(350, 175, text=label_name.UCC, font=("Arial", 10))

        self.canvas.create_rectangle(310, 195, 390, 220, fill="#FF9966", outline="black", width=1, tags="toMES")
        self.canvas.create_text(350, 209, text=label_name.toMES, font=("Arial", 10))

        self.canvas.create_rectangle(310, 225, 390, 250, fill="#FF9966", outline="black", width=1, tags="toERP")
        self.canvas.create_text(350, 239, text=label_name.toERP, font=("Arial", 10))

        # Data Interface 
        self.canvas.create_rectangle(275, 320, 430, 380, fill="lightblue", outline="black", width=2, tags="data_interface")
        self.canvas.create_text(350, 350, text=label_name.DATAINTERFACE, font=("Arial", 12, "bold"))

        # MES
        self.canvas.create_rectangle(550, 150, 650, 210, fill="lightgreen", outline="black", width=2, tags="mes")
        self.canvas.create_text(600, 180, text=label_name.MES, font=("Arial", 12, "bold"))

        # Connection Arrows
        self.canvas.create_line(155, 170, 310, 170, arrow="last", width=4)  # SAP ---> UCC (SAP)
        self.canvas.create_line(100, 210, 100, 350, arrow="first", width=6)  # SAP vertical arrow
        self.canvas.create_line(100, 350, 275, 350, arrow="last", width=6)  # SAP horizontal to Data Interface

        self.canvas.create_line(310, 180, 279, 180, arrow="last", width=4)  # Horizontal from SAP (UCC) (left side)
        self.canvas.create_line(280, 180, 280, 320, arrow="last", width=4)  # Vertical arrow down from SAP UCC to Data Interface

        self.canvas.create_line(390, 240, 600, 240, arrow="first", width=4)  # Horizontal arrows to toERP
        self.canvas.create_line(600, 240, 600, 210, arrow="first", width=4)  # Vertical arrow from MES 

        self.canvas.create_line(300, 320, 300, 205, arrow="last", width=4)  # Vertical from Data Interface
        self.canvas.create_line(300, 208, 315, 208, arrow="last", width=4)  # Horizontal to MES

        self.canvas.create_line(390, 200, 550, 200, arrow="last", width=4)  # Connection from toMES to MES
        self.canvas.create_line(350, 250, 350, 320, arrow="last", width=4)  # Vertical arrows from toERP to Data Interface       
        
        # Message indicating "No Current Connections"
        self.canvas.create_rectangle(200, 10, 500, 50, fill="grey", outline="black", width=2, tags="no_connection2") 
        self.no_connection_text = self.canvas.create_text(350, 30, text=label_name.NO_CONNECTIONS, font=("Arial", 15, "italic"), fill="black", tags="no_connection")

    def draw_connection_arrows(self):
        """
        Draws text labels on the arrows to visually represent the message flow between components.

        Input: None
        Output: None
        """
        # SAP to Data Interface
        self.canvas.create_text(190, 335, text=label_name.RETRIEVE_PRODUCTION_ORDER, font=("Arial", 8, "bold"), fill="white")
        # Data Interface to SAP
        self.canvas.create_text(105, 260, text=label_name.UPDATE_PRODUCTION_ORDER, font=("Arial", 8, "bold"), anchor="w", fill="white")
        # MES to Data Interface
        self.canvas.create_text(470, 250, text=label_name.UPDATE_PRODUCTION_ORDER2, font=("Arial", 8, "bold"), fill="white")
        # Data Interface to MES
        self.canvas.create_text(400, 190, text=label_name.NEW_PRODUCTION_ORDER, font=("Arial", 8, "bold"), anchor="w", fill="white")

    def websocket_status_message(self):
        """
        Logs a message when the WebSocket checkbox is activated or deactivated.
        """
        self.log_text.config(state=tk.NORMAL)
        if self.websocket_enabled.get():
            self.log_text.insert("end", "\nEnabled WebSocket service.\n")
        else:
            self.log_text.insert("end", "\nDisabled WebSocket service.\n")
        self.log_text.config(state=tk.DISABLED)

    def tls_status_message(self):
        """
        Logs a message when the TLS checkbox is activated or deactivated.
        """
        self.log_text.config(state=tk.NORMAL)
        if self.tls_enabled.get():
            self.log_text.insert("end", "\nEnabled TLS service.\n")
        else:
            self.log_text.insert("end", "\nDisabled TLS service.\n")
        self.log_text.config(state=tk.DISABLED)

    ##############################################################################
    # MQTT METHOD: REFERENCE TO MQTT CLIENT METHOD
    ##############################################################################
    def connect_to_broker(self): # Establishes the connection with the broker
        self.mqtt_client.connect_to_broker()

    ##############################################################################
    # ANIMATIONS
    ##############################################################################
    def start_animation(self, topic):
        """
        Starts the message flow animation depending on the given topic. 
        The animation is executed in steps and visualizes the message direction.

        Supported topics: 'toERP', 'toMES'

        Input:
            topic (str): The MQTT topic that triggers the corresponding animation
            
        Output:
            None
        """
        self.current_image_id = None

        if topic == 'toERP':
            self.animate_to_erp()
        elif topic == 'toMES':
            self.animate_sap_to_ucc()
        else:
            print(f"Unknown topic: '{topic}'.")
    ##############################################################################
    # Animation 'toMES'-Topic - BEGINNING
    ############################################################################## 
    def animate_sap_to_ucc(self):
        """
        Starts the animation of the message flow from SAP to UCC.

        Workflow:
            - Loads an image from file
            - Resizes the image to specified dimensions
            - Places it at the defined start position
            - Schedules the next animation step after a delay (1.5 seconds)

        Input:
            None

        Output:
            None
        """
        self.image = PhotoImage(file="pictures/yellow-envelope.png")
        resized_image = self.image.subsample(9, 9) #Verkleinerung des Bildes (Stauchung, Streckung)
        self.current_image_id = self.canvas.create_image(225, 150, image=resized_image) #Startposition vom Bild
        self.image_resized = resized_image #Neues Bild wird vorläufig gespeichert
        self.root.after(1500, self.animate_below_retrieve) #geht zur nächsten Animation über

    def animate_below_retrieve(self):
        """
        Moves the image from its current coordinates to a new position to visually 
        represent the message flow from SAP to the next step (Retrieve Production Order).

        Input:
            None

        Output:
            None
        """
        if self.current_image_id:
            self.canvas.coords(self.current_image_id, 190, 315) # Move image to a new position
        self.root.after(1500, self.animate_to_mes) # Schedule the next animation step

    def animate_to_mes(self):
        """
        Moves the image further to visually indicate the message flow 
        from the current position to the 'toMES' topic.

        Input:
            None
        Output:
            None
        """
        if self.current_image_id:
            self.canvas.coords(self.current_image_id, 318, 265)
        self.root.after(1500, self.animate_new_po)

    def animate_new_po(self):
        """
        Moves the image further to reach the 'New production order' coordinates. 
        Once the target is reached, the animation ends.

        Input:
            None
        Output:
            None
        """
        if self.current_image_id:
            self.canvas.coords(self.current_image_id, 440, 170)
            self.root.after(1500, self.finish_animation)
    ##############################################################################
    # Animation 'toMES'-Topic - END
    ############################################################################## 
    ##############################################################################
    # Animation 'toERP'-Topic - BEGINNING
    ############################################################################## 
    def animate_to_erp(self):
        """
        Starts the animation for the message flow from MES to SAP.

        Process:
            - Loads a different image,
            - Resizes it,
            - Places it at the defined starting coordinates,
            - Begins the first animation step after 1.5 seconds.

        Input:
            None
        Output:
            None
        """
        self.image = PhotoImage(file="pictures/red-envelope.png")
        resized_image = self.image.subsample(13, 13)
        self.current_image_id = self.canvas.create_image(430, 220, image=resized_image)
        self.image_resized = resized_image 
        self.root.after(1500, self.move_to_erp) 
   
    def move_to_erp(self):
        """
        Moves the image from the current position further toward the 'toERP' topic.

        Input:
            None
        Output:
            None
        """
        if self.current_image_id:
            self.canvas.coords(self.current_image_id, 370, 280)
        self.root.after(1500, self.move_to_odata)

    def move_to_odata(self):
        """
        Moves the image further, showing the transition from the 'toERP' topic 
        to the OData interface and ultimately back to SAP.

        Input:
            None
        Output:
            None
        """
        if self.current_image_id:
            self.canvas.coords(self.current_image_id, 80, 250)
        self.root.after(1500, self.finish_animation)
  
    def finish_animation(self):
        """
        Ends the animation by deleting the image from the canvas.

        Input:
            None
        Output:
            None
        """
        if self.current_image_id:
            self.canvas.delete(self.current_image_id)
        self.current_image_id = None
    ##############################################################################
    # Animation 'toERP'-Topic - END
    ############################################################################## 
    def highlight_flow(self):
        """
        Temporarily highlights the connection arrows in the diagram.

        Input:
            None
        Output:
            None
        """
        for arrow in self.connection_arrows.values():
            self.canvas.itemconfig(arrow, fill="red")
        self.root.after(500, lambda: [self.canvas.itemconfig(arrow, fill="black") for arrow in self.connection_arrows.values()])
    
    def run(self):
        """
        Starts the main event loop and waits for user interaction.

        Input:
            None
        Output:
            None
        """
        self.root.mainloop()

if __name__ == "__main__":
    app = MQTTVisualizerGUI()
    app.run()
