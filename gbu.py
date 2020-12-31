import bluetooth
from tkinter import *
import tkinter.ttk as ttk
import threading
import time
import tkinter.messagebox as messages

devices = []
tk = Tk()
devicesVar = StringVar(tk, value = devices)
deviceName = StringVar(tk, value = "Device name: None")
deviceMAC = StringVar(tk, value = "Device MAC Address: None")
deviceClass = StringVar(tk, value = "Device Class: None")
sendInput = StringVar(tk)
isConnected = BooleanVar(tk)

btSocket = None

messageQueue = []

def scan():
    print("Scanning for bluetooth devices")
    scanButton.state(['disabled'])
    btScanThread = threading.Thread(target = scanSubprocess, name = "btscanthread", daemon = True)
    connectLoader.grid(column=0, row=16, pady=[5,0])
    btScanThread.start()
    while btScanThread.is_alive():
        tk.update()
        tk.update_idletasks()
    print("scan finished")
    scanButton.state(['!disabled'])
    connectLoader.grid_forget()

def recieveListener():
    global messageQueue, isConnected
    while isConnected:
        try:
            messageQueue.append(btSocket.recv(1024))
        except bluetooth.btcommon.BluetoothError as err:
             messages.showerror(title="Connection Error", message="Connection terminated. \nError: " + str(err) + "\nPlease restart the program.")
        #print("Recieved message")

def connectToDevice(selection):
    global btSocket
    device = devices[selection[0]]
    addr = device[0]
    port = 1
    btSocket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    btSocket.connect((addr,port))
    deviceName.set("Device name: " + device[1])
    deviceMAC.set("Device MAC Address: " + device[0])
    deviceClass.set("Device class: " + str(device[2]))
    isConnected.set(True)
    recieveThread.start() 
    sendButton.state(['!disabled'])
    disconnectButton.state(["!disabled"])

def updateLog():
    for item in messageQueue:
        writeToDataLog(bytes.fromhex(item.hex()))
        print(item.hex())
        messageQueue.remove(item)
    tk.after(100, updateLog)

def scanSubprocess():
    global devices
    devices = bluetooth.discover_devices(lookup_names = True, lookup_class = True,
                                            flush_cache=True, duration=5)
    devicesList = []
    for name in devices:
        devicesList.append(name[1])
    devicesVar.set(devicesList)
    print(devicesVar.get())

def disconnectFromDevice(ask = True):
    if ask:
        if messages.askyesno(title='Disconnect???', message="Do you really want to disconnect??? Just want to be sure."):
            isConnected.set(False)
            sendButton.state(['disabled'])
            disconnectButton.state(["disabled"])
            btSocket.close()
            deviceName.set("Device name: None")
            deviceMAC.set("Device MAC Address: None")
            deviceClass.set("Device class: None")
    else:
        isConnected.set(False)
        sendButton.state(['disabled'])
        disconnectButton.state(["disabled"])
        btSocket.close()
        deviceName.set("Device name: None")
        deviceMAC.set("Device MAC Address: None")
        deviceClass.set("Device class: None")

def sendMessage():
    btSocket.send(sendInput.get())

def writeToDataLog(msg):
    numlines = int(dataLog.index('end - 1 line').split('.')[0])
    dataLog['state'] = 'normal'
    if numlines==24:
        dataLog.delete(1.0, 2.0)
    if dataLog.index('end-1c')!='1.0':
        dataLog.insert('end', '\n')
    dataLog.insert('end', msg)
    dataLog['state'] = 'disabled'

recieveThread = threading.Thread(target = recieveListener, name = "recievelistenerthread", daemon = True)

tk.geometry("550x500")
tk.title("Ginger Bluetooth Utils")
tk.resizable(0, 0)
tabControl = ttk.Notebook(tk)
connectionTab = ttk.Frame(tabControl)
sendRecieveTab = ttk.Frame(tabControl)
tabControl.add(connectionTab, text='Connection')
tabControl.add(sendRecieveTab, text='Send/Recieve')
tabControl.pack(expand=1, fill="both")

devicesLabel = Label(connectionTab, text="Device info")
devicesLabel.grid(column=1, row=0)

nameLabel = Label(connectionTab, textvariable = deviceName)
nameLabel.grid(column = 1, row = 1, sticky="W", padx = [5,0])
macLabel = Label(connectionTab, textvariable = deviceMAC)
macLabel.grid(column = 1, row = 2, sticky="W", padx = [5,0])
classLabel = Label(connectionTab, textvariable = deviceClass)
classLabel.grid(column = 1, row = 3, sticky="W", padx = [5,0])

scanButton = ttk.Button(connectionTab, text='Scan', command=scan)
scanButton.grid(column=0, row=17, pady=[5,0])

devicesFrame = ttk.Labelframe(connectionTab, text='Devices')
devicesFrame.grid(column=0, row=0, rowspan=10, padx = [5,0], pady = [5,0])
devicesFrame['padding'] = (5, 0, 5, 5)
devicesFrame['relief'] = 'ridge'
devicesListbox = Listbox(devicesFrame, height = 10, listvariable=devicesVar)
devicesListbox.grid(column=0, row=1, rowspan=10)
devicesListbox.bind("<Double-1>", lambda e: connectToDevice(devicesListbox.curselection()))

connectLoader = ttk.Progressbar(connectionTab, orient= "horizontal", length = 190, mode = "indeterminate")
connectLoader.start(5)

dataLog = Text(sendRecieveTab, state='disabled', width=70, height=24, wrap='none')
dataLog.grid(column=0, row=0, pady=[5,0], columnspan=2)

sendEntry = ttk.Entry(sendRecieveTab, textvariable=sendInput, width=45)
sendEntry.grid(column=0, row=1, sticky="W", pady=[5,0])

sendButton = ttk.Button(sendRecieveTab, text='Send', command=sendMessage, state = "disabled")
sendButton.grid(column=1, row=1, sticky="W", pady=[5,0])

disconnectButton = ttk.Button(connectionTab, text='Disconnect', command=disconnectFromDevice, state = "disabled")
disconnectButton.grid(column=1, row=4)

writeToDataLog("Messages recieved from a connected device will appear here.\n")
tk.after(100, updateLog)
tk.mainloop()
