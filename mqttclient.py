#############################################################################
# ERKLÄRUNG
#############################################################################
"""
Kurze Erklärung zur Funktion: 'mqttclient.py' enthält ausschließlich die MQTT-Methoden (+ Klasse), 
    die zur Kommunikation mit einem MQTT-Broker dienlich sind.
"""
#############################################################################
# IMPORTS
#############################################################################
import paho.mqtt.client as mqtt
import tkinter as tk
import ssl #For TLS certificates

##############################################################################
# MQTT-METHODEN + KLASSE
##############################################################################
class MQTTClient:
    """
    +++ Aufgaben der MQTT-Klasse +++ 

    1. Aufbau der Verbindung zum MQTT-Broker
    2. Registrierung der Callback-Funktionen, die bei Verbindungsaufbau
        und Nachrichtenempfang aufgerufen werden
    3. GUI-Aktualisierungen an das GUI-Objekt (bzw. Instanz) weitergeben
    """
    def __init__(self, gui): #PARAMETER AUF GUI-OBJEKT
        self.gui = gui  # REFERENZ AUF DAS GUI-OBJEKT
        self.client = mqtt.Client() #Erzeugt MQTT-CLient-Instanz
        # Callback-Funktionen
        self.client.on_connect = self.on_connect #Aufruf sobald Verbindung hergestellt
        self.client.on_message = self.on_message #Aufruf sobald Nachricht empfangen
        self.topic = None

    def connect_to_broker(self):
        """
        Wird gerufen, sobald der Nutzer explizit auf den 'Connect'-Button 
        in der GUI klickt.
        """
        # Werte aus den Eingabefeldern in der GUI holen
        broker = self.gui.broker_entry.get() #Brokeradresse
        port = int(self.gui.port_entry.get()) #Portnummer als Integer
        self.topic = self.gui.topic_entry.get().strip() #Topic
                                                # .strip() entfernt einfach vorangegangene oder führende Leerzeichen
        """
        Schreibt eine Information, wie das evtl. fehlen von einem Topic,
        in das Log-Feld in der GUI und sperrt es dann wieder mit [...]tk.DISABLED --> sonst ist es ein Eingabefeld
        
        Prüft ob Topic eingegeben wurde.
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

        # Callback-Funktionen (erneut) setzen und Verbindung (wieder) herstellen
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(broker, port, 180)  # Keep-Alive-Time
        self.client.loop_start() #startet separaten Thread im selben Netzwerk

        #Informiere Nutzer über positive Verbindungsherstellung
        self.gui.log_text.config(state=tk.NORMAL)
        self.gui.log_text.insert("end", f"\nConnected with broker '{broker}'\nSubscribing to topic: '{self.topic}'")
        self.gui.log_text.config(state=tk.DISABLED)

        # 'Connect'-Button wird grün, solange Keep-Alive-Time aktiv ist -> aktuell 3 Minuten
        connect_button = self.gui.top_frame.winfo_children()[-1]  # Letztes Element im Frame ist der Button selbst
        original_color = connect_button.cget("style") #Speichert ursprünglichen Button-Style
        connect_button.configure(style="success.TButton") #Wird vorrübergehend Grün = Verbindung hergestellt (3 Minuten lang)
        self.gui.root.after(180 * 1000, lambda: connect_button.configure(style=original_color))

        # Entferne den Hinweis "Keine aktuellen Verbindungen"
        self.gui.canvas.delete("no_connection")
        self.gui.canvas.delete("no_connection2")

        self.gui.draw_connection_arrows()

    def on_connect(self, client, userdata, flags, rc):
        """
        Callback-Funktion die aufgerufen wird, sobald der MQTT-Client
        eine Antwort vom Broker auf den Verbindungsversuch erhält.

        Kurze Erklärung zu Parametern:
            - client --> ist der MQTT-Client
            - userdata --> benutzdefinierte Daten (ungenutzt)
            - flags --> sind die Antworten vom Broker
            - rc --> Rückgabecode (Erfolgreich = 0; Fehler != 0)

        """
        #Erfolgreiche-Verbindung mit Erfolgsmeldung
        if rc == 0:
            self.gui.log_text.config(state=tk.NORMAL)
            self.gui.log_text.insert("end", " - Successfully connected.\n")
            self.gui.log_text.config(state=tk.DISABLED)
            client.subscribe(self.topic + "/#") #MQTT-Wildecard -> abboniere das Topic UND alle Unterthemen
        #Fehlermeldung mit Rückmeldung
        else:
            self.gui.log_text.config(state=tk.NORMAL)
            self.gui.log_text.insert("end", f"Connection failed with error code '{rc}'.\n")
            self.gui.log_text.config(state=tk.DISABLED)

    def on_message(self, client, userdata, message):
        """
        Callback-Funktion, sobald eine Nachricht empfangen wird.

        Verweis auf die GUI-Animation: Je nach Topic wird eine andere Animation ausgeführt.

        Kurze Erklärung zu Parameter:
            - message: empfangene Nachricht (+ Topic + Payload) 
                    --> wird von Binärcode in lesbaren für Menschen verständlichen String übersetzt
        """
        incoming_message = f"\nTopic: '{message.topic}'  +++ Incoming message: '{message.payload.decode('utf-8')}' +++\n"
        self.gui.log_text.config(state=tk.NORMAL)
        self.gui.log_text.insert("end", incoming_message)
        self.gui.log_text.see("end")
        self.gui.log_text.config(state=tk.DISABLED)

        """
        Basierend auf dem Subtopic wird eine Animation ausgelöst sobald die
        Eingangsnachricht eines der Topics enthält
        """
        subtopic = message.topic.split("/")[-1] #Filtern des subtopics
        # Unterscheidung der Eingangsnachricht zur Animation
        if subtopic == 'toERP':
            self.gui.start_animation('toERP')
        elif subtopic == 'toMES':
            self.gui.start_animation('toMES')
        else:
            print(f"Unknown topic: '{message.topic}'.") #Gibt Fehler wenn Topic unbekannt
