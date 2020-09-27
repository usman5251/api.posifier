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
import datetime

application = Flask(__name__)

def ConvertDataFromUrl(url, process):
    if process == 'report':
        conn = sqlite3.connect('records.db')
        for row in conn.execute(f'SELECT * FROM offsets WHERE url = "{url}"'):
            url, offset, status = row
            offset = row[1]
            status = row[2]
            return f'url is {url}, offset is {offset} and status is {status}'
        else:
            return 'No record found for the URL'
        conn.close()
    if process == 'reset':
        conn = sqlite3.connect('records.db')
        conn.execute(f"UPDATE offsets SET offset = 0 WHERE url = '{url}'")
        conn.execute(f"UPDATE offsets SET status = 'get_all' WHERE url = '{url}'")
        conn.commit()
        conn.close()
        return 'Record reset successfull'
    else:
    #Connect to database:
        limit = 50000
        conn = sqlite3.connect('records.db')
        for row in conn.execute(f'SELECT * FROM offsets WHERE url = "{url}"'):
            url, offset, status = row
            offset = row[1]
            status = row[2]
            print(status)
            print('Previous record found for this dataset')
            print(f'Dataset Url = {row[0]}')
            print(f'Starting offset = {row[1]}')
            break
        else:
            offset = 0
            status = 'get_all'
            print(f"Record not found for {url} creating new record...")
            conn.execute(f'INSERT INTO offsets(url, offset, status) VALUES ("{url}", {offset}, "{status}");')
            conn.commit()
            for row1 in conn.execute(f'SELECT * FROM offsets WHERE url = "{url}"'):
                url, offset, status = row1
                print(row1[0], row1[1])
                print('Record successfully created')
                break
            else:
                print('There was a problem when creating new record...')

        if status == 'get_all':
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
                print(len(data))
                offset = offset + len(data)
                data = pd.DataFrame(data[1:], columns=data[0])
                result = data.to_json(orient="records")
                parsed = json.loads(result)
                a = json.dumps(parsed, indent=4)
                if len(data) >= 50000:
                    print('a')
                    conn.execute(f"UPDATE offsets SET offset = {offset} WHERE url = '{url}'")
                    conn.commit()
                    conn.close()
                else:
                    print(url)
                    conn.execute(f"UPDATE offsets SET status = 'get_latest' WHERE url = '{url}'")
                    conn.commit()
                    conn.close()
                return a

        if status == 'get_latest':
            dt = datetime.datetime.utcnow()
            querystring = {"$$app_token" : "HOJFA4YDCOmlZBMOSjbJtHxfo", "$offset" : '0', "$where" : f":updated_at>={dt.year}-{dt.month}-{dt.day-1}"}
            print(querystring)
            url = f"{url}?$$app_token=HOJFA4YDCOmlZBMOSjbJtHxfo&$where=:updated_at>='{dt.year}-{dt.month}-{dt.day}'"
            payload = ""
            response = requests.request("GET",url , data=payload)
            print(response.url)
            r = response.text.splitlines()
            if r:
                print('Found new data')
                print('modifying=- data')
                # print(response.text)
                reader = csv.reader(r)
                data = list(reader)
                print(len(data))
                offset = offset + len(data)
                data = pd.DataFrame(data[1:], columns=data[0])
                result = data.to_json(orient="records")
                parsed = json.loads(result)
                a = json.dumps(parsed, indent=4)
                return a
            else:
                return ''



@application.route('/')
def convert():
    url = request.args.get('url')
    process = request.args.get('process')
    if url and process:
        response = application.response_class(
        response=ConvertDataFromUrl(url, process),
        status=200,
        mimetype='application/json'
    )
        header = response.headers
        header['Access-Control-Allow-Origin'] = '*'
        return response
    elif url:
        response = application.response_class(
        response=ConvertDataFromUrl(url, process),
        status=200,
        mimetype='application/json'
    )
        header = response.headers
        header['Access-Control-Allow-Origin'] = '*'
        return response
    else:
        return ('URL parameter is missing')
    

if __name__ == "__main__":
    application.run(host="0.0.0.0", port=80)



    













