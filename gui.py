#############################################################################
# ERKLÄRUNG
#############################################################################
"""
Kurze Erklärung zur Funktion: Im Grunde erstellt und verwaltet die 'gui.py' die grafischen
    Elemente bzw. die ganze Benutzeroberfläche der GUI, und visualisiert den MQTT-Nachrichtenfluss.
"""
#############################################################################
# IMPORTS
#############################################################################
import tkinter as tk #Grundgerüst der GUI-Oberfläche
from tkinter import * # s. o.
from tkinter import ttk  # Verantwortlich für Widgets 
import ttkbootstrap as tb  # Für das GUI-Design
from tkinter import Canvas
import paho.mqtt.client as mqtt #MQTT-Bibliothek
import yaml

# IMPORT DER LABEL-NAMEN
import label_name #Lädt die Konfigurationsdatei
# IMPORT DER MQTT-METHODEN
from mqttclient import MQTTClient #Importiert die MQTT-Klasse zur Kommunikation
#############################################################################

# Merke: Node Red Image zum Nachrichten testen

#############################################################################
# GUI + METHODEN
#############################################################################
class MQTTVisualizerGUI:
    """
    +++ Aufgaben der Klasse GUI-Klasse +++

    Die Klasse verwaltet die gesamte GUI und stellt die Methoden für die MQTT-Verbindungen und
    die Animationen bereit.
    """
    def __init__(self):
        self.root = tb.Window(themename="superhero")  # Erstellt das Hauptfenster mit Bootstrap-Design (GUI-Design)
        self.root.title(label_name.program_name)  # Vergabe GUI-Titel
        self.root.iconphoto(False, tk.PhotoImage(file = "pictures/htwd-logo.png")) # Icon 

        # Sofern 'load_config' nicht vorhanden -> laden von Standard-Werten für Broker, Port und Topic
        self.config = self.load_config() or {"broker": "", "port": 1883, "topic": ""}
        self.mqtt_client = MQTTClient(self) #VERWEIS AUF DIE MQTTCLIENT-KLASSE
        self.broker = self.config.get("broker", "broker.hivemq.com")  # Standard, falls nicht vorhanden
        self.port = self.config.get("port", 1883)
        self.topic = self.config.get("topic", "KU2UWdy8/toERP")

        self.create_widgets()  # Widgets werden erstellt
        
        self.connection_arrows = {}  # Verbindungspfeile für Nachrichtenfluss-Diagramm

    #############################################################################
    # LADEN DER YAML-DATEI
    #############################################################################
    def load_config(self):
        """
        Lädt die YAML-Datei und gibt die Daten zurück
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
        Erstellung der GUI-Widgets (Eingabefelder), mit denen der Nutzer interagiert.
        """
        # Äußerster Frame
        self.top_frame = ttk.Frame(self.root, padding=10)
        self.top_frame.pack(fill="x")

        # Broker-Eingabe wird hier getätigt
        ttk.Label(self.top_frame, text=label_name.mqtt_broker).pack(side="left", padx=5)
        self.broker_entry = ttk.Entry(self.top_frame, width=30)
        self.broker_entry.insert(0, self.broker)
        self.broker_entry.pack(side="left", padx=5)

        #Port-Eingabe wird hier getätigt
        ttk.Label(self.top_frame, text=label_name.port).pack(side="left", padx=5)
        self.port_entry = ttk.Entry(self.top_frame, width=5)
        self.port_entry.insert(0, str(self.port))
        self.port_entry.pack(side="left", padx=5)

        #Topic-EIngabe wird hier getätigt
        ttk.Label(self.top_frame, text=label_name.topic).pack(side="left", padx=5)
        self.topic_entry = ttk.Entry(self.top_frame, width=20)
        self.topic_entry.insert(0, self.topic)
        self.topic_entry.pack(side="left", padx=5)

        #'Connect'-Button in der GUI -> draufklicken löst die 'connect_to_broker'-Methode aus = Verbindung zum Broker wird hergestellt
        ttk.Button(self.top_frame, text=label_name.connect_button, command=self.connect_to_broker).pack(side="left", padx=5)

        # Darstellung des Nachrichtenflusses zwischen den Komponenten (SAP, MQTT-Broker, MES)
        self.canvas_frame = ttk.LabelFrame(self.root, text=label_name.frame_name, padding=10)
        self.canvas_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.canvas = Canvas(self.canvas_frame, bg="white", height=400)
        self.canvas.pack(fill="both", expand=True)

        self.draw_static_diagram() #Zeichnet die feste Struktur der Komponenten

        # Ausgabe aller Nachrichten (Nachrichtenfeld in GUI)
        self.log_frame = ttk.LabelFrame(self.root, text="Messages", padding=10)
        self.log_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.log_text = tk.Text(self.log_frame, wrap="word", height=10, state=tk.DISABLED)
        self.log_text.pack(fill="both", expand=True)
        self.log_text.insert("end", "Currently no connections.\n")

    def draw_static_diagram(self):
        self.canvas.delete("all")
        """
        SAP --> MES Animation
        """
        # SAP
        self.sap_img = PhotoImage(file="pictures/sap-logo.png")
        resized_sap_img = self.sap_img.subsample(7, 7)
        self.canvas.create_image(115, 180, image=resized_sap_img)
        self.sap_img_resized = resized_sap_img
    
        # MQTT Broker
        self.canvas.create_rectangle(200, 100, 500, 300, fill="#FFD700", outline="black", width=2, tags="broker")
        self.canvas.create_text(350, 130, text=label_name.broker, font=("Arial", 12, "bold"))

        # Topics im Broker
        self.canvas.create_rectangle(310, 160, 390, 190, fill="#FF9966", outline="black", width=1, tags="ucc")
        self.canvas.create_text(350, 175, text=label_name.ucc, font=("Arial", 10))

        self.canvas.create_rectangle(310, 195, 390, 220, fill="#FF9966", outline="black", width=1, tags="toMES")
        self.canvas.create_text(350, 209, text=label_name.toMES, font=("Arial", 10))

        self.canvas.create_rectangle(310, 225, 390, 250, fill="#FF9966", outline="black", width=1, tags="toERP")
        self.canvas.create_text(350, 239, text=label_name.toERP, font=("Arial", 10))

        # Data Interface 
        self.canvas.create_rectangle(275, 320, 430, 380, fill="lightblue", outline="black", width=2, tags="data_interface")
        self.canvas.create_text(350, 350, text=label_name.dataInterface, font=("Arial", 12, "bold"))

        # MES
        self.canvas.create_rectangle(550, 150, 650, 210, fill="lightgreen", outline="black", width=2, tags="mes")
        self.canvas.create_text(600, 180, text=label_name.mes, font=("Arial", 12, "bold"))

        # Verbindungspfeile
        self.canvas.create_line(155, 170, 310, 170, arrow="last", width=4)  # SAP ---> UCC (SAP)
        self.canvas.create_line(100, 210, 100, 350, arrow="first", width=6)  # SAP vertical arrow
        self.canvas.create_line(100, 350, 275, 350, arrow="last", width=6)  # SAP horizontal to Data Interface

        self.canvas.create_line(310, 180, 279, 180, arrow="last", width=4)  # Horizontal von SAP (UCC) (linksseitig)
        self.canvas.create_line(280, 180, 280, 320, arrow="last", width=4)  # Vertikal runter von SAP UCC zu Data Interface

        self.canvas.create_line(390, 240, 600, 240, arrow="first", width=4)  # Horizontaler Pfeil zu toERP
        self.canvas.create_line(600, 240, 600, 210, arrow="first", width=4)  # Vertikal nach unten von MES 

        self.canvas.create_line(300, 320, 300, 205, arrow="last", width=4)  # Vertikal von Data Interface
        self.canvas.create_line(300, 208, 315, 208, arrow="last", width=4)  # Horizontal zu MES

        self.canvas.create_line(390, 200, 550, 200, arrow="last", width=4)  # Verbindung von toMES zu MES
        self.canvas.create_line(350, 250, 350, 320, arrow="last", width=4)  # Vertikaler Pfeil von toERP zu Data Interface       

        
        #Hinweis: Keine aktuellen Verbindungen
        self.canvas.create_rectangle(200, 10, 500, 50, fill="grey", outline="black", width=2, tags="no_connection2") 
        self.no_connection_text = self.canvas.create_text(350, 30, text=label_name.no_connections, font=("Arial", 15, "italic"), fill="black", tags="no_connection")

    def draw_connection_arrows(self):
        """
        Stellt die Beschriftung auf den Pfeilen visuell dar.
        """
        # SAP zu Data Interface
        self.canvas.create_text(190, 335, text=label_name.retrieve_production_order, font=("Arial", 8, "bold"), fill="white")
        # Data Interface zu SAP
        self.canvas.create_text(105, 260, text=label_name.update_production_order, font=("Arial", 8, "bold"), anchor="w", fill="white")
        # MES zu Data Interface
        self.canvas.create_text(470, 250, text=label_name.update_production_order2, font=("Arial", 8, "bold"), fill="white")
        # Data Interface zu MES
        self.canvas.create_text(400, 190, text=label_name.new_production_order, font=("Arial", 8, "bold"), anchor="w", fill="white")

    ##############################################################################
    # MQTT-METHODE: VERWEIS AUF MQTT-CLIENT-METHODE
    ##############################################################################
    def connect_to_broker(self): #Stellt die Verbindung mit dem Broker her
        self.mqtt_client.connect_to_broker()

    ##############################################################################
    # ANIMATIONEN
    ##############################################################################
    def start_animation(self, topic):
        """
        Startet die Animation des Nachrichtenflusses 
        nacheinander, in Abhängigkeit vom Topic.

        Aktuell vorhandene Topics: 'toERP' und 'toMES'.
        """
        self.current_image_id = None

        if topic == 'toERP':
            self.animate_to_erp()
        elif topic == 'toMES':
            self.animate_sap_to_ucc()
        else:
            print(f"Unknown topic: '{topic}'.")
    ##############################################################################
    # Animation 'toMES'-Topic - ANFANG
    ############################################################################## 
    def animate_sap_to_ucc(self):
        """
        Startet den Nachrichtenfluss von SAP zu UCC.
        
        Ablauf:
            --> liest ein Bild aus einer Datei ein,
            --> verkleinert das Bild auf den vorgegebenen Anfangskoordinaten,
            --> platziert es optisch an den wichtigen Punkten und das nach genau 3 Sekunden 
        """
        self.image = PhotoImage(file="pictures/yellow-envelope.png")
        resized_image = self.image.subsample(9, 9) #Verkleinerung des Bildes (Stauchung, Streckung)
        self.current_image_id = self.canvas.create_image(225, 150, image=resized_image) #Startposition vom Bild
        self.image_resized = resized_image #Neues Bild wird vorläufig gespeichert
        self.root.after(3000, self.animate_below_retrieve) #geht zur nächsten Animation über

    def animate_below_retrieve(self):
        """
        Verschiebt das Bild - ausgehend von den letzten Koordinaten - an eine neue Position, sodass es visuell den Weg
        von SAP zum nächsten Schritt (Retrieve production order) andeutet.
        """
        if self.current_image_id:
            self.canvas.coords(self.current_image_id, 190, 315) #Neue Bild-Position
        self.root.after(3000, self.animate_to_mes) #Neue Bild-Koordinaten nach 3 Sekunden

    def animate_to_mes(self):
        """
        Verschiebt das Bild weiter, sodass es den Weg von der aktuellen Position zum Topic
        'toMES' andeutet.
        """
        if self.current_image_id:
            self.canvas.coords(self.current_image_id, 318, 265)
        self.root.after(3000, self.animate_new_po)

    def animate_new_po(self):
        """
        Verschiebt das Bild weiter, um die Koordinten 'New production order' zu erreichen. Sobald
        'New production order' erreicht ist, wird die Animation beendet.
        """
        if self.current_image_id:
            self.canvas.coords(self.current_image_id, 440, 170)
            self.root.after(3000, self.finish_animation)
    ##############################################################################
    # Animation 'toMES'-Topic - ENDE
    ############################################################################## 
    ##############################################################################
    # Animation 'toERP'-Topic - Anfang
    ############################################################################## 
    def animate_to_erp(self):
        """
        Startet die Animation für den Nachrichtenfluss von MES zu SAP.

        Ablauf: 
            --> liest ein anderes Bild ein,
            --> verkleinert das neue Bild wieder,
            --> platziert das Bild an den vorgegebenen Anfangskoordinaten und setzt den ersten Animationsschritt
                nach 3 Sekunden
        """
        self.image = PhotoImage(file="pictures/red-envelope.png")
        resized_image = self.image.subsample(13, 13)
        self.current_image_id = self.canvas.create_image(430, 220, image=resized_image)
        self.image_resized = resized_image 
        self.root.after(3000, self.move_to_erp) 
   
    def move_to_erp(self):
        """
        Verschiebt das Bild von der aktuellen Position weiter in Richtung 'toERP'-Topic.
        """
        if self.current_image_id:
            self.canvas.coords(self.current_image_id, 370, 280)
        self.root.after(3000, self.move_to_odata)

    def move_to_odata(self):
        """
        Verschiebt das Bild weiter, sodass es den Übergang vom 'toERP'-Topic zu ODataInterface visuell 
        darstellt und dann bei SAP beendet.
        """
        if self.current_image_id:
            self.canvas.coords(self.current_image_id, 80, 250)
        self.root.after(3000, self.finish_animation)
  
    def finish_animation(self):
        """
        Beendet die Animation, Bild wird von Canvas gelöscht.
        """
        if self.current_image_id:
            self.canvas.delete(self.current_image_id)
        self.current_image_id = None #Soll anzeigen, dass keine Animation mehr aktiv ist
    ##############################################################################
    # Animation 'toERP'-Topic - ENDE
    ############################################################################## 
    def highlight_flow(self):
        """
        Hebt temporär die Verbindungspfeile im Diagramm hervor.
        """
        for arrow in self.connection_arrows.values():
            self.canvas.itemconfig(arrow, fill="red")
        self.root.after(500, lambda: [self.canvas.itemconfig(arrow, fill="black") for arrow in self.connection_arrows.values()])
    
    # Startet die Hauptschleife und wartet dann auf eine Benutzerinteraktion
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = MQTTVisualizerGUI()
    app.run()
