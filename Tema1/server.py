from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
import cgi, json, codecs, requests, time, threading
from socketserver import ThreadingMixIn


configuration = json.loads(open("configuration.json").read())

def getLog():
    response = requests.get('http://localhost:9000')
    return response.json()

def logInfo(info):
    requests.post('http://localhost:9000', data = json.dumps(info))

def getQueryParams(path):
    query = path.split("?")[-1]
    keys = query.split("&")
    result = dict()
    for key in keys:
        items = key.split("=")
        result[items[0]] = items[1]
    return result

def getLatLongFromLocation(location):
    startTime = time.time()
    url = "https://api.opencagedata.com/geocode/v1/json?q=" + location + "&key=" + configuration["OpenCageKey"] + "&language=ro&pretty=1"
    response = requests.get(url)
    if response.ok:
        endTime = time.time()
        logInfo({"API": "OpenCageData-Geocode","RequestMethod": "GET", "Request": url, "Response": response.status_code, "Latency": (endTime - startTime)})
        return {"response": response, "result": response.json()['results'][0]["geometry"]}
    else:
        endTime = time.time()
        logInfo({"API": "OpenCageData-Geocode","RequestMethod": "GET", "Request": url, "Response": response.status_code, "Latency": (endTime - startTime)})
        return False

def getImageFromLatLong(latLong):
    startTime = time.time()
    url = 'https://image.maps.api.here.com/mia/1.6/mapview?app_id=' + configuration['MapsHereKey']["Id"] + "&app_code=" + configuration['MapsHereKey']["Code"] + '&lat=' + str(latLong['lat']) + '&lon=' + str(latLong['lng']) + '&vt=0&z=6&w=700&h=700&t=5'
    response = requests.get(url)
    if response.ok:
        image = codecs.encode(codecs.decode(response.content.hex(), 'hex'), 'base64').decode()
        if image[-1] == '\n':
            image = image[:-1]
        endTime = time.time()
        logInfo({"API": "ImageMapsApiHere","RequestMethod": "GET", "Request": url, "Response": response.status_code, "Latency": (endTime - startTime)})
        return {"response": response, "result": image }
    else:
        endTime = time.time()
        logInfo({"API": "ImageMapsApiHere","RequestMethod": "GET", "Request": url, "Response": response.status_code, "Latency": (endTime - startTime)})
        return False
        
def getDataFromLocation(location):
    startTime = time.time()
    url = 'http://api.worldbank.org/v2/country?format=json&per_page=400'
    response = requests.get(url)
    countryes = response.json()[1]
    for country in countryes:
        if country['name'] == location:
            result = dict()
            result['name'] = country['name']
            result['region'] = country['region']['value']
            result['incomeLevel'] = country['incomeLevel']['value']
            result['capitalCity'] = country['capitalCity']
            endTime = time.time()
            logInfo({"API": "WorldBank","RequestMethod": "GET", "Request": url, "Response": response.status_code, "Latency": (endTime - startTime)})
            return {"response": response, "result": result}
    else:
        endTime = time.time()
        logInfo({"API": "WorldBank","RequestMethod": "GET", "Request": url, "Response": 404, "Latency": (endTime - startTime)})
        return {"response": response, "result": "Not found"}

def scanImageForViruses(image):
    startTime = time.time()
    params = {'apikey': configuration['VirusTotalKey']}
    files = {'file': ('image.jpg', image)}
    url = 'https://www.virustotal.com/vtapi/v2/file/scan'
    response = requests.post(url, files=files, params=params)
    if response.ok:
        endTime = time.time()
        logInfo({"API": "VirusTotalApi","RequestMethod": "POST", "Request": url, "Response": response.status_code, "Latency": (endTime - startTime)})
        return {"response": response, "result": response.json()["permalink"]}
    else:
        endTime = time.time()
        logInfo({"API": "VirusTotalApi","RequestMethod": "POST", "Request": url, "Response": response.status_code, "Latency": (endTime - startTime)})
        return False

class RestHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        startTime = time.time()
        if "metrics" in self.path:
            log = getLog()
            myApiSum = 0
            myApiCount = 0
            worldBankApiSum = 0
            worldBankApiCount = 0
            imageMapsApiSum = 0
            imageMapsApiCount = 0
            openCageApiSum = 0
            openCageApiCount = 0
            virusTotalApiSum = 0
            virusTotalApiCount = 0
            successfullCalss = 0

            for l in log:
                if l['API'] == "My Api":
                    myApiSum += l['Latency']
                    myApiCount += 1
                if l['API'] == "WorldBank":
                    worldBankApiSum += l['Latency']
                    worldBankApiCount += 1
                if l['API'] == "ImageMapsApiHere":
                    imageMapsApiSum += l['Latency']
                    imageMapsApiCount += 1
                if l['API'] == "OpenCageData-Geocode":
                    openCageApiSum += l['Latency']
                    openCageApiCount += 1
                if l['API'] == "VirusTotalApi":
                    virusTotalApiSum += l['Latency']
                    virusTotalApiCount += 1
                if l["Response"] == 200:
                    successfullCalss += 1

            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps({"SuccessRate": successfullCalss / len(log), "virusTotalApiAverageLatency":(virusTotalApiSum/virusTotalApiCount) ,"myApiAverageLatency": (myApiSum/myApiCount), "worldBankAverageLatency": (worldBankApiSum/worldBankApiCount),"OpenCageAverageLatency": (openCageApiSum/openCageApiCount), "imageMapsAverageLatency": (imageMapsApiSum/imageMapsApiCount), "logs": log}).encode())
            endTime = time.time()
        elif "compute" in self.path:
            queryParams = getQueryParams(self.path)
            latLong = getLatLongFromLocation(queryParams["location"])
            countryData = getDataFromLocation(queryParams["location"])
            image = getImageFromLatLong(latLong['result'])
            scan = scanImageForViruses(image['response'].content)  
            computatution = dict()
            computatution['location'] = latLong['result']
            computatution['details'] = countryData['result']
            computatution['image'] = image['result']  
            computatution['scanUrl'] = scan['result']      
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps(computatution).encode())
            endTime = time.time()
            logInfo({"API": "My Api","Request Method": "GET", "Request": self.path, "Response": 200, "Latency": (endTime - startTime)})
        elif "mPage" in self.path:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(open("./metrics.html").read().encode())
            endTime = time.time()
        elif "requests" in self.path:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(open("./requests.html").read().encode())
            endTime = time.time()
        else:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(open("./index.html").read().encode())
            endTime = time.time()
        return

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass

httpd = ThreadedHTTPServer(('0.0.0.0', 8000), RestHTTPRequestHandler)
httpd.serve_forever()