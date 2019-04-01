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
    # Create a Cloud Datastore client.
    datastore_client = datastore.Client()

    # Use the Cloud Datastore client to fetch information from Datastore about
    # each photo.
    query = datastore_client.query(kind='Faces')
    image_entities = list(query.fetch())

    # Return a Jinja2 HTML template and pass in image_entities as a parameter.
    return render_template('homepage.html', image_entities=image_entities)


@app.route('/upload_photo', methods=['GET', 'POST'])
def upload_photo():
    photo = request.files['file']

    # Create a Cloud Storage client.
    storage_client = storage.Client()

    # Get the bucket that the file will be uploaded to.
    bucket = storage_client.get_bucket(CLOUD_STORAGE_BUCKET)

    # Create a new blob and upload the file's content.
    blob = bucket.blob(photo.filename)
    blob.upload_from_string(
            photo.read(), content_type=photo.content_type)

    # Make the blob publicly viewable.
    blob.make_public()

    # Create a Cloud Vision client.
    vision_client = vision.ImageAnnotatorClient()

    # Use the Cloud Vision client to detect a face for our image.
    source_uri = 'gs://{}/{}'.format(CLOUD_STORAGE_BUCKET, blob.name)
    image = vision.types.Image(
        source=vision.types.ImageSource(gcs_image_uri=source_uri))
    faces = vision_client.face_detection(image).face_annotations

    # If a face is detected, save to Datastore the likelihood that the face
    # displays 'joy,' as determined by Google's Machine Learning algorithm.
    if len(faces) > 0:
        face = faces[0]

        # Convert the likelihood string.
        likelihoods = [
            'Unknown', 'Very Unlikely', 'Unlikely', 'Possible', 'Likely',
            'Very Likely']
        face_joy = likelihoods[face.joy_likelihood]
    else:
        face_joy = 'Unknown'

    # Create a Cloud Datastore client.
    datastore_client = datastore.Client()

    # Fetch the current date / time.
    current_datetime = datetime.now()

    # The kind for the new entity.
    kind = 'Faces'

    # The name/ID for the new entity.
    name = blob.name

    # Create the Cloud Datastore key for the new entity.
    key = datastore_client.key(kind, name)

    # Construct the new entity using the key. Set dictionary values for entity
    # keys blob_name, storage_public_url, timestamp, and joy.
    entity = datastore.Entity(key)
    entity['blob_name'] = blob.name
    entity['image_public_url'] = blob.public_url
    entity['timestamp'] = current_datetime
    entity['joy'] = face_joy

    # Save the new entity to Datastore.
    datastore_client.put(entity)

    # Redirect to the home page.
    return redirect('/')

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
        print(color.color.green,color.color.red,color.color.blue, color.pixel_fraction, color.color.alpha)
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
    if mountainsAmount == 0:
        mountainsAmount = (1 - (waterAmount + fieldsAmount + mountainsAmount + othersAmount))/3
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

def getFromDatastore(key):
    datastore_client = datastore.Client()
    return datastore_client.get(key)

def insertInDatastore():
    i = 0


@app.route('/compute', methods=['GET', 'POST'])
def compute():
    input = request.args.get('query')
    print(getFromDatastore(datastore_client.key("Location", input)))

    datastore_client.put(entity)
    mapImage = getImageFromlocation(input)
    searchResponses = getSearchResponses(input)
    imageProperties = getImageProperties(mapImage['binary'])

    return json.dumps({'imageProperties': imageProperties, 'searchResponses': searchResponses,"image":mapImage['base64']})


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
