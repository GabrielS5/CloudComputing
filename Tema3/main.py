# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from datetime import datetime
import logging
import os, requests,cgi, json, codecs,math
import base64

from flask import Flask, redirect, render_template, request

from google.cloud import datastore
from google.cloud import storage
from google.cloud import vision


CLOUD_STORAGE_BUCKET = os.environ.get('CLOUD_STORAGE_BUCKET')


app = Flask(__name__)


@app.route('/')
def homepage():
    return render_template('homepage.html')

def getPlaceDetails(location):
    url = 'https://maps.googleapis.com/maps/api/place/findplacefromtext/json?key=AIzaSyCNQX5-4_hPDpluC7j-EZK13Oixn_47DpM&input=' + location + '&inputtype=textquery'
    response = requests.get(url)
    if response.ok:
        candidates = response.json()['candidates']
        if len(candidates) == 0:
            return False
        placeId = candidates[0]['place_id']
        url = 'https://maps.googleapis.com/maps/api/place/details/json?key=AIzaSyCNQX5-4_hPDpluC7j-EZK13Oixn_47DpM&placeid=' + placeId
        response = requests.get(url)
        if response.ok:
            result = response.json()['result']
            return {'latitude': result['geometry']['location']['lat'], 'longitude': result['geometry']['location']['lng'], 'shortName': result['address_components'][0]['short_name'],'longName': result['address_components'][0]['long_name'], 'type': result['types'][0]}
        else:
            return False
    else:
        return False

def getImageProperties(content):
    client = vision.ImageAnnotatorClient()
    image = vision.types.Image(content=content)

    response = client.image_properties(image=image)
    props = response.image_properties_annotation

    waterAmount = 0
    fieldsAmount = 0
    mountainsAmount = 0
    othersAmount = 0

    for color in props.dominant_colors.colors:
        if 200 <= color.color.green <= 222 and 169 <= color.color.red <= 189 and 230 <= color.color.blue :
            waterAmount += color.pixel_fraction
        elif 224 <= color.color.green <= 244 and 200 <= color.color.red <= 220 and 190 <= color.color.blue <= 210:
            mountainsAmount += color.pixel_fraction
        elif (236 <= color.color.green <= 246 and 234 <= color.color.red <= 244 and 225 <= color.color.blue <= 235) or (225 <= color.color.green <= 238 and 210 <= color.color.red <= 240 and 205 <= color.color.blue <= 230):
            fieldsAmount += color.pixel_fraction
        else:
            othersAmount += color.pixel_fraction

    if waterAmount == 0:
        waterAmount = 1 - (waterAmount + fieldsAmount + mountainsAmount + othersAmount)
    elif mountainsAmount == 0:
        mountainsAmount = (1 - (waterAmount + fieldsAmount + mountainsAmount + othersAmount))/2
    elif fieldsAmount == 0:
        fieldsAmount = (1 - (waterAmount + fieldsAmount + mountainsAmount + othersAmount))/1.5
    else:
        othersAmount += 1 - (waterAmount + fieldsAmount + mountainsAmount + othersAmount)

    return {'water': round(waterAmount* 100,2), 'fields': round(fieldsAmount* 100,2), 'mountains': round(mountainsAmount * 100,2), 'others': round(othersAmount * 100,2)}

def getImageFromlocation(location):
    url = 'https://maps.googleapis.com/maps/api/staticmap?center=' + location + '&size=800x800&maptype=roadmap&scale=2&key=AIzaSyCNQX5-4_hPDpluC7j-EZK13Oixn_47DpM'
    response = requests.get(url)
    if response.ok:
        image = base64.b64encode(response.content).decode()
        return {'base64': image, 'binary': response.content}
    else:
        return False

def getSearchResponses(query):
    url = 'https://www.googleapis.com/customsearch/v1?q=' + query + '&cx=013429757699244883815:0kpxacrknmm&key=AIzaSyCNQX5-4_hPDpluC7j-EZK13Oixn_47DpM'
    response = requests.get(url)
    if response.ok:
        result = []
        for item in response.json()['items']:
            result.append({'title': item['title'], 'link': item['link']})
        return result
    else:
        return False

def getFromDatastore(name):
    datastore_client = datastore.Client()
    query = datastore_client.query(kind='Location')
    query.add_filter('name', '=', name)
    result = list(query.fetch())

    if result == []:
        return False
    
    result = result[0]

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(CLOUD_STORAGE_BUCKET)
    blob = bucket.get_blob(result['image_blob'])
    return  {'name': result['name'], 'imageProperties': result['imageProperties'], 'searchResponses': result['searchResponses'],"image":blob.download_as_string().decode(), "placeDetails": result['placeDetails']}

def insertInDatastore(item):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(CLOUD_STORAGE_BUCKET)

    blob = bucket.blob(item['name'] + '-blob')
    blob.upload_from_string(item['image'])
    blob.make_public()
    datastore_client = datastore.Client()
    kind = 'Location'
    name = item['name']
    key = datastore_client.key(kind, name)
    entity = datastore.Entity(key)
    entity['name'] = item['name']
    entity['image_blob'] = blob.name
    entity['imageProperties'] = item['imageProperties']
    entity['searchResponses'] = item['searchResponses']
    entity['placeDetails'] = item['placeDetails']
    datastore_client.put(entity)


@app.route('/compute', methods=['GET', 'POST'])
def compute():
    input = request.args.get('query')
    databaseItem = getFromDatastore(input)
    if not databaseItem == False:
        return json.dumps(databaseItem)

    placeDetails = getPlaceDetails(input)
    mapImage = getImageFromlocation(input)
    searchResponses = getSearchResponses(input)
    imageProperties = getImageProperties(mapImage['binary'])
    result = {'name': input, 'imageProperties': imageProperties, 'searchResponses': searchResponses,"image":mapImage['base64'], 'placeDetails': placeDetails}
    insertInDatastore(result)
    return json.dumps(result)


@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
