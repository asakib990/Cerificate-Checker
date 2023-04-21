import cv2
import pytesseract


image = cv2.imread('img.jpg', 0)
thresh = cv2.threshold(image, 0, 255, cv2.THRESH_OTSU +
                       cv2.THRESH_BINARY_INV)[1]
blur = cv2.GaussianBlur(thresh, (3, 3), 0)
result = 255 - blur


# data = pytesseract.image_to_string(result, lang='eng', config='--psm 6')
data = pytesseract.image_to_string(
    result, lang='eng', config='--psm 4  --oem 3 ')

data = data.split('\n')
data = list(filter(None, data))
result = []
# print(data)

for i in range(len(data)):
    if 'Registration No.' in data[i]:
        reg = data[i][data[i].find('Registration No. '):].replace("Registration No. ",'')[:16].replace(" ",'')
        result.append({"Registration No.":reg})
    if 'Certify that' in data[i]:
        
        name = data[i][data[i].find('Certify that '):].replace('Certify that ','')
        result.append({"Name":name})
    if 'Son / Daughter of' in data[i]:
        name = data[i][data[i].find('Son / Daughter of '):].replace('Son / Daughter of ','')
        result.append({"Fathers name":name})
        name = data[i+1][data[i+1].find('and '):].replace('and ','')
        result.append({"Mothers name":name})
        name = data[i+2][data[i+2].find('of '):].replace('of ','')
        result.append({"College name":name})
    if 'bearing Roll' in data[i]:
        name = data[i][data[i].find('bearing Roll '):].replace('bearing Roll ','').split(" No. ")
        result.append({"place":name[0]})
        result.append({"Roll":name[1].replace(" ",'')})
    if 'Examination in' in data[i]:
        name = data[i][data[i].find('Examination in '):].replace('Examination in ','').replace(' group and secured','')
        result.append({"Group":name})
    if 'scale' in data[i]:
        name = data[i][data[i].find('GPA '):].replace('GPA ','').replace('scale of 5.00.','')
        name = ''.join(i for i in name if i.isdigit() or i=='.')
        result.append({"GPA":name})


print(result)
