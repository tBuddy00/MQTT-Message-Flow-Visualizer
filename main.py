#############################################################################
# ERKLÄRUNG
#############################################################################
"""
Kurze Erklärung zur Funktion: Eine Instanz von der GUI wird erstellt und dann startet die Hauptschleife
von Tkinter und die Anwendung wird aktiv ausgeführt.

"""
#############################################################################
# IMPORTS
#############################################################################
from gui import MQTTVisualizerGUI

if __name__ == "__main__":
    app = MQTTVisualizerGUI() #ist die Instanz der GUI
    app.run() #Start der Hauptschleife von Tkinter -> Anwendung startet
