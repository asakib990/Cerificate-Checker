import json
from warnings import catch_warnings
from django.forms.models import model_to_dict
from django.http.response import JsonResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator


import cv2
import pytesseract
import numpy as np

from home.models import dataModel

##########################################################################################################
##########################################################################################################


@csrf_exempt
def homeView(request):
    return render(request,  "home.html")


@csrf_exempt
def validate(request):
    image = request.FILES.get("image")
    data = validateImage(image)
    if data['type'] == True:
        return JsonResponse({"value": "true", "data": data})
    elif data['type'] == 'error':
        return JsonResponse({"error": "Cannot extract data from the certificate. Please use clear certificate."})

    return JsonResponse({"value": "false", "data": data})


#################HELPERS#####################

def validateImage(image):
    image = cv2.imdecode(np.fromstring(
        image.read(), np.uint8), cv2.IMREAD_GRAYSCALE)
    thresh = cv2.threshold(image, 0, 255, cv2.THRESH_OTSU +
                           cv2.THRESH_BINARY_INV)[1]
    blur = cv2.GaussianBlur(thresh, (3, 3), 0)
    result = 255 - blur
    data = pytesseract.image_to_string(
        result, lang='eng', config='--psm 4  --oem 3 ')
    data = data.split('\n')
    data = list(filter(None, data))
    result = []
    # print(data)

    for i in range(len(data)):
        if 'Registration No.' in data[i]:
            reg = data[i][data[i].find('Registration No. '):].replace(
                "Registration No. ", '')[:16].replace(" ", '')
            result.append({"Registration No.": reg})
        if 'Certify that' in data[i]:

            name = data[i][data[i].find('Certify that '):].replace(
                'Certify that ', '')
            result.append({"Name": name})
        if 'Son / Daughter of' in data[i]:
            name = data[i][data[i].find(
                'Son / Daughter of '):].replace('Son / Daughter of ', '')
            result.append({"Fathers name": name})
            name = data[i+1][data[i+1].find('and '):].replace('and ', '')
            result.append({"Mothers name": name})
            name = data[i+2][data[i+2].find('of '):].replace('of ', '')
            result.append({"College name": name})
        if 'bearing Roll' in data[i]:
            name = data[i][data[i].find('bearing Roll '):].replace(
                'bearing Roll ', '').split(" No. ")
            result.append({"place": name[0]})
            name = name[1]
            name = ''.join([s for s in name.split() if s.isdigit()])
            result.append({"Roll": name})
        if 'Examination in' in data[i]:
            name = data[i][data[i].find('Examination in '):].replace(
                'Examination in ', '').replace(' group and secured', '')
            result.append({"Group": name})
        if 'scale' in data[i]:
            name = data[i][data[i].find('GPA '):].replace(
                'GPA ', '').replace('scale of 5.00.', '')
            name = ''.join(i for i in name if i.isdigit() or i == '.')
            result.append({"GPA": name})
    typ = checkData(result)
    if typ =='error':
        return{"type": "error"}
    return {"type": typ, "data": result}


def checkData(data):
    data = dict((key, d[key]) for d in data for key in d)
    try:
        res = dataModel.objects.filter(RegistrationNo=data['Registration No.'])
    except:
        return 'error'
    # print(res)
    if res:
        res = res[0]
        # print(res.Name == data['Name'], res.Father == data['Fathers name'], res.Mother == data['Mothers name'], res.College ==
        #       data['College name'], res.Place == data['place'], res.Roll == data['Roll'], res.Group == data['Group'], res.GPA == data['GPA'])
        if res.Name == data['Name'] and res.Father == data['Fathers name'] and res.Mother == data['Mothers name'] and res.College == data['College name'] and res.Place == data['place'] and res.Roll == data['Roll'] and res.Group == data['Group'] and res.GPA == data['GPA']:
            return True
    else:
        return False
