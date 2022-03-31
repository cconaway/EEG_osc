#IMPORT STANDARD
import time
import numpy as np

#IMPORT CUSTOM
from mv import MovingAverage

#IMPORT 3rd PARTY
from pythonosc.osc_server import ThreadingOSCUDPServer
from pythonosc.dispatcher import Dispatcher
from pythonosc import udp_client

#Set Server IP - BaseStation Sending EEG OSC
server_ip = "192.168.0.55"
server_port = 8000

#Set Client IP - LocalHost -> OSC Reciever 
client_ip = "127.0.0.1"
client_port = 8001

#Create Client - Goes into Functions Below
client = udp_client.SimpleUDPClient(client_ip, client_port)

#Create Dispatch variables
dispatch_list = [
    'alpha_relative',
    'beta_relative',
    'theta_relative',
    'delta_relative',
    'gamma_relative'
]

#Make Moving Averages
mvs = [MovingAverage(size = 30) for i in range(len(dispatch_list))]

#Applies Moving Average
def data_proc(mv, args):
    arg = sum(args)/len(args) 
    return mv.next(arg)

#Print Handler
def handler(address, *args):
    print(f"{address}: {args}")

    #Process
    return_mv = data_proc(args[0][1], args[1:])
    #Send
    client.send_message("{}_mvgAvg".format(address), return_mv)
    time.sleep(1)
    #client.send_message("{}_rawrel".format(address), sum(args[1:])/len(args[1:]))

dispatcher = Dispatcher()
for i in range(len(dispatch_list)):
    dispatcher.map(f"/muse/elements/{dispatch_list[i]}", handler, dispatch_list[i], mvs[i])

#Create Server - Threading Blocks Further Program Execution
server = ThreadingOSCUDPServer((server_ip, server_port), dispatcher) 

#MainLoop - Runs Server and Sends.
if __name__ == "__main__":
    print("Serving on {}".format(server.server_address))
    print("Sending to {}".format(client_ip, client_port))  
    server.serve_forever()
