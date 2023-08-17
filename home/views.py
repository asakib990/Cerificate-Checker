import json
import logging
from warnings import catch_warnings
from django.forms.models import model_to_dict
from django.http.response import JsonResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from . import processImage


import cv2
import pytesseract
import numpy as np

from home.models import dataModel



print("======DATAMODEL=======")
print(dataModel)

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

roi = [
           [(1706, 272), (2090, 332), 'text', 'Registration No.'],
           [(684, 588), (2080, 672), 'text', 'Name'],
           [(542, 708), (2082, 792), 'text', 'Father Name'],
           [(224, 814), (2082, 900), 'text', 'Mother Name'],
           [(190, 928), (2082, 1016), 'text', 'College Name'],
           [(420, 1058), (1152, 1148), 'text', 'Area'],
           [(1282, 1062), (1672, 1150), 'text', 'Roll No.'],
           [(1228, 1174), (1672, 1260), 'text', 'Group'],
           [(276, 1298), (382, 1350), 'text', 'GPA']
       ]


def validateImage(image):
    # image = cv2.imdecode(np.fromstring(
    #     image.read(), np.uint8), cv2.IMREAD_GRAYSCALE)

    # image = cv2.imread(image)

    # OLD
    # thresh = cv2.threshold(image, 0, 255, cv2.THRESH_OTSU +
    #                        cv2.THRESH_BINARY_INV)[1]
    # blur = cv2.GaussianBlur(thresh, (3, 3), 0)
    # result = 255 - blur

    # UPDATED

    myData = []
    imgScan = processImage.cropImage(image)
    imgShow = imgScan.copy()
    imgMask = np.zeros_like(imgShow)

    for x, r in enumerate(roi):
        cv2.rectangle(imgMask, (r[0][0], r[0][1]), (r[1][0], r[1][1]), (0, 255, 0), cv2.FILLED)
        imgShow = cv2.addWeighted(imgShow, 0.99, imgMask, 0.1, 0)

        # -------crop info-------
        imgCrop = imgScan[r[0][1]:r[1][1], r[0][0]:r[1][0]]
        data = pytesseract.image_to_string(imgCrop)
        data = str(data)
        data = data.replace('Mad.', 'Md.')
        # myData.append(data)
        data = data.replace("\n", "").replace("\x0c", "")

        if r[3] == "GPA":
            if "." not in data:
                # Replace the comma with a period
                cleaned_string = data.replace(",", ".")
            else:
                cleaned_string = data
            print("==========GPA============== %r", cleaned_string)
            data = cleaned_string

        if r[3] == "Registration No.":
            if " " in data:
                # Replace the comma with a period
                cleaned_string = data.replace(" ", "")
            else:
                cleaned_string = data
            print("==========Registration No============== %r", cleaned_string)
            data = cleaned_string

        print(f'{r[3]}: {data}')
        myData.append({r[3]: data})

    print("========DATA========")
    print(myData)
    print(myData[0])
    print(len(myData))
    print("================")
    result = []
    search_criteria = {}
    for item in myData:
        key = next(iter(item))
        value = item[key]
        search_criteria[key] = value
        result.append(search_criteria)
    print("========RESULT============")
    print(result[0])

    # result = result[0]
    print("===================RESULT BEFORE===============")
    print(result)

    result = myData
    print("===================RESULT BEFORE")
    print(result)
    # print("========RESULT[I]============")
    # print(result['Registration No.'])

    data = []
    # OLD
    for i in range(len(result)):
        if 'Registration No.' in result[i]:
            reg = result[i]['Registration No.']
            print("============REG============")
            print(i)
            print(reg)

            print("============result[i]============")
            print(result[i])

            print("============result============")
            print(result)
            # numbers = "0123456789"
            # reg = "".join([number for number in reg if number in numbers])
            data.append({"Registration No.": reg})
            print("========RESULT==========")
            print(result)
            print("=======================")

        if 'Name' in result[i]:
            name = result[i]['Name']
            print("============name============")
            print(name)
            data.append({"Name": name})
            print("========RESULT==========")
            print(result)
            print("=======================")

        if 'Father Name' in result[i]:
            f_name = result[i]['Father Name']
            print("============f_name============")
            print(f_name)
            data.append({"Fathers name": f_name})

        if 'Mother Name' in result[i]:
            m_name = result[i]['Mother Name']
            data.append({"Mothers name": m_name})

        if 'College Name' in result[i]:
            college_name = result[i]['College Name']
            print(f"COLLAGE LAST WORD{college_name[-1]}")
            if college_name[-1] == " ":
                college_name = college_name[:-1]

            data.append({"College name": college_name})
            print("========RESULT==========")
            print(result)
            print("=======================")

        if 'Area' in result[i]:
            area_name = result[i]['Area']
            print("============area_name============")
            print(area_name)
            data.append({"Place": area_name})
            print("========PLACE==========")
            print(result)
            print("=======================")

        if 'Roll No.' in result[i]:
            roll_no = result[i]['Roll No.']
            roll_no = ''.join([s for s in roll_no.split() if s.isdigit()])
            data.append({"Roll": roll_no})
            print("========roll_no==========")
            print(result)
            print("=======================")

        if 'Group' in result[i]:
            group = result[i]['Group']
            print("====GROUP 1======")
            print(group)
            print(len(group))
            print("==========")
            i = 0
            if group[-1] == " ":
                group = group[-1].replace(group[-1], "")
            alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
            group = "".join([char for char in group if char in alphabet])

            print("====GROUP 2======")
            print(group)
            print("==========")
            data.append({"Group": group})

        if 'GPA' in result[i]:
            gpa = result[i]['GPA']
            print("=======NAME 1========")
            print(gpa)
            print("=====================")
            # gpa = ''.join(i for i in gpa if i.isdigit() or i == '.')
            # print("=======NAME 1========")
            # print(len(gpa))
            # if len(gpa) == 3:
            #     gpa = gpa[:1] + "." + gpa[1:]
            print(gpa)
            print("=====================")
            data.append({"GPA": gpa})

    # result = result[0]
    print("=========RESULT==========")
    print("RESULT %r", data)
    print("======================")

    typ = checkData(data)

    print("=========TYPE==========")
    print("TYPE %r", type)
    print("======================")



    if typ == 'error':
        return{"type": "error"}
    return {"type": typ, "data": result}


def checkData(data):
    print("============")
    print(data)
    print(type(data))

    # OLD
    data = dict((key, d[key]) for d in data for key in d)
    # print("=======SEARCH========")
    # print(search_criteria)
    # result.append(search_criteria)
    # print("=======befor result========")
    # print(result)
    # result = dict((key, d[key]) for d in result for key in d)
    # print("=======AFTER result========")
    # print(result)

    print("=======TRY========")
    print(data['Registration No.'])
    print(type(data['Registration No.']))
    print(data)
    model = dataModel.objects.all()
    # res = dataModel.objects.filter(RegistrationNo=data['Registration No.'])
    # res = dataModel.objects.get(id=1)
    print("=======RES========")
    print(model[0].id)
    print(model[0].RegistrationNo)
    print(len(model))
    length = len(model)
    for i in range(0, length):
        # pass
        # temp = data[i]

        print("========temp.RegistrationNo==========")
        print(i)
        res = model[i]
        print(res)
        print(res.RegistrationNo)
        print(data['Registration No.'])

        print(res.Place)
        for c in data['Place']:
            if c == "S":
                print(c)
            elif c == "a":
                print(c)
            elif c == "v":
                print(c)
            elif c == "a":
                print(c)
            elif c == "r":
                print(c)

        print(data['Place'])
        print("========temp.RegistrationNo==========")

        try:
            # res = temp.get(RegistrationNo=data['Registration No.'])
            res.RegistrationNo == data['Registration No.']
            print("=======PASS========")
            # print(res)
        except:
            print("=======EROOR========")
            return 'error'

        print("=======RES========")
        print(res)
        print(data)
        print(res.Place == data['Place'])
        print(res.Roll == data['Roll'])

        print("===============")
        final_result = False
        print(res.RegistrationNo == data['Registration No.'], res.Name == data['Name'], res.Father == data['Fathers name'], res.Mother == data['Mothers name'],
              res.College == data['College name'], res.Place == data['Place'], res.Roll == data['Roll'],
              res.Group == data['Group'], res.GPA == data['GPA'])
        if (res.Name == data['Name'] and res.Father == data['Fathers name'] and res.Mother == data['Mothers name'] and \
                res.College == data['College name'] and res.Place == data['Place'] and res.Roll == data['Roll'] and \
                res.Group == data['Group'] and res.GPA == data['GPA']):
            final_result = True
            break

    if final_result == True:
        return True
    else:
        return False
