import base64, cv2, numpy as np, io, time, pickle
from dis import disco

from PIL import Image
from flask import Flask, request
from flask_cors import CORS
from pymongo import MongoClient

def getColor(data, image):
    morph = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))

    mask = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    mask = cv2.threshold(mask, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    mask = cv2.erode(mask, morph)

    contours = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) == 2:
        contours = contours[0]
    else:
        contours = contours[1]

    image = Image.fromarray(image)
    
    selected = False
    
    background = {
        "R": 255,
        "G": 255,
        "B": 255
    }

    foreground = {
        "R": 0,
        "G": 0,
        "B": 0
    }

    backcolor = image.getpixel((data['pos'][0]['x'], data['pos'][0]['y']))

    background['B'] = backcolor[0]
    background['G'] = backcolor[1]
    background['R'] = backcolor[2]

    backsum = background['B'] + background['G'] + background['R']

    for c in contours:
        x = int(c[0][0][0])
        y = int(c[0][0][1])

        if x > data['pos'][0]['x'] and x < data['pos'][2]['x'] and y > data['pos'][0]['y'] and y < data['pos'][2]['y']:
            frontcolor = image.getpixel((x, y))

            foreground['B'] = frontcolor[0]
            foreground['G'] = frontcolor[1]
            foreground['R'] = frontcolor[2]

            selected = True

            break

    frontsum = foreground['B'] + foreground['G'] + foreground['R']

    if selected:
        if abs((frontsum) - backsum) < 150:
            foreground = {
                "R": 255,
                "G": 255,
                "B": 255
            }
    else:
        if backsum < 380:
            foreground = {
                "R": 255,
                "G": 255,
                "B": 255
            }
    
    return {
        "background": background,
        "foreground": foreground,
    }

app = Flask(__name__)
CORS(app)

@app.route('/trangers/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'GET':
        return 'TRANGERS UPLOAD API: 200 OK'

    if request.method == 'POST':
        id = request.args.get('id')
        time = request.args.get('time')
        obj = request.get_json(silent=True)
        
        try :
            with open('./trangers/' + id + '_' + time + '.pkl', 'wb') as f:
                pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

            return {
                "code": "SUCCESS",
                "data": 'download?id=' + id + '&time=' + time
            }

        except Exception as e:
            return {
                "code": "FAILED"
            }

@app.route('/trangers/download', methods=['GET'])
def download():
    if request.method == 'GET':
        id = request.args.get('id')
        time = request.args.get('time')

        with open('./trangers/' + id + '_' + time + '.pkl', 'rb') as f:
            return pickle.load(f)

@app.route('/trangers/getkey', methods=['GET', 'POST'])
def getkey():
    if request.method == 'GET':
        return 'TRANGERS VISION API: 200 OK'

    if request.method == 'POST':
        return "AIzaSyAVm91itY_MHHDIe8GP-Y1rjZiLzfiSRz8"

@app.route('/trangers/getcolor', methods=['GET', 'POST'])
def getcolor():
    if request.method == 'GET':
        return 'TRANGERS COLOR API: 200 OK'

    if request.method == 'POST':
        vision = request.get_json(silent=True)

        imageData = base64.b64decode(vision['image'])
        imageDataBytesIO = io.BytesIO(imageData)

        image = Image.open(imageDataBytesIO)

        result = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2RGB)

        colorInfo = []

        for data in vision['data']:
            colorInfo.append(getColor(data, result))

        return { 
            "data": colorInfo,
        }

@app.route('/trangers', methods=['GET', 'POST'])
def trangers():
    if request.method == 'GET':
        return 'TRANGERS COLOR API: 200 OK'

    if request.method == 'POST':
        vision = request.get_json(silent=True)

        imageData = base64.b64decode(vision['image'])
        imageDataBytesIO = io.BytesIO(imageData)

        image = Image.open(imageDataBytesIO)

        result = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2RGB)

        colorInfo = []

        for data in vision['data']:
            colorInfo.append(getColor(data, result))

        return { 
            "data": colorInfo,
        }

@app.route('/trangers/validphone', methods=['GET', 'POST'])
def validphone():
    if request.method == 'GET':
        return 'TRANGERS USER API: 200 OK'

    if request.method == 'POST':
        client = MongoClient('mongodb://localhost:27017/')
        
        reactdb = client.reactdb
        trangers = reactdb.trangers

        data = request.get_json(silent=True)
        uid = trangers.find_one({"phone": data['phone']})
        
        client.close()

        if uid == None:
            return {
                "status": "SUCCESS"
            }
        else:
            return {
                "status": "FAILED"
            }

@app.route('/trangers/getuser', methods=['GET', 'POST'])
def getuser():
    if request.method == 'GET':
        return 'TRANGERS USER API: 200 OK'

    if request.method == 'POST':
        client = MongoClient('mongodb://localhost:27017/')
        
        reactdb = client.reactdb
        trangers = reactdb.trangers

        data = request.get_json(silent=True)
        uid = trangers.find_one({"_id": data['id']})
        
        client.close()

        if uid == None:
            return {
                "status": "FAILED"
            }
        else:
            return {
                "rank": uid['servicerank'],
                "usage": uid['usage'],
                "limit": uid['limit'],
                "credit": uid['credit'],
                "status": "SUCCESS",
                "available": uid['available'],
                "refcode": uid['refcode']
            }

# @app.route('/trangers/getrank', methods=['GET', 'POST'])
# def getrank():
#     if request.method == 'GET':
#         return 'TRANGERS RANK API: 200 OK'

#     if request.method == 'POST':
#         client = MongoClient('mongodb://localhost:27017/')

#         reactdb = client.reactdb
#         trangers = reactdb.trangers

#         data = request.get_json(silent = True)
#         uid = trangers.find_one({"_id": data['id']})

#         client.close()

#         if uid == None:
#             return "0"
#         else:
#             return str(uid['servicerank'])

# @app.route('/trangers/getlimit', methods=['GET', 'POST'])
# def getlimit():
#     if request.method == 'GET':
#         return 'TRANGERS LIMIT API: 200 OK'

#     if request.method == 'POST':
#         client = MongoClient('mongodb://localhost:27017/')

#         reactdb = client.reactdb
#         trangers = reactdb.trangers

#         data = request.get_json(silent = True)
#         uid = trangers.find_one({"_id": data['id']})

#         client.close()

#         if uid == None:
#             return "0"
#         else:
#             return str(uid['limit'])

# @app.route('/trangers/getusage', methods=['GET', 'POST'])
# def getusage():
#     if request.method == 'GET':
#         return 'TRANGERS USAGE API: 200 OK'

#     if request.method == 'POST':
#         client = MongoClient('mongodb://localhost:27017/')
        
#         reactdb = client.reactdb
#         trangers = reactdb.trangers

#         data = request.get_json(silent = True)
#         uid = trangers.find_one({"_id": data['id']})

#         client.close()

#         if uid == None:
#             return "0"
#         else:
#             return str(uid['usage'])

@app.route('/trangers/setavailable', methods=['GET', 'POST'])
def setavailable():
    if request.method == 'GET':
        return 'TRANGERS AVAILABLE API: 200 OK'

    if request.method == 'POST':
        client = MongoClient('mongodb://localhost:27017/')
        
        reactdb = client.reactdb
        trangers = reactdb.trangers

        data = request.get_json(silent = True)
        trangers.update_one({"_id": data['id']}, {"$set": {"available": data['available']}})

        client.close()
        
        return str(data['available'])

@app.route('/trangers/setusage', methods=['GET', 'POST'])
def setusage():
    if request.method == 'GET':
        return 'TRANGERS USAGE API: 200 OK'

    if request.method == 'POST':
        client = MongoClient('mongodb://localhost:27017/')
        
        reactdb = client.reactdb
        trangers = reactdb.trangers

        data = request.get_json(silent = True)
        trangers.update_one({"_id": data['id']}, {"$set": {"usage": data['usage']}})

        client.close()
        
        return str(data['usage'])

@app.route('/trangers/setcredit', methods=['GET', 'POST'])
def setcredit():
    if request.method == 'GET':
        return 'TRANGERS CREDIT API: 200 OK'

    if request.method == 'POST':
        client = MongoClient('mongodb://localhost:27017/')
        
        reactdb = client.reactdb
        trangers = reactdb.trangers

        data = request.get_json(silent = True)
        trangers.update_one({"_id": data['id']}, {"$set": {"credit": data['credit']}})

        client.close()
        
        return str(data['credit'])

@app.route('/trangers/changepassword', methods=['GET', 'POST'])
def changepassword():
    if request.method == 'GET':
        return 'TRANGERS PASSWORD API: 200 OK'

    if request.method == 'POST':
        client = MongoClient('mongodb://localhost:27017/')
        
        reactdb = client.reactdb
        trangers = reactdb.trangers
        
        data = request.get_json(silent=True)
        uid = trangers.find_one({"_id": data['id']})
        
        if uid == None:
            client.close()
            
            return "FAILED"
        else:
            if uid['password'] == data['pw']:
                client.close()

                trangers.update_one({"_id": data['id']}, {"$set": {"password": data['newpw']}})

                return "SUCCESS"
            else:
                client.close()

                return "FAILED"

@app.route('/trangers/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'GET':
        return 'TRANGERS SIGN API: 200 OK'

    if request.method == 'POST':
        client_ip = request.remote_addr

        print(client_ip)

        client = MongoClient('mongodb://localhost:27017/')
        
        reactdb = client.reactdb
        trangers = reactdb.trangers

        data = request.get_json(silent=True)
        uid = trangers.find_one({"_id": data['id']})
        
        client.close()

        if uid == None:
            return "FAILED"
        else:
            if uid['password'] == data['pw']:
                return "SUCCESS"
            else:
                return "FAILED"

@app.route('/trangers/signcheck', methods=['GET', 'POST'])
def signcheck():
    if request.method == 'GET':
        return 'TRANGERS SIGN API: 200 OK'

    if request.method == 'POST':
        client = MongoClient('mongodb://localhost:27017/')
        
        reactdb = client.reactdb
        trangers = reactdb.trangers

        data = request.get_json(silent=True)
        uid = trangers.find_one({"_id": data['id']})

        client.close()

        if uid != None:
            return 'FAILED'
        else:
            return 'SUCCESS'

@app.route('/trangers/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return 'TRANGERS SIGN API: 200 OK'

    if request.method == 'POST':
        client = MongoClient('mongodb://localhost:27017/')
        
        reactdb = client.reactdb
        trangers = reactdb.trangers

        data = request.get_json(silent=True)
        uid = trangers.find_one({"_id": data['id']})
        
        if uid != None:
            return 'FAILED'

        pow = time.time()
        now = time.strftime('%Y-%m-%d', time.localtime(pow))

        credit = 0

        if len(data['refcode']) > 0:
            ref = trangers.find_one({"_id": data['refcode']})

            if ref != None:
                credit = 5000

                # trangers.update_one({"_id": ref['_id']}, {"$set": {"credit": ref['credit'] + 5000}})

        database = {
            "_id": data['id'],

            "password": data['pw'],

            "servicetype": data['servicetype'],
            "servicerank": data['servicerank'],

            "usage": data['usage'],
            "limit": data['limit'],
            "available": 1,

            "name": data['name'],
            "email": data['email'],
            "phone": data['phone'],

            "create": now,
            
            "refcode": data['refcode'],
            "credit": credit
        }

        trangers.insert_one(database)

        client.close()

        return 'SUCCESS'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)