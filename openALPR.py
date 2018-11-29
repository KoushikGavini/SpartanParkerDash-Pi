#!/usr/bin/python

import requests
import base64
import json
import os
import time
import boto3

from picamera import PiCamera
from time import sleep
#from collections import OrderedDict

camera = PiCamera()

for i in range(1):


    #camera = PiCamera()
    camera.rotation = 180
    camera.start_preview()
    sleep(5)
    camera.capture('/home/pi/Desktop/image.jpg')
    camera.stop_preview()


    IMAGE_PATH = '/home/pi/Desktop/image.jpg'
    SECRET_KEY = 'sk_9dd2d1b4ad3769557928f454'

    with open(IMAGE_PATH, 'rb') as image_file:
        img_base64 = base64.b64encode(image_file.read())

    url = 'https://api.openalpr.com/v2/recognize_bytes?recognize_vehicle=1&country=us&secret_key=%s' % (SECRET_KEY)
    r = requests.post(url, data = img_base64)
    
    
    os.remove(IMAGE_PATH)
    #create an json_object that converts the response into json string format
    json_object = r.json()
    #pretty print the json_object
    json_object2=json.dumps(json_object, indent=2)
    #convert the string into an hash for faster parsing O(1)
    json_data = json.loads(json_object2)
    #debug print
    print(json_object2)
    #Logic1: use the hash main key of results, and sub keys of candiates and plate to get the most accurate reading

    try:
        LicensePlate = json_data["results"][0]["candidates"][0]["plate"]
    except IndexError:
        LicensePlate = "Not reconziable"


        
    print("this is the license plate", LicensePlate)
    
    if LicensePlate != 'BEEF':
        LicensePlate2 = LicensePlate
    else:
        LicensePlate2 = "Nothing to invalidate"
        
    '''
The following lines of code will use the aws sdk to input the licenseplateDB with the parsed License Plate
    '''

#Getting the service

    dynamodb = boto3.resource('dynamodb')

    table = dynamodb.Table('LicensePlateDB')
    print(table.creation_date_time)
    SpotId = 'A1'


    table.put_item(
        Item={
            'LicensePlate': LicensePlate,
            'SpotId': SpotId
            }
    )

    
    table2 = dynamodb.Table('InvalidLicensePlate')
    print(table2.creation_date_time)
    
    table2.put_item(
        Item={
            'LicensePlate': LicensePlate2
            }
    )
