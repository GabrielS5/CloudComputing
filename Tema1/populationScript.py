import requests, threading, time

def request():
    startTime = time.time()
    url = "http://localhost:8000/compute?location=Romania"
    response = requests.get(url)

for i in range(0,10):
    slv = []
    for j in range(0,10):
        sl = threading.Thread(target=request)
        slv.append(sl)
        sl.start()
    
    for sl in slv:
        sl.join()