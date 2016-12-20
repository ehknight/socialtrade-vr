from flask import Flask, session, render_template, request, send_from_directory
import requests
from math import sin, cos, pi, radians
import os
from scipy import arange as range
from itertools import repeat
from itertools import chain

app = Flask(__name__)
app.secret_key='pasta_elephant_green_leaf_shoe'
app.config['MAX_FEEDS']=7
app.config['IMAGE_HEIGHT']=7

def calculate_img_positions(num_images):
    return [(cos(theta),sin(theta)) for theta in range(0,360,360/num_images)]

def calculate_img_theta(num_images):
    return chain.from_iterable(repeat((["0 "+str(x)+" 0" for x in range(
                                  0,360,360/num_images)])))

def calculate_image_widths(num_images):
    return (2*pi)/(num_images*5)

def create_scene():
    return render_template(json_feed=session['json_feed'],
                           previous=session['previous'])

def parse_json():
    global session
    session['current_views']=[]
    print("started response")
    response = requests.get(session['json_feed'])
    data = response.json()
    print("finished response")
    num_feeds = 0
    print(data["entries"])
    print(len(data["entries"]))
    thetas = calculate_img_theta(min(app.config["MAX_FEEDS"],len(data["entries"])))
    print(thetas)
    for cur_ind, entry in enumerate(data["entries"]):
        print(entry['name'])
        print(entry['id'])
        theta = next(thetas)
        num_feeds += 1
        parsed_images = []
        int_thetas = -1*float(theta[2:-2])
        pos_x = str(20*cos(radians(int_thetas)))
        pos_y = str(20*sin(radians(int_thetas)))
        height_offset = ((cur_ind+1)//app.config["MAX_FEEDS"])*app.config["IMAGE_HEIGHT"]
        pos_z = str(height_offset+app.config["IMAGE_HEIGHT"]+0.5)
        for img_url in entry["preview"]:
            parsed_images.append(img_url[:-2])
        current_view = {"id":"view"+str(entry["id"]),
                        "hash_id":"#view"+str(entry["id"]),
                        "name":entry["name"],
                        "images":parsed_images,
                        "button_pos":' '.join([pos_x,str(height_offset),pos_y]),
                        "button_rot":' '.join(["0",str(-1*int_thetas),"0"]),
                        "image_pos":' '.join(["0",pos_z,"0"]),
                        "theta":theta}
        session['current_views'].append(current_view)
    return True

def url_from_id(id):
    return 'http://slopeofhope.com/socialtrade/app/stacks/substacks_'+str(id)+'.json'


@app.route('/static/aframe.min.js')
def aframe():
    return send_from_directory('static','aframe.min.js')

@app.route('/id/<viewpath>')
def new_view(viewpath):
    global session
    try:
        session['previous']
        session['previous']=session['json_feed']
    except KeyError:
        session['previous']=url_from_id(0)
    cleaned_id = int(viewpath[4:])
    print("cleaned id:")
    print(cleaned_id)
    session['json_feed']=url_from_id(cleaned_id)
    session['current_views']=[]
    parse_json()
    img_width = calculate_image_widths(len(session['current_views']))
    return render_template('index.html',
                           width=img_width,
                           height=img_width*(2/3),
                           views=session['current_views'])

@app.route('/')
def main():
    global session
    return new_view('view0')

if __name__=='__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0',port=port, debug=True)
