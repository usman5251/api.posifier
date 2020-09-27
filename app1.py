from flask import Flask, render_template, request, redirect, url_for
import os
import datetime
import requests
import time
import json
import sqlite3
import geodaisy.converters as convert
from shapely.wkt import dumps, loads
from shapely.geometry import mapping, shape
from shapely.geometry import LineString
import mylib
import csv
import pandas as pd
import io
from flask import jsonify

application = Flask(__name__)

def ConvertDataFromUrl(url, limit):
    try:
        querystring = {"$$app_token" : "HOJFA4YDCOmlZBMOSjbJtHxfo" , "$limit" : f'{limit}', "$offset" : '0'}
        payload = ""
        response = requests.request("GET", url, data=payload, params=querystring)
        r = response.text.splitlines()
        if r:
            print('Found new data')
            print('modifying data')
            # print(response.text)
            reader = csv.reader(r)
            data = list(reader)
            data = pd.DataFrame(data[1:], columns=data[0])
            result = data.to_json(orient="records")
            parsed = json.loads(result)
            a = json.dumps(parsed, indent=4) 
            return a

        else:
            return '--NO-DATA--'
    except Exception as e:
        return e

@application.route('/')
def convert():
    url = request.args.get('url')
    limit = request.args.get('limit')
    if url and limit:
        response = application.response_class(
        response=ConvertDataFromUrl(url, limit),
        status=200,
        mimetype='application/json'
    )
        header = response.headers
        header['Access-Control-Allow-Origin'] = '*'
        return response
    else:
        return ('URL and LIMIT parameter is missing')

if __name__ == "__main__":
    application.run(host="0.0.0.0", port=80)



    













