from flask import Flask, render_template, request, send_from_directory
from flask_socketio import SocketIO, emit

import os
import re
import requests
import random
import threading
from html import escape as html_escape
from math import sin, cos, pi, radians
from itertools import repeat, chain
from collections import deque
from dateutil.parser import parse as time_parse

from gevent import monkey, sleep
monkey.patch_all()

app = Flask(__name__)
socketio = SocketIO(app)

app.secret_key='pasta_elephant_green_leaf_shoe'
app.config['MAX_FEEDS']=7   
app.config['IMAGE_HEIGHT']=7
thread = threading.Thread()
thread_stop_event = threading.Event()
connections = dict()

class Connection(object):
    def __init__(self, sid):
        self.sid = sid
        self.connected = True
        self.session = dict()

    def emit(self, event, data):
        socketio.emit(event, data, room=self.sid)

# CORS handling from http://coalkids.github.io/flask-cors.html
@app.before_request
def option_autoreply():
    if request.method == 'OPTIONS':
        resp = app.make_default_options_response()
        headers = None
        if 'ACCESS_CONTROL_REQUEST_HEADERS' in request.headers:
            headers = request.headers['ACCESS_CONTROL_REQUEST_HEADERS']
        h = resp.headers
        h['Access-Control-Allow-Origin'] = request.headers['Origin']
        h['Access-Control-Allow-Methods'] = request.headers['Access-Control-Request-Method']
        h['Access-Control-Max-Age'] = "10"
        if headers is not None:
            h['Access-Control-Allow-Headers'] = headers
        return resp

@app.after_request
def set_allow_origin(resp):
    h = resp.headers
    if request.method != 'OPTIONS' and 'Origin' in request.headers:
        h['Access-Control-Allow-Origin'] = request.headers['Origin']
    return resp

def range(x, y, jump):
  while x < y:
    yield x
    x += jump

@app.route('/static/sky.png')
def skybox():
    return send_from_directory('static','sky-tron.png')

@app.route('/static/aframe.min.js')
def aframe():
    return send_from_directory('static','aframe.min.js')

@app.route('/static/sand.jpg')
def sand():
    return send_from_directory('static','sand.jpg')

@app.route('/static/next.png')
def next_img():
    return send_from_directory('static','next_page.png')

@app.route('/static/back-button.jpg')
def backbutton():
    return send_from_directory('static','back-button.jpg')

@app.route('/static/button_click.ogg')
def button_click_mp3():
    return send_from_directory('static','button_press.ogg')

@app.route('/static/whoosh.ogg')
def whooshmp3():
    return send_from_directory('static','whoosh.ogg')

@app.route('/static/back.ogg')
def backmp3():
    return send_from_directory('static','back.ogg')

@app.route('/futura.fnt')
def futura():
    return send_from_directory('static','futura.fnt')

@app.route('/futura.png')
def futurapng():
    return send_from_directory('static','futura.png')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static','favicon.ico')

@app.route('/gear-controls.html')
def gearcontrols():
    return send_from_directory('static','gear-controls.html')

@app.route('/vive-controls.html')
def vivecontrols():
    return send_from_directory('static','vive-controls.html')

@app.route('/static/main.js')
def mainjs():
    return send_from_directory('static','main.js')

@app.route('/static/controls.js')
def controlsjs():
    return send_from_directory('static','controls.js')

@app.route('/static/move_animations.js')
def movejs():
    return send_from_directory('static','move_animations.js')

def calculate_img_positions(num_images):
    return [(cos(theta),sin(theta)) for theta in range(0,360,360/num_images)]

class ThetaIterator(object):
    def __init__(self, num_images):
        self.num_images = num_images
        self.thetas = ["0 "+str(-1*x)+" 0" for x in range(0,360,360/num_images)]
        self.index = 0

    def next(self):
        to_return = self.thetas[self.index]
        self.index = (self.index+1)%len(self.thetas)
        return to_return
    
    def previous(self):
        self.index = self.index-1

class ThetaTextIterator(object):
    def __init__(self):
        self.text_thetas = [150,90,-30,30,90,150]
        self.index = 0
    
    def next(self):
        to_return = self.text_thetas[self.index]
        self.index = (self.index+1)%len(self.text_thetas)
        return to_return

    def previous(self):
        self.index = self.index-1

def calculate_image_widths(num_images):
    return (2*pi)/(num_images*5)

def shorten_message(text):
    text = re.sub(re.compile(r'[\s]+'), r" ", text)
    sub_length = 83
    if len(text)>sub_length:
        text = text[:sub_length-3]+'...'
    else:
        text = text
    return html_escape(text)

def calculate_text_pos_height(text):
    line_len_list = [-0.12,-0.22,-0.31,-0.4,-0.4,-0.4]
    lines = len(text)//20
    try:
        return str(line_len_list[lines])
    except:
        raise ValueError

class URLContainer(object):
    def __init__(self):
        self.urls=list()
    
    def append(self, to_append):
        try:
            if self.urls[-1]!=to_append:
                self.urls.append(to_append)
        except IndexError:
            self.urls.append(to_append)
    
    def pop(self):
        print(self.urls)
        try:
            del self.urls[-1]
            to_pop = self.urls[-1]
            try:
                if to_pop != self.urls[-2]:
                    del self.urls[-1]
                    return to_pop
                else:
                    del self.urls[-1]
                    to_pop = self.urls[-1]
                    del self.urls[-1]
                    return to_pop
            except IndexError:
                del self.urls[-1]
                return to_pop
        except IndexError:
            return 'view0'

def url_from_id(id, stack=True):
    try:
        print("trying!")
        if "?" not in id:
            raise ValueError
        stack_id, page_start = str(id).split("?")
        return 'http://slopeofhope.com/socialtrade/app/tagged-items/stack_'+stack_id+'.json'+"?"+page_start
    except ValueError:
        if stack:
            return 'http://slopeofhope.com/socialtrade/app/stacks/substacks_'+str(id)+'.json'
        else:
            return 'http://slopeofhope.com/socialtrade/app/tagged-items/stack_'+str(id)+'.json'

def parse_json(url):
    print("vvvvvvvvvvvvvvvvv")
    print(url)
    print("^^^^^^^^^^^^^^^^^")
    global connections
    is_stack = True
    cur_sid = request.sid
    connections[cur_sid].session['current_views']=[]
    response = requests.get(url)

    data = response.json()
    num_feeds = 0
    if len(data["entries"])==0:
        # not a stack
        is_stack = False
        url = url_from_id(connections[cur_sid].session['id'], stack=False)
        response = requests.get(url)
        data = response.json()
        num_feeds = 0
        thetas = ThetaIterator(min(app.config["MAX_FEEDS"],len(data["entries"])))
    thetas = ThetaIterator(min(app.config["MAX_FEEDS"],len(data["entries"])))
    iters = 0
    text_thetas = ThetaTextIterator()
    for cur_ind, entry in enumerate(data["entries"]):
        iters += 1
        theta = thetas.next()
        text_theta = text_thetas.next()
        unit_theta = 360/min(app.config["MAX_FEEDS"],len(data["entries"]))
        num_feeds += 1
        parsed_images = []
        cur_theta = -1*float(theta[2:-2])
        theta_adj = 10
        pos_x = str(10*cos(radians(cur_theta+unit_theta+theta_adj+50/4)))
        pos_y = str(10*sin(radians(cur_theta+unit_theta+theta_adj+50/4)))
        current_level = ((cur_ind)//app.config["MAX_FEEDS"])
        height_offset = 5
        image_height = str((3/4)+9.25*current_level+height_offset)
        button_height = str(1/2+5+9.25*(current_level-1)+height_offset)
        person_move = str(2.2+1/2+5+9.25*(current_level-1)+height_offset)
        try:
           entry['name']
        except KeyError:
            is_stack = False
        if is_stack:
            name = entry['name']
            for img_url in entry["preview"]:
                parsed_url = img_url[:-2]+'_l'
                parsed_url = re.sub(r'https://',r'http://',parsed_url)
                parsed_images.append(parsed_url)
            image = random.choice(parsed_images)
            str_id = str(entry["id"])
        else:
            try:
                name = entry['item']['description']
                date = time_parse(entry['item']['posted_on']).strftime("%m/%d/%y")
                name = "["+date+"] "+name
                image = entry['item']['image_url'][:-2]
                str_id = str(entry['item']['id'])
            except TypeError:
                thetas.previous()
                text_thetas.previous()
                continue
        name = shorten_message(name)
        if not is_stack:
            sort_index = str(time_parse(entry['item']['posted_on']))
        else:
            sort_index = name
        current_view = {"id":"view"+str_id,
                        "hash_id":"#view"+str_id,
                        "name":name,
                        "text_pos_height":calculate_text_pos_height(name),
                        "image":image,
                        "button_height": person_move,
                        "button_pos":' '.join([pos_x,button_height,pos_y]),
                        "button_rot":' '.join(["0",str(-1*(cur_theta+unit_theta+50/2)),"0"]),
                        "image_pos":' '.join(["0",image_height,"0"]),
                        "theta":theta,
                        "level":str(current_level+1),
                        "is_stack":is_stack,
                        "sort_index":sort_index}
        connections[cur_sid].session['current_views'].append(current_view)

    if not is_stack and (iters == 50):
        cur_ind += 1
        theta = thetas.next()
        text_theta = text_thetas.next()
        unit_theta = 360/min(app.config["MAX_FEEDS"],len(data["entries"]))
        num_feeds += 1
        cur_theta = -1*float(theta[2:-2])
        pos_x = str(10*cos(radians(cur_theta+unit_theta+theta_adj+50/4)))
        pos_y = str(10*sin(radians(cur_theta+unit_theta+theta_adj+50/4)))
        current_level = ((cur_ind)//app.config["MAX_FEEDS"])
        image_height = str((3/4)+9.25*current_level+height_offset)
        button_height = str(1/2+5+9.25*(current_level-1)+height_offset)
        person_move = str(2.2+1/2+5+9.25*(current_level-1)+height_offset)
        print(url)
        try:
            str_id = re.findall(r"_\d+",url)[-1][1:]+"?start="+str(int(re.findall(r"\?start=[\d]+",url)[-1][7:])+50)
        except IndexError:
            str_id = re.findall(r"_\d+",url)[-1][1:]+"?start=50"
        str_id = str_id.replace("?","question__mark").replace("=","equals__sign")
        current_view = {"id":"view"+str_id,
                        "hash_id":"#view"+str_id,
                        "name":"More",
                        "text_pos_height":calculate_text_pos_height(""),
                        "image":"/static/next.png",
                        "button_height": person_move,
                        "button_pos":' '.join([pos_x,button_height,pos_y]),
                        "button_rot":' '.join(["0",str(-1*(cur_theta+unit_theta+50/2)),"0"]),
                        "image_pos":' '.join(["0",image_height,"0"]),
                        "theta":theta,
                        "level":str(current_level+1),
                        "is_stack":True,
                        "sort_index":"9999999"}
        connections[cur_sid].session['current_views'].append(current_view)

    connections[cur_sid].session['current_views'] = \
            sorted(connections[cur_sid].session['current_views'], key=lambda item:item['sort_index'], reverse=False)
    return True

class ViveChecker(threading.Thread):
    def __init__(self):
        self.delay = 1
        super(ViveChecker, self).__init__()
 
    def vive_connected(self):
        while not thread_stop_event.isSet():
            socketio.emit('check_vive_connected', broadcast=True)
            sleep(self.delay)
    
    def run(self):
        self.vive_connected()

def receive_sent_views(data):
    global connections
    viewpath = data.replace("question__mark","?").replace("equals__sign","=")
    cleaned_id = viewpath[4:]
    connections[request.sid].session['id'] = cleaned_id
    connections[request.sid].session['json_feed']=url_from_id(cleaned_id)
    connections[request.sid].session['current_views']=[]
    parse_json(connections[request.sid].session['json_feed'])
    img_width = calculate_image_widths(len(connections[request.sid].session['current_views']))
    try:
        connections[request.sid].emit('receive_views', connections[request.sid].session['current_views'])
    except KeyError:
        print("ConnectionWarn: Creating new connection")
        connections[request.sid] = Connection(request.sid)
        connections[request.sid].emit('receive_views', connections[request.sid].session['current_views'])

@socketio.on('send_view') # when button is clicked...
def on_button_click(send_view):
    connections[request.sid].session['url_container'].append(send_view['data'])
    return receive_sent_views(send_view['data'])

@socketio.on('go_back')
def go_back():
    return receive_sent_views(connections[request.sid].session['url_container'].pop())

@socketio.on('connect')
def connect_and_send_views():
    global thread, connections
    connections[request.sid] = Connection(request.sid)
    if not thread.isAlive():
        print("Starting heartbeat thread...")
        thread = ViveChecker()
        thread.start()
    connections[request.sid].session['previous_id']='view0'
    connections[request.sid].session['url_container'] = URLContainer()
    receive_sent_views('view0')

@socketio.on('heartbeat')
def heartbeat():
    return

@socketio.on('disconnect')
def disconnect():
    try:
        del connections[request.sid]
    except KeyError:
        print("ConnectionWarn: Deleting connection that never exsisted")
    print("Client "+str(request.sid)+" disconnected")

@app.route('/')
def main():
    return render_template('index.html')

if __name__=='__main__':
    port = int(os.environ.get('PORT', 5000))
    print("Port: ",port)
    socketio.run(app, host='0.0.0.0',port=port, debug=True, logger=False)
