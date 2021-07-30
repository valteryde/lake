
# VALTERT 2021
# MIT LICENSE

import webbrowser
import socket
import time
from _thread import start_new_thread
import os, sys #signal
import json

from flask import * #pip install package|module
from .websocket_server import WebsocketServer #file
# from bs4 import BeautifulSoup


# *** CONST ***
URL = 'http://127.0.0.1:5000/_boot_'
PID = os.getpid()
SLEEP_TIME = 1#s
FRONT_FOLDER = 'front'
DUMMY_DICT = {'intjected_html_files':["landing.html", "redirect.html"]}
BASE_FOLDER = os.getcwd()



# *** CODE TO BE PLOTTED INTO FILES
HTML_JS_INJECT = """<script src="https://code.jquery.com/jquery-3.6.0.min.js" charset="utf-8"></script><script src="{{ url_for('static', filename='lake.js') }}" charset="utf-8"></script>"""




# *** REMOTE CONNECTION ***
# This class will be the remote connection
# with the document obj from the client browser side
# this also has a map|dict of all the functions made by the decorator (@remote.function)

# maybe instead of doing all the document.getElementById();
# then just expose a few functions
# we can automatially, be default, expose the querryElement('#htmldomElementID') function
# and some other functions


class Remote:

    def __init__(self):
        self.functions = {}


    # passed to the msg handeling in Lake class
    def _executeFunction_(self, funcName):

        try:
            self.functions[funcName]()
        except NameError:
            return


    #the decorator
    def function(self, f):
        self.functions[f.__name__] = f

    # remote connection
    def do(self, funcname, *args):
        self.server.send_message_to_all('[exe]('+str(funcname)+')')



# *** APP CLASS ***
class Lake:

    def standardBootPage():
        #name = request.args.get("name", "World")
        return render_template('landing.html')


    # *** INIT ***
    def __init__(self, name='my lake app', landingpage=standardBootPage):
        self.app = Flask(name, template_folder=os.path.join(BASE_FOLDER, FRONT_FOLDER,'templates'), static_url_path=None)
        self.route = self.app.route
        self.remote = Remote()

        # setting the static folder url
        self.app.static_folder = os.path.join(BASE_FOLDER, FRONT_FOLDER, 'static')

        # Websocket state
        self.websocketState = 'open' #open, switching, closed

        #Before request function
        #to handle websocket connection
        @self.app.before_request
        def before_request_callback():
            self.websocketState = 'switching'


        @self.route('/_boot_')
        def redirect():
            return render_template('redirect.html')


        @self.route('/')
        def start():
            return landingpage()


        #open cache
        if 'lakecache.json' in os.listdir():
            cache = open('lakecache.json', 'r+')
            cache_text = cache.read()
        else:
            cache = open('lakecache.json', 'w+')
            dumped = json.dumps(DUMMY_DICT)
            cache.write(dumped)
            cache_text = dumped

        # retv cached info into a dict (d)
        d = json.loads(cache_text, strict=False)

        # include js into all renders
        for fileName in os.listdir(os.path.join(BASE_FOLDER, FRONT_FOLDER, 'templates')):

            # check cache
            if fileName not in d['intjected_html_files']:
                file = open(os.path.join(BASE_FOLDER, FRONT_FOLDER, 'templates', fileName), 'r+')

                raw_text = file.read()
                if HTML_JS_INJECT not in raw_text:

                    #place it just before the headtag
                    index = raw_text.index('<head>')
                    new_text = '<head>\n    ' + HTML_JS_INJECT + raw_text[index:]

                    file.seek(index)
                    file.truncate()

                    file.write(new_text)
                d['intjected_html_files'].append(fileName)

                file.close()

        cache.seek(0)
        cache.truncate()
        cache.write(json.dumps(d))


    #*** "WEB"SOCKET ***
    # Called for every client connecting (after handshake)
    def _socketOpened_(self, client, server):
        self.websocketState = 'open'
        self.websocketBypass = True
        print("\033[32m[INFO] Contact with the browser's websocket was made\033[0m")
        server.send_message_to_all('[MSG] Welcome user')


    # Called for every client disconnecting
    def _socketClosed_(self, client, server):
        time.sleep(SLEEP_TIME)

        if self.websocketBypass:
            self.websocketBypass = False
            return


        if self.websocketState == 'open': #!switching
            print('\033[91m[INFO] Server closing\033[0m')
            os.kill(PID, 9) #os.kill(PID, signal.SIGSTOP)


    # Called when a client sends a message
    def _msgRecv_(self, client, server, msg):

        # welcome message
        if msg == '[welcome]':
            time.sleep(SLEEP_TIME)
            self.websocketBypass = False


        if '[' in msg and ']' in msg:
            tp = msg[msg.index('[')+1:msg.index(']')]
            if tp.lower() == 'switching':
                self.websocketState = 'switching'
            elif tp.lower() == 'exe':

                # pass it to the remote class
                self.remote._executeFunction_(msg[msg.index('(')+1:msg.index(')')])

        else:
            print('[INFO] User sent msg without type')


    def _startWebsocketServer_(self):
        server = WebsocketServer(8765, host='localhost')

        self.remote.server = server

        server.set_fn_new_client(self._socketOpened_)
        server.set_fn_client_left(self._socketClosed_)
        server.set_fn_message_received(self._msgRecv_)
        server.run_forever()


    # *** RUN ***
    def run(self):

        os.system('clear') #only on darwin && linux
        start_new_thread(self._startWebsocketServer_, ())
        start_new_thread(webbrowser.open, (URL,))
        self.app.run()
