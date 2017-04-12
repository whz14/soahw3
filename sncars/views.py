from django.shortcuts import render
from models import IMG
import httplib
import urllib
import json
import urllib2
from django.http.response import HttpResponseRedirect, JsonResponse

# Create your views here.

face_headers = {
    # Request headers
    'Content-Type': 'application/json',
    'Ocp-Apim-Subscription-Key': '0530ebe8880f4eb493579a6481341c69',
}


params = urllib.urlencode({
    # Request parameters
    'returnFaceId': 'true',
    'returnFaceLandmarks': 'false',
    'returnFaceAttributes': 'age,gender',
})

properties = {
    'ColumnNames': ["make", "body-style", "wheel-base", "engine-size", "horsepower", "peak-rpm", "highway-mpg"],
}

url = 'https://ussouthcentral.services.azureml.net/workspaces/64ac72519c994c3aa3857d07eb03039f/services/057904745df841a1b337fc19d4ca277a/execute?api-version=2.0&details=true'
api_key = 'vfgxt80VU+u9IUl+NhZlnWaug1009/eQnUBPmMwJPdDlDO95prZF7ykwaCJK7HszrqyL2znhHcz4cdbH4aRkDg=='  # Replace this with the API key for the web service
headers = {'Content-Type': 'application/json',
           'Authorization': ('Bearer ' + api_key)}


gender = ""
age = 0


def face_recog(url):
    try:
        conn = httplib.HTTPSConnection('westus.api.cognitive.microsoft.com')
        body = {'url': 'http://www.hz11x.com/Article/UploadFiles/200807/2008073012101702.jpg'}
        conn.request("POST", "/face/v1.0/detect?%s" % params, json.dumps(body), face_headers)
        response = conn.getresponse()
        data = response.read()
        attrs = json.loads(data)[0]['faceAttributes']
        conn.close()
        global gender, name, age
        gender = attrs['gender']
        age = attrs['age']
        print gender, age
        return data
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))


def uploadImg(request):
    print request.method
    if request.method == 'POST':
        new_img = IMG(
            img=request.FILES.get('img')
        )
        new_img.save()
        face_recog(new_img.img.url)
        return HttpResponseRedirect('/properties')
    return render(request, 'uploadimg.html')


def showImg(request):
    imgs = IMG.objects.all()
    content = {
        'imgs': imgs,
    }
    print content
    return render(request, 'showimg.html', content)


def fill_properties(request):
    return render(request, 'index.html', {'pr': properties, 'gender': gender, 'age': age})


def predict(request):
    print request.GET
    print request.GET.get('make')
    # print request.GET.get('data')
    values = []
    for cn in properties['ColumnNames']:
        print request.GET.get(cn)
        values.append(request.GET.get(cn))
    values.append(u'0')
    print values
    pridict_data = {

        "Inputs": {

            "input1":
            {
                # "ColumnNames": ["make", "body-style", "wheel-base", "engine-size", "horsepower", "peak-rpm", "highway-mpg", "price"],
                # "Values": [["subaru", "sedan", "97", "108", "111", "4800", "29", "0"], ]
            }, },
        "GlobalParameters": {
        }
    }
    pridict_data["Inputs"]["input1"].update(properties)
    # print pridict_data
    pridict_data["Inputs"]["input1"]['ColumnNames'].append('price')
    pridict_data["Inputs"]['input1']['Values'] = [values]
    print pridict_data
    body = str.encode(json.dumps(pridict_data))
    req = urllib2.Request(url, body, headers)
    try:
        response = urllib2.urlopen(req)

        # If you are using Python 3+, replace urllib2 with urllib.request in the above code:
        # req = urllib.request.Request(url, body, headers)
        # response = urllib.request.urlopen(req)

        result = response.read()
        r1 = json.loads(result)
        print type(r1), r1
        print r1['Results']['output1']['value']['Values'][0][-1]
        return JsonResponse({'price': r1['Results']['output1']['value']['Values'][0][-1]})
        # print(result)
    except urllib2.HTTPError, error:
        print("The request failed with status code: " + str(error.code))

        # Print the headers - they include the requert ID and the timestamp, which
        # are useful for debugging the failure
        print(error.info())

        print(json.loads(error.read()))
