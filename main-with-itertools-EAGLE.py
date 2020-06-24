#Eagle is a test to see why the process keeps being started over on socet conneciton.

from utils import print_grid, file_to_list, gut_words, ungut_words, make_dict, sum_dicts, prepare_helium, test_data
import time
import eventlet
import socketio
import math
import threading
from itertools import *
eventlet.monkey_patch()

sio = socketio.Server(cors_allowed_origins='*')

app = socketio.WSGIApp(sio, static_files={
    '/': {'content_type': 'text/html', 'filename': 'index.html'}
})


def chunky():
    global switch
    while switch:
        # print(1)
        for a in range(100000000):
            for b in range(100000000):
                for c in range(100000000):
                    if a + b + c % 58713 == 0:
                        print(a + b + c)
                        if a + b + c == 99999559:
                            print("Process ended naturally.")
    else:
        print("Terminated by switch.")

def turn_off():
    global switch
    switch = 0
    print("************************************")
    print("************************************")
    print("************************************")
    print("************************************")
    print("************************************")
    print("************************************")

# switch = 1
# chunky()
# t = threading.Timer(0.5, turn_off)
# t.start()

switch = 0

@sio.event
def connect(sid, environ):
    print('Client connected: ', sid)
    sio.emit("message", {"message": "Eagle confirms that the client has connected."})

@sio.event
def eagle(sid, data):
    global switch
    switch = 1
    chunky()

@sio.event
def eagle_off(sid, data):
    global switch
    switch = 0
    print("************************************")
    print("************************************")
    print("************************************")
    print("************************************")
    print("************************************")
    print("************************************")

sio.on('connect', connect);
sio.on('eagle', eagle);
sio.on('eagle off', eagle_off);


if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 5003)), app)