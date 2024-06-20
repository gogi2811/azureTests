from flask import Flask, request, jsonify
from flask_swagger_ui import get_swaggerui_blueprint
import requests
import google
import cv2
import google.generativeai as genai
import PIL.Image
import numpy
import pandas as pd
import base64
from PIL import Image
from io import BytesIO
from pyzbar.pyzbar import decode 
GOOGLE_API_KEY = "AIzaSyC81hsbRz79lDZ9Y-4gMrzz_cDhBYh-uTU"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')
prompt = """Give the name of %s after 'Food:' and specify all 'Raw Material:', Ingredients -> Components (contains materials that make up the raw mmaterials or displays 'None') separately under 'Ingredients:' in new lines. Start each list with commas. In the next line, state 'Hazards:', followed by the health hazards this food item can cause. Then, in the next line, state 'Allergies:', followed by all the allergies this food item can cause. Ensure there are no empty lines or extra white spaces.

*Example:*

Food: <Food Name>
Ingredients:
Raw Material: <raw material, name all separately, and include spices, flavors, oils, colors, if raw materials consist of more components that are used to make it, display theses components it inside of brackets after the raw material, else DISPLAY (None) after the raw material> eg: Chocolate (mill, cocoa), Salt (None), Sunflower Oil (None)
Hazards: <health hazards, name diseases or any illness that might be caused due consuming this product normally and by over eating it,  names of diseases/illnesses only>
Allergies: <allergies caused from any of the raw materials, names only>


NOTE: THERE HAS TO BE EITHER 'NONE' OR COMPONENTS THAT MAKE UP THE RAW MATERIALS IN A BRACKET AFTER ANY RAW MATERIAL NAME
eg <raw material name> (componatents used to make it), <raw material name> (NONE) 
"""
def display(response):
    lists = response.split('\n')
    biggest = 0
    for i,list in enumerate(lists):
        st = list.find(':')
        lists[i] = [list[0:st],list[st+1:]]
        if lists[i][0] == '':
            lists.pop(i)
            continue
        li = lists[i][1]
        split = True
        pos = 0
        temp = []
        for j,let in enumerate(li):
            if let == '(': split = False
            elif let == ')': split = True
            if split and let == ',' or j == len(li)-1:
                t = li[pos:j+1]
                if t[-1] == ',':temp.append(t[0:-1].strip())
                else: temp.append(t.strip())
                pos = j+1
        if len(temp) > biggest: biggest = len(temp)
        lists[i][1] = temp
    
    print("INITIATING RAW MATERIAL SEPERATION")
    dic = dict(lists)
    if len(dic["Raw Material"]) <= 3: raise(AttributeError)
    for i, raw in enumerate(dic["Raw Material"]):
        if raw.find('(') != -1:
            st = raw.find('(')
            dic['Raw Material'][i] = [raw[0:st],raw[st+1:-1].split(',')]
        else:
            dic['Raw Material'][i] = [raw,['None']]
        print(dic['Raw Material'][i])
    return dic
    
def text(TEXT):
    try: 
        response = model.generate_content(prompt % TEXT)
        res = response.text.replace('*',"").replace('#','')
        print(res)
        return display(res)
    except google.api_core.exceptions.InternalServerError: text(TEXT)
    except AttributeError: text(TEXT)
    except IndexError: text(TEXT)
def img(IMAGE):
    try:
        response = model.generate_content([prompt % 'this food item', IMAGE], stream=True)
        response.resolve()
        res = response.text.replace('*',"")
        print(res)
        print('IMAGE DONE PROCESSING')
        dic = display(res)
        return  dic
    except google.api_core.exceptions.InternalServerError: img(IMAGE)
    except AttributeError: img(IMAGE)
    except IndexError: img(IMAGE)
    
def get_food_name_openfoodfacts(barcode):
    api_url = f'https://world.openfoodfacts.org/api/v0/product/{barcode}.json'
    
    response = requests.get(api_url)
    
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 1:
            product = data['product']
            name = product.get('product_name')
            company = product.get('brand_owner')
            print('From OpenFoodFacts:',name)
            print('From Company:',company)
            if company != None:
                t = name,company
            else: t = name
            return text(str(t))
        else: return "Product Not Found"
    
def BarcodeReader(IMAGE): 
    img = numpy.array(IMAGE)
    detectedBarcodes = decode(IMAGE) 
       
    if not detectedBarcodes: 
        print("Barcode Not Detected") 
    else:
        for barcode in detectedBarcodes:   
            (x, y, w, h) = barcode.rect 
            
            cv2.rectangle(img, (x-10, y-10), 
                          (x + w+10, y + h+10),  
                          (255, 0, 0), 2) 
              
            if barcode.data!="": 
                print('Barcode Reader:',barcode.data)
                return get_food_name_openfoodfacts(barcode.data)

app = Flask(__name__)

# @app.route("/")
# def home():
#     return "Hone"

# @app.route("/get-user/<user_id>")
# def get_user(user_id):
#     user_data = {
#         "user_id": user_id,
#         "name": 'Sahir'
#     }
#     extra = request.args.get("extra")
#     if extra:
#         user_data["extra"] = extra
#     return jsonify(user_data), 200

SWAGGER_URL = ''  # URL for exposing Swagger UI (without trailing '/')
#API_URL = 'http://petstore.swagger.io/v2/swagger.json'  # Our API url (can of course be a local resource)
API_URL = '/static/swagger.json'

# Call factory function to create our blueprint
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
    API_URL,
    config={  # Swagger UI config overrides
        'app_name': "Test application"
    },
    # oauth_config={  # OAuth config. See https://github.com/swagger-api/swagger-ui#oauth2-configuration .
    #    'clientId': "your-client-id",
    #    'clientSecret': "your-client-secret-if-required",
    #    'realm': "your-realms",
    #    'appName': "your-app-name",
    #    'scopeSeparator': " ",
    #    'additionalQueryStringParams': {'test': "hello"}
    # }
)

app.register_blueprint(swaggerui_blueprint)

@app.route("/food-name",methods=["POST"])
def using_name():
    if request.method == "POST":
        data = request.get_json()
        data = text(data['foodItem'])
        return jsonify(data), 200
    
@app.route("/barcode",methods=["POST"])
def using_barcode():
    if request.method == "POST":
        data = request.get_json()
        print(data)
        data = get_food_name_openfoodfacts(data['barcode'])
        return jsonify(data), 200
    
@app.route("/barcode-image",methods=["POST"])
def using_barcodeImage():
    if request.method == "POST":
        data = request.get_json()
        im = Image.open(BytesIO(base64.b64decode(data['encodedImage'])))
        return jsonify(BarcodeReader(im)), 200
    
@app.route("/food-image",methods=["POST"])
def using_foodImage():
    if request.method == "POST":
        data = request.get_json()
        im = Image.open(BytesIO(base64.b64decode(data['encodedImage'])))
        dic = img(im)
        return jsonify(dic), 200

if __name__ == "__main__":
    app.run(debug=True)