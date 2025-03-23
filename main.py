#############################################################################
# DESCRIPTION
#############################################################################
"""
Brief explanation of the function: An instance of the GUI is created and then the 
main loop of Tkinter is started, which keeps the application running.
"""
#############################################################################
# IMPORTS
#############################################################################
from gui import MQTTVisualizerGUI

if __name__ == "__main__":
    app = MQTTVisualizerGUI() #Creates an instance of the GUI
    app.run() #Starts Tkinter's main loop -> application becomes active
