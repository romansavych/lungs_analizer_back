import json
import os
import pickle

import flask
import pymongo
from flask_pymongo import PyMongo
import numpy as np
from scipy.io import wavfile

from fileHandler import getArrayOfValues, drawGraphByFile, drawGraphByArray
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error
from math import sqrt

from flask import Flask, request, render_template, Response
from flask_cors import CORS
from bson.objectid import ObjectId
app = Flask(__name__)
CORS(app)
from flask import current_app, g
# app.config["MONGO_URI"] = "mongodb+srv://admin:admin@cluster0.jpkesih.mongodb.net/?retryWrites=true&w=majority"
try:

    # mongo = pymongo.MongoClient("mongodb+srv://admin:admin@cluster0.jpkesih.mongodb.net/?retryWrites=true&w=majority")
    mongo = pymongo.MongoClient("mongodb+srv://admin:admin@cluster0.jpkesih.mongodb.net/?retryWrites=true&w=majority")
    mongo.server_info()
    db = mongo.company
    print(mongo.server_info())
except Exception as ex:
    print('connection error', ex)

@app.route("/" , methods=['POST'])
def getResult():
    default_value = '0'
    print(request)
    queryFile = request.files["file"]
    email = request.form["email"]
    gender = request.form["gender"]
    age = request.form["age"]
    arr = getArrayOfValues(queryFile)
    result = analizeLungs(arr)
    dbUsersResponse = db.users.insert_one(
        {
        'email': email,
        'gender': gender,
        'age': age
         })
    dbFilesResponse = db.files.insert_one(
        {
        'user_id':dbUsersResponse.inserted_id,
         'file'  :arr,
        'result':result
        }
    )

    dbResponse =  db.reports.insert_one(
        {'email': email,
        'result': result,
        'gender': gender,
        'age': age,
         'user_id':dbUsersResponse.inserted_id,
         'file_id':dbFilesResponse.inserted_id
         }
    )

    for attr in dir(dbResponse):
        print(attr)
    print('id: ' , dbResponse.inserted_id)
    return {"result":result}


@app.route("/all")
def all_reports():
    data = list(db.reports.find())
    for record in data:
        record["_id"] = str(record["_id"])
    return Response(
    response=json.dumps(data),
    status=200,
    mimetype="application/json"
    )

@app.route("/find_by_email" , methods=['GET', 'POST'])
def find_one_report():
    email = request.form["email"]
    data = list(db.reports.find({"email" : email}))
    print(data)
    for record in data:
        record["_id"] = str(record["_id"])
        record["user_id"] = str(record["user_id"])
        record["file_id"] = str(record["file_id"])
    return Response(
    response=json.dumps(data),
    status=200,
    mimetype="application/json"
    )

def getSingleArray(arr):
    newArr = []
    for x in arr:
        newArr.append(x[0])
    return newArr


def getMSEResult(val1, val2):
    if (len(val1) > len(val2)):
        val1 = val1[0:len(val2)]
    if (len(val2) > len(val1)):
        val2 = val2[0:len(val1)]
    return sqrt(mean_squared_error(val1 , val2))
    # return mean_absolute_percentage_error(np.float64(val1),np.float64(val2))

def analizeLungs(file):
    data = {
        'normal': [],
        'asthma':[],
        'pneumonia':[],
        'copd':[]
    }

    try:
        with open('./preanalized.txt', 'rb') as f:
            data = pickle.loads(f.read())
    except FileNotFoundError:
        for filename in os.listdir('./db'):
            f = os.path.join('./db', filename)
            print(filename)
            # checking if it is a file
            if os.path.isfile(f):
                arr = getArrayOfValues(f)
                for class_ in data.keys():
                    if class_ in f.lower():
                        data[class_].append(arr)
        with open('./preanalized.txt', 'wb') as f:
            f.write(pickle.dumps(data))


    # drawGraphByFile('lungs', './test/lungs.wav' , 'red')
    coefs = []
    all_compare_results = []

    for class_, val in data.items():
        sum_ = []
        for arr in val:
            sum_.append(getMSEResult(file, arr))
            # drawGraphByArray(arr, 'red', class_)
            # if(len(sum_) != 0):
        coefs.append((class_, min(sum_)))


    min_coefs = min(coefs, key=lambda x: x[1])
    # print(min_coefs)
    # print('result' , min_coefs[0])
    return  min_coefs[0]

file = getArrayOfValues('./test/lung test 2.wav')
# analizeLungs(file)
if __name__ == '__main__':


    app.run(debug=True)
