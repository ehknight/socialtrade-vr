from flask import Flask, session, render_template, request, send_from_directory
from flask_cors import CORS
from flask.ext.socketio import SocketIO, emit

import os
import re
import requests
import random
from math import sin, cos, pi, radians
from itertools import repeat
from itertools import chain
from scipy import arange as range
from collections import deque

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app)

app.secret_key='pasta_elephant_green_leaf_shoe'
app.config['MAX_FEEDS']=7   
app.config['IMAGE_HEIGHT']=7

@app.route('/static/sky.png')
def skybox():
    return send_from_directory('static','sky-tron.png')

@app.route('/static/aframe.min.js')
def aframe():
    return send_from_directory('static','aframe.min.js')

@app.route('/static/sand.jpg')
def sand():
    return send_from_directory('static','sand.jpg')

@app.route('/static/back-button.jpg')
def backbutton():
    return send_from_directory('static','back-button.jpg')

@app.route('/futura.fnt')
def futura():
    return send_from_directory('static','futura.fnt')

@app.route('/futura.png')
def futurapng():
    return send_from_directory('static','futura.png')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static','favicon.ico')

def calculate_img_positions(num_images):
    return [(cos(theta),sin(theta)) for theta in range(0,360,360/num_images)]

def calculate_img_theta(num_images):
    return chain.from_iterable(repeat((["0 "+str(x)+" 0" for x in range(
                                  0,360,360/num_images)])))

def calculate_text_thetas():
    return chain.from_iterable(repeat([150,90,-30,30,90,150]))

def calculate_image_widths(num_images):
    return (2*pi)/(num_images*5)

def create_scene():
    return render_template(json_feed=session['json_feed'],
                           previous=session['previous'])

def shorten_message(text):
    text = re.sub(re.compile(r'\W+'), r" ", text)
    if len(text)>92:
        return text[:88]+'...'
    else:
        return text

def calculate_text_pos_height(text):
    line_len_list = [-0.12,-0.22,-0.31,-0.4,-0.52,-0.55]
    lines = len(text)//16
    try:
        return str(line_len_list[lines])
    except:
        print(lines)
        raise ValueError

def url_from_id(id, stack=True):
    if stack:
        return 'http://slopeofhope.com/socialtrade/app/stacks/substacks_'+str(id)+'.json'
    else:
        return 'http://slopeofhope.com/socialtrade/app/tagged-items/stack_'+str(id)+'.json'

def parse_json(url):
    global session
    is_stack = True
    session['current_views']=[]
    print("started response")
    response = requests.get(url)
    data = response.json()
    print("finished response")
    num_feeds = 0
    print(data["entries"])
    if len(data["entries"])==0:
        # not a stack
        is_stack = False
        url = url_from_id(session['id'], stack=False)
        print(url)
        response = requests.get(url)
        print("response:")
        print(response)
        data = response.json()
        print("finished response")
        num_feeds = 0
        print(data["entries"])
        print(len(data["entries"]))
        thetas = calculate_img_theta(min(app.config["MAX_FEEDS"],len(data["entries"])))
    thetas = calculate_img_theta(min(app.config["MAX_FEEDS"],len(data["entries"])))
    text_thetas = calculate_text_thetas()
    print(thetas)
    for cur_ind, entry in enumerate(data["entries"]):
        theta = next(thetas)
        text_theta = next(text_thetas)
        unit_theta = 360/min(app.config["MAX_FEEDS"],len(data["entries"]))
        num_feeds += 1
        parsed_images = []
        cur_theta = -1*float(theta[2:-2])
        theta_adj = 10
        pos_x = str(10*cos(radians(cur_theta+unit_theta+theta_adj)))
        pos_y = str(10*sin(radians(cur_theta+unit_theta+theta_adj)))
        current_level = ((cur_ind)//app.config["MAX_FEEDS"])
        height_offset = 5
        image_height = str((3/4)+9.25*current_level+height_offset)
        button_height = str(1/2+5+9.25*(current_level-1)+height_offset)
        person_move = str(2.2+1/2+5+9.25*(current_level-1)+height_offset)
       
        if is_stack:
            name = entry['name']
            for img_url in entry["preview"]:
                parsed_url = img_url[:-2] # remove "_l"
                parsed_url = re.sub(r'https://',r'http://',parsed_url)
                parsed_images.append(parsed_url)
            image = random.choice(parsed_images)
            str_id = str(entry["id"])
        else:
            try:
                name = entry['item']['description']
                print(entry['item']['image_url'])
                image = entry['item']['image_url'][:-2]
                str_id = str(entry['item']['id'])
            except TypeError:
                continue
        name = shorten_message(name)
        current_view = {"id":"view"+str_id,
                        "hash_id":"#view"+str_id,
                        "name":name,
                        "text_pos_height":calculate_text_pos_height(name),
                        "image":image,
                        "button_height": person_move,
                        "button_pos":' '.join([pos_x,button_height,pos_y]),
                        "button_rot":' '.join(["0",str(-1*(cur_theta+unit_theta)),"0"]),
                        "image_pos":' '.join(["0",image_height,"0"]),
                        "theta":theta,
                        "is_stack":is_stack}
        session['current_views'].append(current_view)
    return True

def receive_sent_views(data):
    global session
    viewpath = data
    print(viewpath)
    cleaned_id = int(viewpath[4:])
    print("cleaned id:")
    print(cleaned_id)
    session['id'] = cleaned_id     
    session['json_feed']=url_from_id(cleaned_id)
    session['current_views']=[]
    parse_json(session['json_feed'])
    img_width = calculate_image_widths(len(session['current_views']))
    socketio.emit('receive_views', session['current_views'])

@socketio.on('send_view') # when button is clicked...
def on_button_click(send_view):
    global session
    session['url_deque'].append(send_view['data'])
    print("received click")
    return receive_sent_views(send_view['data'])

@socketio.on('go_back')
def go_back():
    global session
    try:
        session['previous_id'] = session['url_deque'].pop()
    except:
        session['url_deque'] = deque(['view0'])
        session['previous_id'] = 'view0'
    return receive_sent_views(session['url_deque'])

@socketio.on('connect')
def connect_and_send_views():
    global session
    session['previous_id']='view0'
    session['url_deque'] = deque(['view0'])
    receive_sent_views('view0')

@socketio.on('disconnect')
def disconnect():
    print("Client disconnected")

# @app.route('/id/<viewpath>')
# def new_view(viewpath):
#     global session
#     try:
#         session['previous']
#         session['previous']=session['json_feed']
#     except KeyError:
#         session['previous']=url_from_id(0)
#     cleaned_id = int(viewpath[4:])
#     print("cleaned id:")
#     print(cleaned_id)
#     session['id'] = cleaned_id     
#     session['json_feed']=url_from_id(cleaned_id)
#     session['current_views']=[]
#     parse_json(session['json_feed'])
#     img_width = calculate_image_widths(len(session['current_views']))
#     return render_template('index.html',
#                            width=img_width,
#                            height=img_width*(2/3),
#                            views=session['current_views'])

@app.route('/')
def main():
    return render_template('index.html')

if __name__=='__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0',port=port, debug=True)
