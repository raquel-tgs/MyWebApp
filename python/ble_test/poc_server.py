# This is a working prototype. DO NOT USE IT IN LIVE PROJECTS
# https://github.com/bowdentheo/BLE-Beacon-Scanner/blob/master/ScanUtility.py

# https://github.com/hbldh/bleak
# https://koen.vervloesem.eu/blog/decoding-bluetooth-low-energy-advertisements-with-python-bleak-and-construct/
# import const

import asyncio
import os
import time
from csv import excel
from logging import exception
from tkinter.ttk import Treeview
import shutil
import numpy as np
import pandas as pd
import bleak
from bleak import BleakScanner
from bleak import BleakClient
from uuid import UUID
from construct import Array, Byte, Const, Int8sl, Int16ub, Struct
from construct.core import ConstError
import keyboard
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
import paho.mqtt.subscribe as subscribe
from paho.mqtt import client as paho
import json
from math import sqrt, pi, exp, pow,log, cos
from threading import Thread
from scipy.optimize import minimize
import subprocess
import psutil
import webapp as app
import ble_scan_tag as bldtag
import logging

logging.basicConfig(
    format="%(name)s: %(asctime)s | %(levelname)s | %(filename)s:%(lineno)s | %(process)d >>> %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%SZ",
)
logging.basicConfig(filename='poc_server.log',level=logging.DEBUG)
logging.info("Staring poc_server..")
# Function to run the executable
# def run_anchor1(batprg="c:\\tgspoc\\mqtt\\mqtt_server_#1_192_188_1.219.bat"):
#     try:
#         # Replace 'your_program.exe' with the path to your executable
#         subprocess.run([batprg], check=True)
#     except subprocess.CalledProcessError as e:
#         print(f"An error occurred while running the executable {0}: {1}".format(batprg,e))

#MQTT
broker ='localhost' #'broker.emqx.io' "test.mosquitto.org"#
port = 1883
topic_angle="silabs/aoa/angle/#"
topic_location="silabs/aoa/position/positioning-test_room/#"
topic_correction="silabs/aoa/correction/#"


datadf={}
janhors_processed=[]
datadf_pos = {}
jmpos_processed=[]
datadf_corr = {}
jang_corr_processed=[]

# rssi_host_scan={}
scanstarted=False
devices_processed=[]
directory = "c:/tgspoc"
app_localpath=directory+'/'

use_MQTT = False      #Set to True to start MQTT client

Stop_collecting = True
keep_mqtt_on = True
disableCTE_duringlocation = True #True
keepactive_all_CTE_during_location = False #False
keepCTE_ON_aftert_location = False
startCTE=True
startCTE_address_filter=[]#["0C:43:14:F4:6E:17"]#["0C4314F45C27","0C4314F46E7B"]
discover_rssi_start=True

scan_control={"tag_re_scan":[],"scan":0, "redo_scan":False, "scan_loop":0}
MAX_RESCAN=2
val_outliers=1.5                    #mts to discard x and y intersections from the median
CTE_Wait_Time=20                   #>1 if CTE is not alwys on.
wait_for_mqtt_angles=True          #if False set CTE_Wait_Time to enough tiome for the tag to be seen by the anchor
CTE_Wait_Time_posscan=20            #>1 if CTE_Wait_Time=1 to give time to the last tag
CTE_Wait_Time_prescan=55            # >5 if : Only necessary of server is not always on
actions_filter=["READ","LOCATION","UPDATE"]
discover_rssi=False
scan_mac_filter=[]#["0C4314F46DA1"] #A5DA find full mac
page_configuration="page_configuration"
update_mac_filter=[]
location_filter=True
MaxScan=3
MaxErrorLoops=2
MaxTags=20          #to limit the max scan time
SamplesPerTag=10
NumAnchors=4

uuuds = []
uuuds.append("a3e68a83-4c4d-4778-bd0a-829fb434a7a1")

find_milwakiee = True
find_dewalt = False
print_no_manufacturer_data = False

#(IN definition)
anchors_db={}
# 0 degree rotation
anchors_init = {}
anchors_init["0C4314F46AF2"] = {'x': 0, "y": 10, "z": 0, "max_azimut_min":-90,"max_azimut_max":0,"max_elevation_min": -90,"max_elevation_max":90, "z_rot":0, "short":"F2","IP":"192.168.1.221"}
anchors_init["0C4314F46D3D"] = {'x': 10, "y": 10, "z": 0, "max_azimut_min":-180,"max_azimut_max":-90,"max_elevation_min": -90,"max_elevation_max":90, "z_rot":0, "short":"3D","IP":"192.168.1.220"}
anchors_init["0C4314F46C1D"] = {'x': 0, "y": 0, "z": 0, "max_azimut_min":0,"max_azimut_max":90,"max_elevation_min": -90,"max_elevation_max":90, "z_rot":0, "short":"1D","IP":"192.168.1.219"}
anchors_init["0C4314F46CC0"] = {'x': 10, "y": 0, "z": 0, "max_azimut_min":90,"max_azimut_max":180,"max_elevation_min": -90,"max_elevation_max":90, "z_rot":0, "short":"C0","IP":"192.168.1.222"}
anchors_db["0 degree rotation"]=anchors_init
# # 90degree inward
anchors_init = {}
anchors_init["0C4314F46AF2"] = {'x': 0, "y": 10, "z": 0, "max_azimut_min":45,"max_azimut_max":135,"max_elevation_min": -90,"max_elevation_max":90, "z_rot":-135, "short":"F2","IP":"192.168.1.221"}
anchors_init["0C4314F46D3D"] = {'x': 10, "y": 10, "z": 0, "max_azimut_min":45,"max_azimut_max":135,"max_elevation_min": -90,"max_elevation_max":90, "z_rot":135, "short":"3D","IP":"192.168.1.220"}
anchors_init["0C4314F46C1D"] = {'x': 0, "y": 0, "z": 0, "max_azimut_min":45,"max_azimut_max":135,"max_elevation_min": -90,"max_elevation_max":90, "z_rot":-45, "short":"1D","IP":"192.168.1.219"}
anchors_init["0C4314F46CC0"] = {'x': 10, "y": 0, "z": 0, "max_azimut_min":45,"max_azimut_max":135,"max_elevation_min": -90,"max_elevation_max":90, "z_rot":45, "short":"C0","IP":"192.168.1.222"}
anchors_db["90degree inward"]=anchors_init
# -45degree inward
anchors_init = {}
anchors_init["0C4314F46AF2"] = {'x': 0, "y": 10, "z": 0, "max_azimut_min":-90,"max_azimut_max":0,"max_elevation_min": -90,"max_elevation_max":90, "z_rot":0, "short":"F2","IP":"192.168.1.221"}
anchors_init["0C4314F46D3D"] = {'x': 10, "y": 10, "z": 0, "max_azimut_min":-90,"max_azimut_max":0,"max_elevation_min": -90,"max_elevation_max":90, "z_rot":90, "short":"3D","IP":"192.168.1.220"}
anchors_init["0C4314F46C1D"] = {'x': 0, "y": 0, "z": 0, "max_azimut_min":-90,"max_azimut_max":0,"max_elevation_min": -90,"max_elevation_max":90, "z_rot":-90, "short":"1D","IP":"192.168.1.219"}
anchors_init["0C4314F46CC0"] = {'x': 10, "y": 0, "z": 0, "max_azimut_min":-90,"max_azimut_max":0,"max_elevation_min": -90,"max_elevation_max":90, "z_rot":180, "short":"C0","IP":"192.168.1.222"}
anchors_db["-45degree inward"]=anchors_init
anchors_db_layout="-45degree inward"
anchors_init=anchors_db[anchors_db_layout]
gateway={"x":1,"y":1,"rssi":-45.18608923884508, "rssi_ref":-62.236408977555826, "dist_ref":6.905070600652827, "dist":1.4142135623730951}

# max_azimut_min = -135
# max_azimut_max = -45
# max_elevation_min = -90
# max_elevation_max = +90

def quadratic_error(x, values):
    return np.sum((values - x) ** 2)

#----------------------------------------------------------------------#
srv_antenna_anchor={}
srv_antenna_anchor["219"]={"enabled":True, "status":None,"process":None,"monitor_thread":None, "bat_file": "C:\\tgspoc\\mqtt\\mqtt_server_#1D_192_168_1_219.bat","cmdline":""}
srv_antenna_anchor["220"]={"enabled":True, "status":None,"process":None,"monitor_thread":None,"bat_file": "C:\\tgspoc\\mqtt\\mqtt_server_#3D_192_168_1_220.bat","cmdline":""}
srv_antenna_anchor["221"]={"enabled":True, "status":None,"process":None,"monitor_thread":None,"bat_file": "C:\\tgspoc\\mqtt\\mqtt_server_#F2_192_168_1_221.bat","cmdline":""}
srv_antenna_anchor["222"]={"enabled":True, "status":None,"process":None,"monitor_thread":None,"bat_file": "C:\\tgspoc\\mqtt\\mqtt_server_#C0_192_168_1_222.bat","cmdline":""}
srv_antenna_anchor["srv"]={"enabled":True, "status":None,"process":None,"monitor_thread":None,"bat_file": "C:\\tgspoc\\mqtt\\start_mqtt_position.bat","cmdline":""}

#------------------------------- BLE CONSTANTS ----------------------------
#Gatt database
#--------------------
# char_uuid = {}
# char_uuid[0]={"id": "tag_id", "uuid": "c01cdf18-2465-4df6-956f-fde4867e2bc1", "value": "","scan":True,'type':"UTF-8","length":50, "data_type":"base","NFC":False}
# char_uuid[1]={"id": "asset_id", "uuid": "7db7b5e3-168e-48fd-aadb-94607557b832", "value": "", "scan": True, 'type': "UTF-8","length":150, "data_type":"base","NFC":False}
# char_uuid[2]={"id": "update_nfc", "uuid": "1b9bba4d-34c0-4542-8d94-0da1036bd64f", "value": "","scan":False,'type':"HEX","length":1, "data_type":"configuration","NFC":False}
# char_uuid[3]={"id": "ble_data_crc", "uuid": "cfdd75b8-5ed3-43cd-96cd-35129f648c5d", "value": "","scan":False,'type':"UTF-8","length":8, "data_type":"base","NFC":False}
# char_uuid[4]={"id": "certificate_id", "uuid": "fd052ad3-b4d3-426f-be19-b6b3107ab535", "value": "","scan":True,'type':"UTF-8","length":60, "data_type":"base","NFC":False}
# char_uuid[5]={"id": "type", "uuid": "d1251886-0135-4757-a6a4-233ed79914f3", "value": "","scan":True,'type':"UTF-8","length":150, "data_type":"base","NFC":False}
# char_uuid[6]={"id": "expiration_date", "uuid": "04f7c038-5717-4da6-b0af-4441388bf938", "value": "","scan":True,'type':"UTF-8","length":10, "data_type":"base","NFC":False}
# char_uuid[7]={"id": "color", "uuid": "3ef6ebcc-db6e-4b65-ab42-81bedf9c95a5", "value": "","scan":True,'type':"UTF-8","length":20, "data_type":"base","NFC":False}
# char_uuid[8]={"id": "series", "uuid": "b68a7594-7bf0-4da5-9067-cf986fa2e91d", "value": "","scan":True,'type':"UTF-8","length":32, "data_type":"base","NFC":False}
# char_uuid[9]={"id": "asset_images_file_extension", "uuid": "c53ff832-45ae-4a94-8bb9-26bea6b64c2c", "value": "","scan":True,'type':"UTF-8","length":3, "data_type":"base","NFC":False}
# char_uuid[10]={"id": "read_nfc", "uuid": "d2fe9b8c-fdfa-4006-b1ef-44969591fb1b", "value": "","scan":True,'type':"HEX","length":1, "data_type":"base","NFC":False}
# char_uuid[11]={"id": "certification_company_name", "uuid": "d2bcecac-383d-4224-a60b-bb35ebc4defb", "value": "","scan":True,'type':"UTF-8","length":50, "data_type":"detail","NFC":False}
# char_uuid[12]={"id": "certification_company_id", "uuid": "91cdf87d-a278-486f-942c-ab1816565dc2", "value": "","scan":True,'type':"UTF-8","length":50, "data_type":"detail","NFC":False}
# char_uuid[13]={"id": "certification_place", "uuid": "b184ba24-a2ab-460d-8cb5-d9424017d730", "value": "","scan":True,'type':"UTF-8","length":50, "data_type":"detail","NFC":False}
# char_uuid[14]={"id": "certification_date", "uuid": "5d5d87d9-eafe-4197-8893-ffa5576cf657", "value": "","scan":True,'type':"UTF-8","length":10, "data_type":"detail","NFC":False}
# char_uuid[15]={"id": "test_type", "uuid": "183d8f3e-8276-4b6f-ac45-beb289ab4e21", "value": "","scan":True,'type':"UTF-8","length":150, "data_type":"detail","NFC":False}
# char_uuid[16]={"id": "asset_diameter", "uuid": "b21f382a-9115-4236-958d-df714beee49a", "value": "","scan":True,'type':"UTF-8","length":10, "data_type":"detail"}
# char_uuid[17]={"id": "asset_comment", "uuid": "1984cab5-5f24-4e98-87d8-0559c96980d5", "value": "","scan":True,'type':"UTF-8","length":20, "data_type":"detail","NFC":False}
# char_uuid[18]={"id": "batch_id", "uuid": "34992c7e-8d34-4b87-b9c8-8fbcc3641a27", "value": "","scan":True,'type':"UTF-8","length":50, "data_type":"detail","NFC":False}
# char_uuid[19]={"id": "batch_date", "uuid": "9ac91987-9da4-41b3-a60c-5c407bc7881d", "value": "","scan":True,'type':"UTF-8","length":10, "data_type":"detail","NFC":False}
# char_uuid[20]={"id": "machine_id", "uuid": "ed5c5d2b-486c-46ce-9812-6fc09d0a64b8", "value": "","scan":True,'type':"UTF-8","length":50, "data_type":"detail","NFC":False}
# char_uuid[21]={"id": "status_code", "uuid": "d469aa23-63da-42c9-83ed-e2dc5601acd7", "value": "","scan":True,'type':"UTF-8","length":4, "data_type":"configuration","NFC":False}
# char_uuid[22]={"id": "asset_images_crc", "uuid": "4bdbf8ed-53a9-4518-a907-c4376e43b62d", "value": "","scan":True,'type':"UTF-8","length":4, "data_type":"detail","NFC":False}
# char_uuid[23]={"id": "logo_images_crc", "uuid": "30dd3370-65e7-48ec-871d-1994bc9cc2fc", "value": "","scan":True,'type':"UTF-8","length":4, "data_type":"detail","NFC":False}
# char_uuid[24]={"id": "signature_images_crc", "uuid": "028f73b8-e36b-4cd9-b99b-51f946e8888b", "value": "","scan":True,'type':"UTF-8","length":4, "data_type":"detail","NFC":False}
# char_uuid[25]={"id": "owner_company_name", "uuid": "5b7ef22d-72a9-490c-bdba-1bd225531e6f", "value": "","scan":True,'type':"UTF-8","length":50, "data_type":"detail","NFC":False}
# char_uuid[26]={"id": "owner_data", "uuid": "e46f56de-7341-4231-9f29-b8ae5e470a93", "value": "","scan":True,'type':"UTF-8","length":50, "data_type":"detail","NFC":False}
# char_uuid[27]={"id": "ndir_id", "uuid": "8024d4a4-f212-497b-8499-4b1ebb467b48", "value": "","scan":True,'type':"UTF-8","length":50, "data_type":"detail","NFC":False}
# char_uuid[28]={"id": "tag_mac", "uuid": "6a103778-d584-4ce6-b3e2-94f417673cfc", "value": "","scan":True,'type':"UTF-8","length":20, "data_type":"configuration","NFC":False}
#
# char_uuid[29]={"id": "enable_cte" , "uuid": "c92c584f-7b9e-473a-ad4e-d9965e0cd678", "value": "","scan":True,'type':"HEX","length":1, "data_type":"configuration","NFC":False}
# char_uuid[30]={"id": "tag_enabled" , "uuid": "886eb62a-2c17-4e8e-9579-1c5483973577", "value": "","scan":True,'type':"HEX","length":1, "data_type":"configuration","NFC":False}
# char_uuid[31]={"id": "tag_advertisement_period", "uuid": "4f9c97c2-41c2-4215-ab22-8c0a9d3ba777", "value": "","scan":True,'type':"HEX","length":4, "data_type":"configuration","NFC":False}
# char_uuid[32]={"id": "ble_on_period", "uuid": "b13603ed-2ac4-4ee1-9b4d-21ee264543a4", "value": "","scan":True,'type':"HEX","length":4, "data_type":"configuration","NFC":False}
# char_uuid[33]={"id": "ble_on_wakeup_period", "uuid": "41af4710-5494-4793-860f-31031c3148bd", "value": "","scan":True,'type':"HEX","length":4, "data_type":"configuration","NFC":False}
# char_uuid[34]={"id": "ble_off_period", "uuid": "ed407a07-5109-4525-894a-6182aacf8237", "value": "","scan":True,'type':"HEX","length":4, "data_type":"configuration","NFC":False}
# char_uuid[35]={"id": "tag_periodic_scan", "uuid": "f178d4ee-af0a-418f-b302-47c051578047", "value": "","scan":True,'type':"HEX","length":1, "data_type":"configuration","NFC":False}
# char_uuid[36]={"id": "battery_voltage", "uuid": "9b9dcb7a-b2f5-4a3d-8e59-b96a9b88b6ef", "value": "","scan":True,'type':"HEX","length":4, "data_type":"configuration","NFC":False}
# char_uuid[37]={"id": "read_battery_voltage", "uuid": "914254cd-dafe-4bb8-8517-048adb4e08ab", "value": "","scan":True,'type':"HEX","length":1, "data_type":"configuration","NFC":False}
# char_uuid[38]={"id": "altitude", "uuid": "6d139387-9f68-4827-8442-641956a94979", "value": "","scan":True,'type':"HEX","length":4, "data_type":"configuration","NFC":False}
# char_uuid[39]={"id": "moved", "uuid": "e410f434-a1f1-4088-9578-19d08830a489", "value": "","scan":True,'type':"HEX","length":1, "data_type":"configuration","NFC":False}
# char_uuid[40]={"id": "tag_firmware", "uuid": "ae795504-8f02-4d4c-bd37-b46935193fd2", "value": "","scan":True,'type':"UTF-8","length":10, "data_type":"configuration","NFC":False}

# def filter_db(id, data_type=None, scan=None):
#     try:
#         res=None
#         if id is None:
#             res = [y for y in [char_uuid[x] for x in list(char_uuid)] if   (y["scan"] == scan or scan is None) and (y["data_type"] == data_type or data_type is None)]
#         else:
#             if type(id) is list:
#                 res = [y for y in [char_uuid[x] for x in list(char_uuid)] if (y["scan"] == scan or scan is None) and (y["data_type"] == data_type or data_type is None) and y["id"] in id]
#             else:
#                 res=[y for y in [char_uuid[x] for x in list(char_uuid)] if (y["scan"] == scan or scan is None) and (y["data_type"] == data_type or data_type is None) and y["id"] == id][0]
#     except Exception as e:
#         print(e)
#     return res

#cahracteristics
# char_uuid_update_nfc=filter_db("update_nfc")["uuid"] #"1b9bba4d-34c0-4542-8d94-0da1036bd64f"
# char_uuid_enable_cte =filter_db("enable_cte")["uuid"] #"c92c584f-7b9e-473a-ad4e-d9965e0cd678"


# serv_uuid_Custom_Service = "87e29466-8be6-4ede-9ffb-04a7121938da"
# serv_uuid_Generic_Service = "00001800-0000-1000-8000-00805f9b34fb"
# serv_uuid_Constant_Tone_Service="0000184a-0000-1000-8000-00805f9b34fb"


charfile_uuid=[]
charfile_uuid.append({"id": "buffer_read", "uuid": "68ed3fb7-03c6-48cd-b385-baa4c8bce505", "value": "","scan":True,'type':"HEX","length":255})
charfile_uuid.append({"id": "buffer_write", "uuid": "715016b1-abd0-41cd-80d9-9a997f87c642", "value": "", "scan": True,'type': "HEX", "length": 255})
charfile_uuid.append({"id": "file_length", "uuid": "d86480ed-95f1-4cf9-9b7a-dd3ff2cdeb35", "value": "", "scan": True, 'type': "HEX","length": 4})
charfile_uuid.append({"id": "file_transfer_status", "uuid": "3d03d488-34b8-4f94-b9a1-0f7e339b7878", "value": "", "scan": True, 'type': "HEX", "length": 1})
charfile_uuid.append({"id": "file_length_sent", "uuid": "89bc1cd2-cee7-46a6-ba38-d3497678a777", "value": "", "scan": True, 'type': "HEX","length": 4})
serv_uuid_Custom_File_Transfer_Service = "4c209b89-3330-4f18-b26e-d90f8653306e"

#x,y must be the last in the row defintion as they are not part of the scan
# csv_row={'mac':"","name":"",'tag_id':"",'asset_id':"",'certificate_id':"",'type':"",'expiration_date':"",'color':"",'series':"",'asset_images_file_extension':"","read_nfc":""}
# scan_columnIds = ['mac', 'name', 'tag_id', 'asset_id', 'certificate_id', 'type', 'expiration_date', 'color', 'series', 'asset_images_file_extension','read_nfc',  'x', 'y'];

#base
# csv_row={"mac":"","name":"","tag_id":"","asset_id":"","certificate_id":"","type":"","expiration_date":"","color":"","series":"","read_nfc":"","status":"","status_code":"","asset_images_file_extension":"","x":"","y":""}
# scan_columnIds=["mac","name","tag_id","asset_id","certificate_id","type","expiration_date","color","series","read_nfc","status","status_code","asset_images_file_extension","x","y"]

#detail
# csv_extended_row={"mac":"","certification_company_name":"","certification_company_id":"","certification_place":"","certification_date":"","test_type":"","asset_diameter":"",
#          "batch_id":"","batch_date":"","machine_id":"","status_code":"","ble_data_crc":"","asset_images_crc":"","logo_images_crc":"","signature_images_crc":"",
#          "owner_company_name":"","owner_data":"","altitude":"","moved":"","battery_voltage":"","asset_comment":"","ndir_id":"","status":"","x":"","y":""}
# scan_extended_columnIds=["mac","certification_company_name",
#                 "certification_company_id","certification_place","certification_date","test_type","asset_diameter","batch_id","batch_date",
#                 "machine_id","status_code","ble_data_crc","asset_images_crc","logo_images_crc","signature_images_crc","owner_company_name",
#                 "owner_data","altitude","moved","battery_voltage","asset_comment","ndir_id","status","x","y"]
#onfiguration
# csv_config_row={"mac":"","status_code":"","enable_cte":"","tag_enabled":"","tag_advertisement_period":"",
#                 "ble_on_period":"","ble_on_wakeup_period":"","tag_mac":"","read_battery_voltage":"",
#                 "ble_off_period":"","tag_periodic_scan":"","altitude":"","moved":"","battery_voltage":"","tag_firmware":"","status":"","x":"","y":""}
# scan_config_columnIds=["mac","status_code","enable_cte","tag_enabled","tag_advertisement_period","ble_on_period","tag_mac","read_battery_voltage",
#                        "ble_on_wakeup_period","ble_off_period","tag_periodic_scan","altitude","moved","battery_voltage","tag_firmware","status","x","y"]
#
# cloud_csv_row={"mac":"","logo_file_extension":"","signature_image_file_extension":"","is_machine":""}
# cloud_scan_columnIds=["mac","logo_file_extension","signature_image_file_extension","is_machine"]

# location_cvs_row={"tag_mac":"","out_prob":"","out_prob_k":"","anchors":"","result":"","x":"","y":""}
# location_cvs_columnIds=["tag_mac","out_prob","out_prob_k","anchors","result","x","y"]

# char_uuid_nfc=["certification_company_name","certification_company_id","certification_place","certification_date",
#                "certificate_id","expiration_date","test_type","asset_id",
#                "tag_id","type","color","series",
#                "asset_diameter","asset_comment","batch_id","batch_date",
#                "machine_id","status_code","ble_data_crc","asset_images_crc",
#                "logo_images_crc","signature_images_crc","owner_company_name","owner_data",
#                "ndir_id","asset_images_file_extension","tag_mac","gattdb_tag_periodic_scan"]


#-------------------------------------------------------------------------------

def is_batch_file_running(batch_file_name):
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            # Check if the process command line contains the batch file name
            if proc.info['cmdline'] is not None and len(proc.info['cmdline'])==3:
                # if (proc.info['cmdline'][0]=='cmd' or proc.info['cmdline'][0]=="C:\\WINDOWS\\system32\\cmd.exe") and proc.info['cmdline'][1]=='/c':
                if proc.info['cmdline'][1] == '/c':
                    # print(proc.info['cmdline'])
                    #print(proc.info['cmdline'][2])
                    if batch_file_name[4] == proc.info['cmdline'][2]:
                        return True,proc
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False,None

def monitor_process(process,anchor,srv_antenna_anchor):
    """Function to monitor the process output and status."""
    while True:
        try:
            #time.sleep(5)
            output = process.stdout.readline()
            print("monitor_process {0} : process.poll(): {1} - output: {1}".format(anchor,process.poll(), output.decode().strip()))
            if output == b'' and process.poll() is not None:
                srv_antenna_anchor[anchor]["status"] = False
                print("monitor_process {0} : Terminate Montor".format(anchor))
                break
            if output:
                print(output.decode().strip())

        except Exception as e:
            print("monitor_process {0} : {1}".format(anchor, e))


    return process.poll()


def run_bat_file(bat_file,anchor,srv_antenna_anchor):
    """Function to run the .bat file."""
    try:
        # process = subprocess.Popen(['start', 'cmd', '/k', bat_file] , stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        cmdline = ['start', '/MIN', 'cmd', '/c', bat_file]
        process = subprocess.Popen(cmdline, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   shell=True)

        monitor_thread = Thread(target=monitor_process, args=(process,anchor,srv_antenna_anchor,))
        monitor_thread.start()
    except Exception as e:
        print("run_bat_file {}".format(e))

    return process, monitor_thread,cmdline

def terminate_process(process):
    """Function to terminate the process."""
    process.terminate()


#---------------------------------------------------------------------#
#Call back advertisement
#
#---------------------------------------------------------------------#
# def device_found(device: BLEDevice, advertisement_data: AdvertisementData):
#     """Decode iBeacon."""
#     try:
#         bres = False
#         # print("device.name -------------------> %s" % device.name)
#         # print("nservice_uuids %s" % advertisement_data.service_uuids)
#         # print("nmanufacturer_data %s" % advertisement_data.manufacturer_data)
#         # print("local_name --------->>%s" % advertisement_data.local_name)
#         # print("service_data %s" % advertisement_data.service_data)
#         # print("rssi %s" % advertisement_data.rssi)

#         if device.name is not None:
#             if device.name.startswith("BoldTag"):
#                 address=device.address.replace(":","")
#                 rssi=advertisement_data.rssi
#                 if (address in startCTE_address_filter or len(startCTE_address_filter)==0) and discover_rssi_start:
#                     #print("RSSI {0}:{1}".format(address,rssi))
#                     tag_data_crc="0000000000000000"
#                     if len(advertisement_data.manufacturer_data.items())>0:
#                        tag_data_crc=[x for x in advertisement_data.manufacturer_data.items()][0][1].hex()
#                     rssi_host_scan[len(rssi_host_scan)]={"address":address,"rssi_host":rssi,"tag_data_crc":tag_data_crc}

#     except Exception as e:
#         print(f'error in device_found {e}')

#---------------------------------------------------------------------#
#                   MQTT Subscription
#
#---------------------------------------------------------------------#
def on_subscribe(client, userdata, mid, granted_qos):
    try:
        print("Subscribed: "+str(mid)+" "+str(granted_qos))
    except Exception as e:
        print(e)

def on_message(client, userdata, message):
    #print(message.topic+" "+str(message.qos)+" "+str(message.payload))
    #print(f"Received message {message.payload} on topic '{message.topic}' with QoS {message.qos}")
    #print(str(message.topic))
    try:
        topic = str(message.topic)
        #print(topic)
        if not Stop_collecting:
            if topic.startswith(topic_angle[:-2]):
                janhors = pass_to_func_and_pub(message.payload.decode('utf-8'))
                anchor = topic.split("/")[3]
                tag = topic.split("/")[4]
                tag_mac=tag.split("-")[2]
                anchor_mac=anchor.split("-")[2]
                janhors['tag_mac'] = tag_mac
                janhors['anchor_mac'] = anchor_mac
                datadf[len(datadf)] = janhors
                if tag_mac not in janhors_processed:
                    janhors_processed.append(tag_mac)
                    print("Processing Angles {0}".format(tag_mac))


            if topic.startswith(topic_location[:-2]):

                jmpos = pass_to_func_and_pub(message.payload.decode('utf-8'))
                topic_pos = message.topic
                tag = topic_pos.split("/")[4]
                tag_mac = tag.split("-")[2]
                jmpos['tag_mac'] = tag_mac
                datadf_pos[len(datadf_pos)] = jmpos
                if tag_mac not in jmpos_processed:
                    jmpos_processed.append(tag_mac)
                    print("Processing Position {0}".format(tag_mac))

            if topic.startswith(topic_correction[:-2]):
                jang_corr = pass_to_func_and_pub(message.payload.decode('utf-8'))
                topic_corr = message.topic
                anchor = topic_corr.split("/")[3]
                tag = topic_corr.split("/")[4]
                tag_mac = tag.split("-")[2]

                jang_corr['tag_mac'] = tag_mac
                jang_corr['anchor_mac'] = anchor.split("-")[2]
                datadf_corr[len(datadf_corr)] = jang_corr
                if tag_mac not in jang_corr_processed:
                    jang_corr_processed.append(tag_mac)
                    print("Processing Correction {0}".format(tag_mac))


    except Exception as e:
        print(e)

# 0: Connection accepted
# 1: Connection refused because the protocol level is not supported
# 2: Connection refused because the server does not allow the client identifier
# 3: Connection refused because the MQTT service is not available
# 4: Connection refused because the username or password data is malformed
# 5: Connection refused because the client is not authorized to connect
def on_connect(client, userdata, flags, rc):
    try:
        print('CONNACK received with code %d.' % (rc))
        if (rc==0):
            client.on_message = on_message
            print("Connected to MQTT Broker!")
            res = client.subscribe(topic=topic_angle, qos=1)
            print('subscribe code {0}'.format(res))
            res = client.subscribe(topic=topic_location, qos=1)
            print('subscribe code {0}'.format(res))
            res = client.subscribe(topic=topic_correction, qos=1)
            print('subscribe code {0}'.format(res))
        else:
            print("Failed to connect, return code %d\n", rc)
    except Exception as e:
        print(e)
def on_disconnect(client, userdata, rc):
    try:
        print("DisConnected result code "+str(rc))
        client.loop_stop()
    except Exception as e:
        print(e)
def run_mqtt():
    try:
        client = paho.Client(client_id="local_test")
        client.on_connect = on_connect
        client.connect(broker, port)
        client.loop_start()
    except Exception as e:
        print(e)
    return client

def threaded_function(client):
    try:
        client.loop_forever()
    except Exception as e:
        print(e)


#---------------------------------------------------------------------#
#                   Kalmann Filter
#
#---------------------------------------------------------------------#
# gaussian function
def f(mu, sigma2, x):
    ''' f takes in a mean and squared variance, and an input x
       and returns the gaussian value.'''
    coefficient = 1.0 / sqrt(2.0 * pi *sigma2)
    exponential = exp(-0.5 * (x-mu) ** 2 / sigma2)
    return coefficient * exponential


# the update function
def update(mean1, var1, mean2, var2):
    ''' This function takes in two means and two squared variance terms,
        and returns updated gaussian parameters.'''
    # Calculate the new parameters
    new_mean = (var2 * mean1 + var1 * mean2) / (var2 + var1)
    new_var = 1 / (1 / var2 + 1 / var1)

    return [new_mean, new_var]


# the motion update/predict function
def predict(mean1, var1, mean2, var2):
    ''' This function takes in two means and two squared variance terms,
        and returns updated gaussian parameters, after motion.'''
    # Calculate the new parameters
    new_mean = mean1 + mean2
    new_var = var1 + var2

    return [new_mean, new_var]
#data_last_scan=self.est_kalmann(data_last_scan, measurement_sig=2., mu=np.mean([int(x['rssi']) for x in data_last_scan]), sig=10000.)
def est_kalmann(data_last_scan,measurement_sig = 2.,mu_ini = 0.,sig = 10000., y_name="rssi",x_name=["tag_mac","anchor_mac"], verbose=False):
    try:
        # initial parameters
        # measurement_sig = 2.
        # motion_sig = 2.
        # mu = 0.
        # sig = 10000.
        k_mu = "k_{0}_mu".format(y_name)
        k_sig = "k_{0}_sig".format(y_name)

        data = data_last_scan#pd.DataFrame(data_last_scan)
        data[k_mu] = 0
        data[k_sig] = 0
        tag_mac=x_name[0]
        anchor_mac=x_name[1]
        # for i in range(len(data.groupby([tag_mac]).count().reset_index()[tag_mac])):
        #     d1 = data[data[tag_mac] == (data.groupby([tag_mac]).count().reset_index()[tag_mac][i])]
        #     for j in range(len(d1.groupby([anchor_mac]).count().reset_index()[anchor_mac])):
        #         fd1 = data[tag_mac] == (data.groupby([tag_mac]).count().reset_index()[tag_mac][i])
        #         fd2 = d1[anchor_mac] == (d1.groupby([anchor_mac]).count().reset_index()[anchor_mac][j])
        #         f = (fd1 & fd2)
        #         # d2=data[f]
        for ix, rec in data.groupby([anchor_mac,tag_mac]):
                # d2 = d1[d1["node"] == (d1.groupby(["node"]).count().reset_index()["node"][j])]
                # measurements = data[f][y_name].values
                measurements = rec[y_name].values
                # motions = data.loc[f,["rssi"]].values
                ## TODO: Loop through all measurements/motions
                # this code assumes measurements and motions have the same length
                # so their updates can be performed in pairs
                if mu_ini is None:
                    mu=measurements.mean()
                else:
                    mu=mu_ini
                for n in range(len(measurements)):
                    # measurement update, with uncertainty
                    if verbose :print('measurement: [{}, ]'.format(measurements[n]))
                    mu, sig = update(mu, sig, measurements[n], measurement_sig)
                    if verbose :print('Update: [{}, {}]'.format(mu, sig))
                    # motion update, with uncertainty
                    # mu, sig = predict(mu, sig, motions[n], motion_sig)
                    # print('Predict: [{}, {}]'.format(mu, sig))

                # print the final, resultant mu, sig
                if verbose :print('\n')
                if verbose :print('Final result: [{}, {}]'.format(mu, sig))
                data.loc[rec.index, [k_mu]] = mu
                data.loc[rec.index, [k_sig] ]= sig

        # i = 0
        # for x in data_last_scan:
        #     x[k_mu] = data.loc[i][k_mu]
        #     x[k_sig] = data.loc[i][k_sig]
        #     i = i + 1

    except Exception as e:
        # logging.error('Error at %s', 'division', exc_info=e)
        print('Error at %s'%e)
    return data#data_last_scan

#---------------------------------------------------------------------#
# END  Kalmann Filter
#---------------------------------------------------------------------#



#---------------------------------------------------------------------#
#                 Scan Location
#
#---------------------------------------------------------------------#
def pass_to_func_and_pub(data_to_pub, verbose=False):
    if verbose:print("Raw data: ", data_to_pub)
    try:
        unpacked_json = json.loads(data_to_pub)
    except Exception as e:
        print("Couldn't parse raw data: %s" % data_to_pub, e)
    else:
        if verbose: print("JSON:", unpacked_json)
    return unpacked_json

def filter_location(file_path_angle,file_path_correction,file_path_angle_raw,file_path_correction_raw,file_path_position_raw,rssi_host_scan, scan_control,
                    file_path_xposition_raw,file_path_yposition_raw,file_path_rposition_raw, tagfilter=[], val_outliers=1.5):
    resdf=None
    dataavg=None
    data_posavg=None
    dataavg1=None
    dfpos_x = None
    dfpos_r = None
    dfpos_y = None
    cancel_process = False
    try:
        try:
            scan_control["ScanError"] = False
            data=pd.DataFrame.from_dict(datadf, orient="index")
            data_pos = pd.DataFrame.from_dict(datadf_pos, orient="index")
            data_corr = pd.DataFrame.from_dict(datadf_corr, orient="index")
            if len(tagfilter)>0:
                if data.shape[0]>0: data = data[data['tag_mac'].isin(tagfilter)]
                if data_pos.shape[0]>0: data_pos=data_pos[data_pos['tag_mac'].isin(tagfilter)]
                if data_corr.shape[0]>0: data_corr=data_corr[data_corr['tag_mac'].isin(tagfilter)]
            if len(scan_control["tag_re_scan"])>0:
                data = data[data["tag_mac"].isin(scan_control["tag_re_scan"])]
                if data_pos.shape[0]>0:data_pos = data_pos[data_pos["tag_mac"].isin(scan_control["tag_re_scan"])]
                if data_corr.shape[0]>0:data_corr = data_corr[data_corr["tag_mac"].isin(scan_control["tag_re_scan"])]
            data_corravg=None
            if data.shape[0]>0:
                dataavg1 = data.groupby(['anchor_mac', 'tag_mac']).median().reset_index()
                dataavg1['samples'] = data[['anchor_mac', 'tag_mac', "azimuth"]].groupby(['anchor_mac', 'tag_mac']).count().values
            if data_pos.shape[0]>0:data_posavg = data_pos.groupby([ 'tag_mac']).mean().reset_index()
            if data_corr.shape[0]>0:
                data_corravg = data_corr.groupby(['anchor_mac', 'tag_mac']).mean().reset_index()
                data_corravg["samples"] = data_corr[['anchor_mac', 'tag_mac', "azimuth"]].groupby(['anchor_mac', 'tag_mac']).count().values

            if data_posavg is not None: data_posavg["d"] = np.sqrt(data_posavg["x"] ** 2 + data_posavg["y"] ** 2)
            # caltest.append(data_posavg.values[0])
            # data_cal = pd.DataFrame(caltest)
            # data_cal.columns = data_pos.columns

            if data_corravg is not None and dataavg1 is not None:
                rows_list=[]
                for ix, rec in dataavg1.groupby("anchor_mac"):
                    for k in rec["tag_mac"].values:
                        chk=(data_corravg["anchor_mac"]==ix) & (data_corravg["tag_mac"]==k)
                        chk1 = (dataavg1["anchor_mac"] == ix) & (dataavg1["tag_mac"] == k)
                        if sum(chk)>0:
                            rows_list.append(data_corravg[chk].values[0])
                        else:
                            rows_list.append(dataavg1[chk1].values[0])
                dataavg = pd.DataFrame(rows_list)
                dataavg.columns =    dataavg1.columns
            else:
                dataavg=dataavg1

            #Angels autisde
            dataavg["out_prob"] = 0
            res={}
            for ix,rec in dataavg.groupby("tag_mac"):
                res_tag_val=[]
                for a in rec['anchor_mac'].values:
                    res_tag_val.append(((rec[rec["anchor_mac"]==a]['azimuth'].values>=anchors_init[a]["max_azimut_max"]) | (rec[rec["anchor_mac"]==a]['azimuth'].values<=anchors_init[a]["max_azimut_min"])))
                res_tag=sum(res_tag_val)[0]/rec.shape[0]
                tagname = rec[["tag_mac"]].values[0][0]
                res[tagname]=res_tag
                #res.append({"tag_mac":tagname, "out_prob": res_tag, "num_anchors":rec.shape[0]})
            resdf=pd.DataFrame.from_dict(res, orient="index").reset_index()
            resdf.columns=["tag_mac","out_prob"]
            print(resdf)

            #Kalmann filtering
            data=est_kalmann(data, measurement_sig=2.,mu_ini=None, sig=10000., y_name="azimuth",x_name=["tag_mac","anchor_mac"])
            data = est_kalmann(data, measurement_sig=2., mu_ini=None, sig=10000., y_name="elevation",
                               x_name=["tag_mac", "anchor_mac"])
            data = est_kalmann(data, measurement_sig=2., mu_ini=None, sig=10000., y_name="distance",
                               x_name=["tag_mac", "anchor_mac"])
                # data.loc[res.index,"azimuth_k"] = res["k_azimuth_mu"]
                # data.loc[res.index, "azimuth_k"] = res["k_azimuth_sig"]
            dataavg["k_azimuth_mu"]=0
            dataavg["k_azimuth_sig"] = 0
            dataavg["k_distance_mu"]=0
            dataavg["k_distance_sig"] = 0
            dataavg["k_elevation_mu"]=0
            dataavg["k_elevation_sig"] = 0

            for ix, rec in data.groupby(["tag_mac", "anchor_mac"]):
                kx=dataavg[(dataavg["tag_mac"]==ix[0]) & (dataavg["anchor_mac"]==ix[1])].index
                dataavg.loc[kx,"k_azimuth_mu"]=rec["k_azimuth_mu"].values[0]
                dataavg.loc[kx, "k_azimuth_sig"] = rec["k_azimuth_sig"].values[0]
                dataavg.loc[kx, "k_distance_mu"] = rec["k_distance_mu"].values[0]
                dataavg.loc[kx, "k_distance_sig"] = rec["k_distance_sig"].values[0]
                dataavg.loc[kx, "k_elevation_mu"] = rec["k_elevation_mu"].values[0]
                dataavg.loc[kx, "k_elevation_sig"] = rec["k_elevation_sig"].values[0]

            #Angels autisde using Kalmann
            dataavg["out_prob_k"] = 0
            res={}
            for ix,rec in dataavg.groupby("tag_mac"):
                res_tag_val=[]
                for a in rec['anchor_mac'].values:
                    res_tag_val.append(((rec[rec["anchor_mac"]==a]['k_azimuth_mu'].values>=anchors_init[a]["max_azimut_max"]) | (rec[rec["anchor_mac"]==a]['k_azimuth_mu'].values<=anchors_init[a]["max_azimut_min"])))
                res_tag=sum(res_tag_val)[0]/rec.shape[0]
                tagname = rec[["tag_mac"]].values[0][0]
                res[tagname]=res_tag
                #res.append({"tag_mac":tagname, "out_prob": res_tag, "num_anchors":rec.shape[0]})
            resdf_k=pd.DataFrame.from_dict(res, orient="index").reset_index()
            resdf_k.columns=["tag_mac","out_prob_k"]
            print(resdf)
            resdf=resdf.join(resdf_k.set_index("tag_mac"), on="tag_mac")
            resdf["anchors"]=rec.shape[0]
            if rec.shape[0]==4:
                rmin=1/4
            elif rec.shape[0]==3:
                rmin=1/3
            else:
                rmin=0
            if rmin>0:
                resdf["result"] = ["OUT" if x > rmin else "IN" for x in resdf["out_prob_k"].values]
            else:
                resdf["result"] =np.nan

                #distanc from gateway from rssi
            dfrssi_host=None
            dfrssi_host_scan=pd.DataFrame.from_dict(rssi_host_scan, orient="index")
            dfrssi_host_scan["host"] = "host"
            if dfrssi_host_scan.shape[0]>0:
                # for ix, rec in dfrssi_host_scan.groupby(["address"]):
                dfrssi_host_scan = est_kalmann(dfrssi_host_scan, measurement_sig=2., mu_ini=None, sig=10000., y_name="rssi_host",x_name=["address","host"])
                    # kx=data[data["tag_mac"]==ix].index
                    # data.loc[kx, "rssi_host_k"] = res["k_rssi_host_mu"]
                    # data.loc[kx, "rssi_host_sig"] = res["k_rssi_host_sig"]
                dfrssi_host=dfrssi_host_scan.groupby(["address"]).max().reset_index()
                nrssi=((gateway["rssi"]-gateway["rssi_ref"]))/20/log(gateway["dist_ref"]/gateway["dist"]) #nrssi=((dfrssi_host[dfrssi_host["address"]=="0C4314F46DA1"]["k_rssi_host_mu"].values[0]-dfrssi_host[dfrssi_host["address"]=="0C4314F46E18"]["k_rssi_host_mu"].values[0]))/20/log(1.4142135623730951)*log(6.905070600652827)
                dfrssi_host["distance_host"]=gateway["dist"]*np.exp((gateway["rssi"] - dfrssi_host["k_rssi_host_mu"].values) / nrssi/20)

            #distance from 00 taken from gteway measurement
            dfanchors = pd.DataFrame.from_dict(anchors_init, orient="index").reset_index()
            address_00 = dfanchors[(dfanchors["x"] == 0) & (dfanchors["y"] == 0)]["index"].values[0]
            dataavg["dist_00"] = np.nan
            kix = dataavg[dataavg["anchor_mac"] == address_00].index
            if dfrssi_host is not None :
                dfdist0 = dataavg.loc[kix].join(dfrssi_host.set_index("address"), how="left", on="tag_mac")
                alpha=np.atan(gateway["x"]/gateway["y"])
                betha=np.cos(np.radians(dfdist0["k_azimuth_mu"]))
            if gateway["dist"]>0 and  dfrssi_host is not None :
                r=gateway["dist"]
                R=dfdist0["distance_host"]
                a=gateway["dist"] * np.sin(alpha+betha)
                dataavg.loc[kix,"dist_00"]=r * np.cos(alpha+betha)+R * np.sqrt(1-np.pow(a/R,2))
            else:
                dataavg.loc[kix, "dist_00"] = gateway["dist"]

            #calculates intersecction
            dataavg=dataavg.merge(dfanchors[["index", "x", "y","z_rot"]], left_on="anchor_mac", right_on="index", how="left")
            dataavg.drop(columns=["index"],inplace=True)
            #change to take into account anchor rotation ONLY on Z axis
            dataavg["m_k"] = np.tan(np.radians(dataavg["k_azimuth_mu"]+dataavg["z_rot"]))
            dataavg["c_k"] = -dataavg["m_k"] * dataavg["x"] + dataavg["y"]
            for i in np.unique(dataavg["anchor_mac"].values):
                for j in np.unique(dataavg["anchor_mac"].values):
                    ix=dataavg[dataavg["anchor_mac"] == i].index
                    rec_i= dataavg[dataavg["anchor_mac"]==i][["x","y","anchor_mac","tag_mac","c_k","m_k","k_azimuth_mu"]]
                    rec_j = dataavg[dataavg["anchor_mac"] == j][["x","y","anchor_mac","tag_mac","c_k","m_k","k_azimuth_mu"]]
                    rec=rec_i.reset_index().merge(rec_j.reset_index(), left_on="tag_mac", right_on="tag_mac", how="left")
                    if i!=j:
                        if j+"_x" not in dataavg.columns:
                            dataavg[j+"_x"] = np.nan
                            dataavg[j + "_y"] = np.nan
                            dataavg[j + "_r"] = np.nan

                        ixf = (np.abs(rec["m_k_x"] - rec["m_k_y"]) >= 0.6)
                        if len(ixf)>0:
                            m1=rec.loc[ixf, "m_k_x"]
                            c1=rec.loc[ixf, "c_k_x"]
                            m2 = rec.loc[ixf, "m_k_y"]
                            c2 = rec.loc[ixf, "c_k_y"]
                            xc=(c2-c1) / (m1-m2)
                            yc= m1 * (c2-c1)/(m1-m2)+c1
                            dataavg.loc[rec.loc[ixf,"index_x"].values, j+ "_x"]  = xc.values
                            dataavg.loc[rec.loc[ixf, "index_x"].values, j + "_y"] = yc.values
                            dataavg.loc[rec.loc[ixf, "index_x"].values, j + "_r"] = np.sqrt(np.pow(xc - rec.loc[ixf, "x_x"],2)+np.pow(yc - rec.loc[ixf, "y_x"],2)).values
                    else:
                        if j+"_x"  in dataavg.columns:
                            dataavg.loc[ix,i+"_x"]=np.nan
                            dataavg.loc[ix,i + "_y"] = np.nan
                            dataavg.loc[ix,i + "_r"] = np.nan
                        else:
                            dataavg[i+"_x"] = np.nan
                            dataavg[i + "_y"] = np.nan
                            dataavg[i + "_r"] = np.nan

            dpos_x=[]
            dpos_y = []
            dpos_r = []
            for ix, rec in dataavg.groupby(["tag_mac"]):
                #print(rec)
                rpos_x={"tag_mac":ix[0]}
                rpos_y = {"tag_mac": ix[0]}
                rpos_r = {"tag_mac": ix[0]}
                # for i in np.unique(dataavg["anchor_mac"].values):
                #     rpos_x[i+"_x"]=np.nan
                #     rpos_y[i + "_y"] = np.nan
                #     rpos_r[i + "_r"] = np.nan
                proc=[]
                n = len(np.unique(dataavg["anchor_mac"].values))
                for i in np.unique(dataavg["anchor_mac"].values):
                    for ik in rec.index:
                        j=rec.loc[ik,"anchor_mac"]
                        if i!=j and (i+"_"+j) not in proc:
                            proc.append(j+"_"+i)
                            proc.append(i + "_" + j)
                            rpos_x[j[8:]+"_"+i[8:] + "_x"] = rec.loc[ik, i + "_x"]
                            rpos_y[j[8:]+"_"+i[8:] + "_y"] = rec.loc[ik, i + "_y"]
                            rpos_r[j[8:]+"_"+i[8:] + "_r"] = rec.loc[ik, i + "_r"]
                            if len(proc)==n*n-n:
                                dpos_x.append(rpos_x)
                                dpos_y.append(rpos_y)
                                dpos_r.append(rpos_r)
                                break

            dfpos_x=pd.DataFrame.from_dict(dpos_x)
            dfpos_x["median"] = dfpos_x[dfpos_x.filter(like='_x').notnull()].median(axis=1)
            xfg = ~dfpos_x[dfpos_x.filter(like='_x').notnull()].gt(dfpos_x["median"] + val_outliers, axis=0)
            xfl = ~dfpos_x[dfpos_x.filter(like='_x').notnull()].lt(dfpos_x["median"] - val_outliers, axis=0)
            dfpos_x["min_value"]=np.nan
            dfpos_x["goods"] = np.nan
            dfpos_x["std"] = np.nan
            for ix in dfpos_x.index:
                datax = dfpos_x[dfpos_x[(xfg & xfl)].filter(like='_x').notnull()].loc[ix].dropna().values
                dfpos_x.loc[ix, "goods"]=len(datax)
                dfpos_x.loc[ix, "std"]=np.std(datax) if len(datax)>1 else np.nan
                if len(datax)>0:
                    result=minimize(quadratic_error, x0=dfpos_x.loc[ix,"median"], args=(datax,))
                    if result.success:
                        dfpos_x.loc[ix,"min_value"] = result.x[0]

            dfpos_y = pd.DataFrame.from_dict(dpos_y)
            dfpos_y["median"] = dfpos_y[dfpos_y.filter(like='_y').notnull()].median(axis=1)
            xfg = ~dfpos_y[dfpos_y.filter(like='_y').notnull()].gt(dfpos_y["median"] + val_outliers, axis=0)
            xfl = ~dfpos_y[dfpos_y.filter(like='_y').notnull()].lt(dfpos_y["median"] - val_outliers, axis=0)
            dfpos_y["min_value"]=np.nan
            dfpos_y["goods"] = np.nan
            dfpos_y["std"] = np.nan
            for ix in dfpos_y.index:
                datay = dfpos_y[dfpos_y[(xfg & xfl)].filter(like='_y').notnull()].loc[ix].dropna().values
                dfpos_y.loc[ix, "goods"]=len(datay)
                dfpos_y.loc[ix, "std"] = np.std(datay) if len(datay)>1 else np.nan
                if len(datay)>0:
                    result=minimize(quadratic_error, x0=dfpos_y.loc[ix,"median"], args=(datay,))
                    if result.success:
                        dfpos_y.loc[ix,"min_value"] = result.x[0]


            dfpos_r = pd.DataFrame.from_dict(dpos_r)
            dfpos_r["median"] = dfpos_r[dfpos_r.filter(like='_r').notnull()].median(axis=1)
            xfg = ~dfpos_r[dfpos_x.filter(like='_r').notnull()].gt(dfpos_r["median"] +val_outliers, axis=0)
            xfl = ~dfpos_r[dfpos_x.filter(like='_r').notnull()].lt(dfpos_r["median"] -val_outliers, axis=0)
            dfpos_r["min_value"]=np.nan
            dfpos_r["goods"] = np.nan
            dfpos_r["std"] = np.nan
            for ix in dfpos_r.index:
                datar = dfpos_r[dfpos_r[(xfg & xfl)].filter(like='_r').notnull()].loc[ix].dropna().values
                dfpos_r.loc[ix, "goods"]=len(datar)
                dfpos_r.loc[ix, "std"] = np.std(datar) if len(datar)>1 else np.nan
                if len(datar)>0:
                    result=minimize(quadratic_error, x0=dfpos_r.loc[ix,"median"], args=(datar,))
                    if result.success:
                        dfpos_r.loc[ix,"min_value"] = result.x[0]

        except Exception as e:
            print(e)
            scan_control["ScanError"] = True
            # scan_control["redo_scan"] = False
            # scan_control["tag_re_scan"] = []
            scan_control["scan_loop"]=scan_control["scan_loop"]+1
            print("-->>Location Error - Check MQTT Servers!!")

        if dfpos_x is not None and dfpos_y is not None and not scan_control["ScanError"]:
            redo_x = dfpos_x[dfpos_x["goods"]<2]["tag_mac"].values
            redo_y = dfpos_y[dfpos_y["goods"] < 2]["tag_mac"].values

            tag_re_scan=list(redo_x)
            tag_re_scan.extend(redo_y)
            tags = dataavg["tag_mac"].unique()
            tags_missed=list(filter(len, [x if x not in tags else "" for x in scan_control["tag_re_scan"]]))
            scan_control["tag_re_scan"] = list(np.unique(tag_re_scan))
            scan_control["tag_re_scan"].extend(tags_missed)
            tags_ok = list(filter(len, [x if x not in scan_control["tag_re_scan"] else "" for x in tags]))
            #missed if filter is not []
            scan_control["tag_re_scan"].extend([x for x in ["" if x in tags_ok else x for x in tagfilter] if x != ""])
            print("tag_re_scan {0}".format(scan_control["tag_re_scan"]))
            app.print_statuslog("tag_re_scan {0}".format(scan_control["tag_re_scan"]))
        else:
            if not scan_control["ScanError"]:scan_control["scan_loop"] = scan_control["scan_loop"] + 1
            print("-->>Location Error - Check MQTT Servers!!")
            # scan_control["redo_scan"] = False
            # scan_control["tag_re_scan"]=[]
            scan_control["ScanError"]=True
            app.print_statuslog("-->>Location Error - Check MQTT Servers!!")
        if len(scan_control["tag_re_scan"])>0 and scan_control["scan"]<MAX_RESCAN and scan_control["scan_loop"]<MAX_RESCAN+1:
            if scan_control["scan"]==0:
                scan_control["scan_data"]=[]
                scan_control["tags"]=[]
                scan_control["tag_re_scan_log"]=[]
                scan_control["redo_scan"] = True
                scan_control["scan_loop"]=0
                print("Starting loop scan....")
                app.print_statuslog("Starting loop scan....")
            if scan_control["ScanError"]:
                scan_control["ScanError"] = False
            else:
                scan_control["scan"]=scan_control["scan"]+1
                scan_control["tags"].append(tags_ok)
                scan_control["tag_re_scan_log"].append(scan_control["tag_re_scan"])
                scan_control["scan_data"].append({"n":scan_control["scan"]-1,"dfpos_x":dfpos_x, "dfpos_y" : dfpos_y, "dfpos_r": dfpos_r, "dataavg":dataavg, "dfrssi_host":dfrssi_host, "resdf":resdf,"data_corravg":data_corravg, "data_pos":data_pos })
        else:
            #dfrssi_host = None# ADDED BY RAQUEL REMOVE
            try:
                if scan_control["scan"]>0:
                    ini=False
                    ini_concat=False
                    for i in range(len(scan_control["scan_data"])):
                        try:
                            if len(scan_control["tags"][i]) > 0:
                                dfpos_x_1=scan_control["scan_data"][i]["dfpos_x"]
                                dfpos_y_1 = scan_control["scan_data"][i]["dfpos_y"]
                                dfpos_r_1 = scan_control["scan_data"][i]["dfpos_r"]
                                dataavg_1 = scan_control["scan_data"][i]["dataavg"]
                                dfrssi_host_1 = scan_control["scan_data"][i]["dfrssi_host"]
                                resdf_1 = scan_control["scan_data"][i]["resdf"]
                                data_corravg_1 = scan_control["scan_data"][i]["data_corravg"]
                                data_pos_1 = scan_control["scan_data"][i]["data_pos"]
                                if not ini:ini=len(scan_control["tags"][i])>0

                            if (not scan_control["ScanError"]==True and ini ) or (ini_concat and len(scan_control["tags"][i])>0):
                                dfpos_x =pd.concat([dfpos_x,dfpos_x_1[dfpos_x_1['tag_mac'].isin(scan_control["tags"][i])]], ignore_index=True)
                                dfpos_y =pd.concat([ dfpos_y,dfpos_y_1[dfpos_y_1['tag_mac'].isin(scan_control["tags"][i])]], ignore_index=True)
                                dfpos_r =pd.concat([ dfpos_r,dfpos_r_1[dfpos_r_1['tag_mac'].isin(scan_control["tags"][i])]], ignore_index=True)
                                dataavg =pd.concat([ dataavg,dataavg_1[dataavg_1['tag_mac'].isin(scan_control["tags"][i])]], ignore_index=True)
                                if dfrssi_host_1 is not None:dfrssi_host =pd.concat([ dfrssi_host,dfrssi_host_1[dfrssi_host_1['address'].isin(scan_control["tags"][i])]], ignore_index=True)
                                resdf =pd.concat([ resdf,resdf_1[resdf_1['tag_mac'].isin(scan_control["tags"][i])]], ignore_index=True)
                                if data_corravg is not None and data_corravg_1 is not None and data_corravg_1.shape[0]>0:
                                    data_corravg =pd.concat([ data_corravg,data_corravg_1[data_corravg_1['tag_mac'].isin(scan_control["tags"][i])]], ignore_index=True)
                                else:
                                    if data_corravg_1 is not None:
                                        data_corravg=data_corravg_1[data_corravg_1['tag_mac'].isin(scan_control["tags"][i])]
                                if data_pos is not None and data_pos_1 is not None and data_pos_1.shape[0]>0 :
                                    data_pos =pd.concat( [data_pos,data_pos_1[data_pos_1['tag_mac'].isin(scan_control["tags"][i])]], ignore_index=True)
                                else:
                                    if data_pos_1 is not None and data_pos_1.shape[0]>0:
                                        data_pos = data_pos_1[data_pos_1['tag_mac'].isin(scan_control["tags"][i])]
                                ini_concat=True

                            elif scan_control["ScanError"]==True and ini and not ini_concat:
                                dfpos_x = dfpos_x_1[dfpos_x_1['tag_mac'].isin(scan_control["tags"][i])]
                                dfpos_y = dfpos_y_1[dfpos_y_1['tag_mac'].isin(scan_control["tags"][i])]
                                dfpos_r = dfpos_r_1[dfpos_r_1['tag_mac'].isin(scan_control["tags"][i])]
                                dataavg = dataavg_1[dataavg_1['tag_mac'].isin(scan_control["tags"][i])]
                                if dfrssi_host_1 is not None: dfrssi_host = dfrssi_host_1[dfrssi_host_1['address'].isin(scan_control["tags"][i])]
                                resdf = resdf_1[resdf_1['tag_mac'].isin(scan_control["tags"][i])]
                                data_corravg=data_corravg_1[data_corravg_1['tag_mac'].isin(scan_control["tags"][i])] if data_corravg_1 is not None else None
                                if data_pos_1 is not None and data_pos_1.shape[0]>0 :
                                    data_pos=data_pos_1[data_pos_1['tag_mac'].isin(scan_control["tags"][i])]
                                else:
                                    data_pos=None
                                ini_concat = True
                        except Exception as e:
                            print(e)

                if dfpos_x is not None: dfpos_x = dfpos_x.sort_values(by=['tag_mac'])
                if dfpos_y is not None:dfpos_y = dfpos_y.sort_values(by=['tag_mac'])
                if dfpos_r is not None:dfpos_r = dfpos_r.sort_values(by=['tag_mac'])
                if dataavg is not None:dataavg = dataavg.sort_values(by=['anchor_mac','tag_mac'])
                if dfrssi_host is not None:dfrssi_host = dfrssi_host.sort_values(by=['address'])
                if resdf is not None:resdf = resdf.sort_values(by=['tag_mac'])
                if data_corravg is not None: data_corravg = data_corravg.sort_values(by=['anchor_mac','tag_mac'])
                if data_pos is not None: data_pos = data_pos.sort_values(by=['tag_mac']) if data_pos.shape[0]>0 else data_pos

                if resdf is not None:
                    if resdf.shape[0]>0:
                        resdf = resdf.set_index("tag_mac").merge(dfpos_x.set_index("tag_mac")["min_value"], on="tag_mac")
                        resdf.rename(columns={'min_value': 'x'},inplace=True)
                        resdf = resdf.merge(dfpos_x.set_index("tag_mac")["std"], on="tag_mac")
                        resdf.rename(columns={'std': 'x_std'}, inplace=True)

                        resdf = resdf.merge(dfpos_y.set_index("tag_mac")["min_value"], on="tag_mac")
                        resdf.rename(columns={'min_value': 'y'}, inplace=True)
                        resdf = resdf.merge(dfpos_y.set_index("tag_mac")["std"], on="tag_mac")
                        resdf.rename(columns={'std': 'y_std'}, inplace=True)
                        resdf["std"]=np.sqrt(np.pow(resdf["x_std"], 2) + np.pow(resdf["y_std"], 2))

                        resdf = resdf.merge(dataavg[["tag_mac", "samples"]].groupby(["tag_mac"]).min().reset_index(),on="tag_mac")
                        resdf.rename(columns={'samples': 'samples_min'}, inplace=True)
                        resdf = resdf.merge(dataavg[["tag_mac", "samples"]].groupby(["tag_mac"]).sum().reset_index(),on="tag_mac")
                        resdf.rename(columns={'samples': 'samples_total'}, inplace=True)

                        resdf=resdf.reset_index()
                    else:
                        resdf= pd.DataFrame(columns=["tag_mac","out_prob","out_prob_k","result","x","y"])
                else:
                    resdf = pd.DataFrame(columns=["tag_mac", "out_prob", "out_prob_k", "result", "x", "y"])
                print(resdf)
                scan_control["redo_scan"]=False
                scan_control["tag_re_scan"]=[]
                scan_control["scan"]=0
                scan_control["tags"] = []
                print(dfrssi_host)
                if os.path.exists(file_path_angle):
                    # Delete the file
                    os.remove(file_path_angle)
                    print(f"File {file_path_angle} has been deleted.")
                if os.path.exists(file_path_angle_raw):
                    # Delete the file
                    os.remove(file_path_angle_raw)
                    print(f"File {file_path_angle_raw} has been deleted.")
                if os.path.exists(file_path_correction):
                    # Delete the file
                    os.remove(file_path_correction)
                    print(f"File {file_path_correction} has been deleted.")
                if os.path.exists(file_path_correction_raw):
                    # Delete the file
                    os.remove(file_path_correction_raw)
                    print(f"File {file_path_correction_raw} has been deleted.")
                if os.path.exists(file_path_position_raw):
                    # Delete the file
                    os.remove(file_path_position_raw)
                    print(f"File {file_path_position_raw} has been deleted.")

                if os.path.exists(file_path_xposition_raw):
                    # Delete the file
                    os.remove(file_path_xposition_raw)
                    print(f"File {file_path_xposition_raw} has been deleted.")
                if os.path.exists(file_path_yposition_raw):
                    # Delete the file
                    os.remove(file_path_yposition_raw)
                    print(f"File {file_path_yposition_raw} has been deleted.")
                if os.path.exists(file_path_rposition_raw):
                    # Delete the file
                    os.remove(file_path_rposition_raw)
                    print(f"File {file_path_rposition_raw} has been deleted.")


                if data_corravg is not None:
                    data_corravg.to_csv(file_path_correction, index=False)
                if dataavg is not None:
                    dataavg.to_csv(file_path_angle, index=False)
                if data is not None:
                    data.to_csv(file_path_angle_raw, index=False)
                if data_corr is not None:
                    data_corr.to_csv(file_path_correction_raw, index=False)
                if data_pos is not None:
                    data_pos.to_csv(file_path_position_raw, index=False)

                if dfpos_x is not None:
                    dfpos_x.to_csv(file_path_xposition_raw, index=False)
                if dfpos_y is not None:
                    dfpos_y.to_csv(file_path_yposition_raw, index=False)
                if dfpos_r is not None:
                    dfpos_r.to_csv(file_path_rposition_raw, index=False)
            except Exception as e:
                print(e)
                scan_control["redo_scan"] = False
                scan_control["tag_re_scan"] = []
                scan_control["scan"] = 0
                scan_control["tags"] = []
                cancel_process=True
                app.print_statuslog("----------------- Location exception error 1 - canceling.... -----------------------")
    except Exception as e:
        print(e)
        scan_control["redo_scan"] = False
        scan_control["tag_re_scan"] = []
        scan_control["scan"] = 0
        scan_control["tags"] = []
        cancel_process=True
        app.print_statuslog("----------------- Location exception error 2 - canceling.... -----------------------")
    return resdf,dataavg,data_posavg,scan_control,cancel_process


#---------------------------------------------------------------------#
# END  Scan Location
#---------------------------------------------------------------------#



#---------------------------------------------------------------------#
#               Main Scan BLE
#---------------------------------------------------------------------#
import signal
def terminate_mqttservers(srv_antenna_anchor):
    try:
        for ix in srv_antenna_anchor.keys():
            if srv_antenna_anchor[ix]["status"]:
                print(f"terminate_process(process) {ix}")
                process = srv_antenna_anchor[ix]["process"]
                if process is not None:
                    process.send_signal(signal.SIGINT)
                    print(f"Sent Ctrl+C (SIGINT) to process anchor {ix}.")
                    process.send_signal(signal.SIGINT)
                    print(f"Sent Ctrl+C (SIGINT) to process anchor {ix}.")
                # # Terminate the process if needed
                # terminate_process(process)
                monitor_thread = srv_antenna_anchor[ix]["monitor_thread"]
                if monitor_thread is not None:
                    # Wait for the monitor thread to finish
                    monitor_thread.join()
                    # Check the final status of the process
                #exit_code = process.poll()
                #print(f"Process finished with exit code {exit_code}")
                srv_antenna_anchor[ix]["status"] = False
    except Exception as e:
        print(e)
    return srv_antenna_anchor

def checkmqttservers(srv_antenna_anchor):
    # chck servers
    for ix in srv_antenna_anchor.keys():
        cmdline = srv_antenna_anchor[ix]["cmdline"]
        if srv_antenna_anchor[ix]["status"] is None or srv_antenna_anchor[ix]["status"] is True:
            bat_file = srv_antenna_anchor[ix]["bat_file"]
            if cmdline == "":
                cmdline = ['start', '/MIN','cmd', '/c', bat_file]
            res, process=is_batch_file_running(cmdline)
            if res:
                # print(f"{bat_file} is currently running.")
                srv_antenna_anchor[ix]["status"] = True
                srv_antenna_anchor[ix]["process"] =process
            else:
                print(f"{bat_file} is not running.")
                srv_antenna_anchor[ix]["status"] = False

    for ix in srv_antenna_anchor.keys():
        if not srv_antenna_anchor[ix]["status"] and srv_antenna_anchor[ix]["enabled"]:
            try:
                srv_antenna_anchor[ix]["status"] = True
                print(f"Restarting {ix}")
                bat_file = srv_antenna_anchor[ix]["bat_file"]
                process, monitor_thread, cmdline = run_bat_file(bat_file, ix, srv_antenna_anchor)
                srv_antenna_anchor[ix]["process"] = process
                srv_antenna_anchor[ix]["monitor_thread"] = monitor_thread
                srv_antenna_anchor[ix]["cmdline"] = cmdline
                time.sleep(5)
            except Exception as e:
                srv_antenna_anchor[ix]["status"] = False
                print(e)

    return srv_antenna_anchor

def mergelocation(resdf,df_res, scan_columnIds, filter=False):
    try:
        if resdf is not None:
            if not filter:
                try:
                    if "x" in list(df_res.columns) or "y" in list(df_res.columns):
                        cols = [x for x in list(df_res.columns) if x not in ['x', 'y']]
                        df_res=df_res[cols]
                    if "x" in list(resdf.columns) and "y" in list(resdf.columns):

                        temp_values = list(resdf['tag_mac'].values)
                        if len(temp_values) > 0:
                            if len(temp_values[0]) > 30:
                                resdf['tag_mac_strip'] = temp_values
                            else:
                                resdf['tag_mac_strip'] = [
                                    x[0:2] + ":" + x[2:4] + ":" + x[4:6] + ":" + x[6:8] + ":" + x[8:10] + ":" + x[10:12] for x in
                                    resdf['tag_mac'].values]
                            df_res = df_res.merge(resdf.set_index("tag_mac_strip")[["x", "y", "result"]],  left_on="mac", right_on="tag_mac_strip", how="left")
                            df_res = df_res[scan_columnIds]
                            #['mac', 'name', 'tag_id', 'asset_id', 'certificate_id', 'type', 'expiration_date', 'color',
                            # 'series', 'asset_images_file_extension', 'read_nfc', 'x', 'y']]

                        # df_res.rename(columns={"x_y": "x", "y_y": "y"}, inplace=True)
                            df_res['x'] = df_res['x'].apply(lambda x: '{:,.1f}'.format(x))
                            df_res['y'] = df_res['y'].apply(lambda x: '{:,.1f}'.format(x))
                            df_res.rename(columns={"result": "in_out"})

                        else:
                            pass
                    else:
                        df_res["x"] = np.nan
                        df_res["y"] = np.nan
                        df_res["in_out"] = np.nan
                except Exception as e:
                    print(e)
            else:
                #priority to current values
                try:
                    if "x" in list(resdf.columns) and "y" in list(resdf.columns):
                        resdf['tag_mac_strip'] = [
                            x[0:2] + ":" + x[2:4] + ":" + x[4:6] + ":" + x[6:8] + ":" + x[8:10] + ":" + x[10:12] for x in
                            resdf['tag_mac'].values]
                        df_res = df_res.merge(resdf.set_index("tag_mac_strip")[["x", "y"]], left_on="mac", right_on="tag_mac_strip", how="left")
                        df_res.loc[
                            df_res[(np.isnan(df_res["x_y"]) == False) | (np.isnan(df_res["y_y"]) == False)].index, "x_x"] = \
                        df_res.loc[
                            df_res[(np.isnan(df_res["x_y"]) == False) | (np.isnan(df_res["y_y"]) == False)].index, "x_y"]
                        df_res.loc[
                            df_res[(np.isnan(df_res["x_y"]) == False) | (np.isnan(df_res["y_y"]) == False)].index, "y_x"] = \
                        df_res.loc[
                            df_res[(np.isnan(df_res["x_y"]) == False) | (np.isnan(df_res["y_y"]) == False)].index, "y_y"]
                        df_res.rename(columns={"x_x": "x", "y_x": "y"}, inplace=True)
                        df_res = df_res[
                            ['mac', 'name', 'tag_id', 'asset_id', 'certificate_id', 'type', 'expiration_date', 'color',
                             'series', 'asset_images_file_extension', 'read_nfc', 'x', 'y']]
                        df_res['x'] = df_res['x'].apply(lambda x: '{:,.1f}'.format(x))
                        df_res['y'] = df_res['y'].apply(lambda x: '{:,.1f}'.format(x))
                    else:
                        df_res["x"] = np.nan
                        df_res["y"] = np.nan
                except Exception as e:
                    print(e)
        else:
            df_res["x"] = np.nan
            df_res["y"] = np.nan

    except Exception as e:
        print(e)
    return df_res

async def main():
    """Scan for devices."""

    global keep_mqtt_on
    global Stop_collecting
    global datadf
    global janhors_processed
    global datadf_pos
    global datadf_corr
    global jmpos_processed
    global jang_corr_processed
    # global rssi_host_scan
    global scanstarted
    global discover_rssi
    global discover_rssi_collect
    global devices_processed
    global scan_control
    global scan_control
    global srv_antenna_anchor
    global MaxTags
    global scan_mac_filter
    global update_mac_filter
    global startCTE_address_filter
    global val_outliers
    global directo
    global app_page_configuration
    global app_localpath
    global directory

    datadf = {}
    janhors_processed = []
    datadf_pos = {}
    jmpos_processed = []
    datadf_corr = {}
    jang_corr_processed = []
    startup_firstscan=True
    # app.run()
    # Run Flask app in a separate thread


    # flask_thread = Thread(target=app.run_flask_app)
    # flask_thread.start()
    # app.print_statuslog("Starting...")

    # for ix in char_uuid.keys():
    #     if char_uuid[ix]["id"] in char_uuid_nfc:
    #         char_uuid[ix]["NFC"] = True
    mqttclient = None
    #scan_location()
    if use_MQTT:
        mqttclient=run_mqtt()
        thread = Thread(target = threaded_function, kwargs={'client':mqttclient},daemon=True)
        thread.start()
    # thread.join()
    print("MQTT thread stared")
    time_process=None

    # scanner = BleakScanner()
    # scanner.register_detection_callback(device_found)



    #time.sleep(5)
    print("MQTT paused")
    if use_MQTT:
        if not keep_mqtt_on : mqttclient.loop_stop()

    webcancelprocess = False

    scan_control = {"tag_re_scan": [], "scan": 0, "redo_scan":False, "scan_loop":0}
    action=""

    bscanner = bldtag.boldscanner(disableCTE_duringlocation=disableCTE_duringlocation,
                                  keepactive_all_CTE_during_location=keepactive_all_CTE_during_location,
                                    use_MQTT =use_MQTT, mqttclient = mqttclient, keep_mqtt_on = keep_mqtt_on,
                                    wait_for_mqtt_angles = wait_for_mqtt_angles, CTE_Wait_Time_prescan = CTE_Wait_Time_prescan, CTE_Wait_Time = CTE_Wait_Time,webapp=app,directory=directory)
    await bscanner.discover_rssi_start()
    # webapp initialization
    app.columnIds=list(bscanner.tags.gatewaydb.csv_row.keys())#bscanner.tags.gatewaydb.scan_columnIds
    # app.cloud_columnIds = bscanner.tags.gatewaydb.cloud_scan_columnIds
    # app.cloud_csv_row =bscanner.tags.gatewaydb.cloud_csv_row
    app.localpath = directory + "/"

    # app.columnIds_base = bscanner.tags.gatewaydb.scan_columnIds
    # app.cloud_columnIds_base = bscanner.tags.gatewaydb.cloud_scan_columnIds
    # app.cloud_csv_row_base = bscanner.tags.gatewaydb.cloud_csv_row
    # app.localpath_base = directory + "/"

    # app.columnIds_detail = bscanner.tags.gatewaydb.scan_det_columnIds
    # app.cloud_columnIds_detail = bscanner.tags.gatewaydb.cloud_scan_columnIds
    # app.cloud_csv_row_detail = bscanner.tags.gatewaydb.cloud_csv_row
    # app.localpath_detail = directory + "/detail/"

    # app.columnIds_configuration = bscanner.tags.gatewaydb.scan_cfg_columnIds
    # app.cloud_columnIds_configuration = bscanner.tags.gatewaydb.cloud_scan_columnIds
    # app.cloud_csv_row_configuration = bscanner.tags.gatewaydb.cloud_csv_row
    # app.localpath_configuration = directory + "/configuration/"

    app.location_cvs_columnIds = bscanner.tags.gatewaydb.location_cvs_columnIds
    app.location_cvs_row = bscanner.tags.gatewaydb.location_cvs_row
    app.sync_init()

    app.anchors_init = anchors_init
    app.readscanfile()

    # app.get_data()

    flask_thread = Thread(target=app.run_flask_app)
    flask_thread.start()

    app.print_statuslog("Starting [TESTING RENAME]...")
    app.print_statuslog("Scanning BoldTags\n")
    # time.sleep(5)

    # await bscanner.discover_rssi_start()
    # time.sleep(5)
    #
    #BAC if i do not start this scanner the bscanner does not discover devices!!!!! TODO
    # if discover_rssi:
    #     await scanner.start()

    # n=0
    # while (n<20):
    #     n=n+1
    #     app.print_statuslog(".",addLFCR=False if n>1 else True)
    #     time.sleep(1)
    # app.print_statuslog("\nFinished Scanning BoldTags...")
    #
    # # await bscanner.discover_rssi_stop()
    # rssi_host_scan=bscanner.get_rssi_host_scan()
    # app.print_statuslog("BoldTag detected {}".format(bscanner.rssi_tag_scan))
    app.set_rssi_tag_scan(bscanner.rssi_tag_scan,True)

    while True:
        app.set_rssi_tag_scan(bscanner.rssi_tag_scan,False)
        scan_mac_banned_read=pd.DataFrame()
        if os.path.exists(directory+"/scan_mac_banned.csv"):
            scan_mac_banned_read=pd.read_csv(directory + "/scan_mac_banned.csv")
        if scan_mac_banned_read.shape[0]>0:
            scan_mac_banned=scan_mac_banned_read.values[0]
        else:
            scan_mac_banned=[]

        # #check if MQTTT locators and server are running. If not start them
        if action == "LOCATION" : srv_antenna_anchor=checkmqttservers(srv_antenna_anchor)

        #check status of the web API - Update type of data selected by API (page_configuration)
        app.checkstatus()
        app_page_configuration=app.page_configuration
        app_localpath=app.localpath
        #adjust working directory and data columns base on page_configuration
        directory=app_localpath[:-1]
        app_scan_columnIds=app.columnIds

        # if action == "LOCATION":
        #     mqttsrv_status=True
        #     for ix in srv_antenna_anchor.keys():
        #         mqttsrv_status=srv_antenna_anchor[ix]["status"] & mqttsrv_status
        #     if not mqttsrv_status:
        #         for ix in srv_antenna_anchor.keys():
        #             if not srv_antenna_anchor[ix]["status"] and srv_antenna_anchor[ix]["enabled"]:
        #                 print(
        #                     "MQTT ANTENNAS POLLING SERVER NOT RUNINNG!!!!!!!!!!!!!!!!!!!!!!!-------------------->>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> {0}".format(srv_antenna_anchor[ix]["bat_file"]))
        #             if srv_antenna_anchor[ix]["enabled"]:
        #                 print("Anchor {0} is disabled".format(srv_antenna_anchor[ix]["bat_file"]))

        if action == "LOCATION" and len(scan_control["tag_re_scan"])>0  and scan_control["redo_scan"]:
            #in case the loop is for a LOCATION redo
            scannaddress = []
            devprocessed = []
            idupdate = []
            dfupdate = None
            doscan=True
            startCTE_address_filter = scan_control["tag_re_scan"]
            redo_location=True
        else:
            redo_location = False
            #Start normal operation requestd by API
            scan_control = {"tag_re_scan": [], "scan": 0, "redo_scan":False, "scan_loop":0}

            csv_read_data = []
            devprocessed=[]
            idupdate = []
            # Specify the directory path
            # directory = "c:/tgspoc"

            # Check if the directory exists
            if not os.path.exists(directory):
                # Create the directory if it does not exist
                os.makedirs(directory)
                print(f"Directory {directory} created.")
            else:
                print(f"Directory {directory} already exists.")
            doscan = False
            # Specify the CSV file path
            file_path = directory+"/scan.csv"
            file_path_location = directory + "/scan_location.csv"
            file_path_location_copy = directory +"/scan_location_copylastlocation.csv"
            file_path_position = directory + "/scan_position.csv"
            file_path_position_raw = directory + "/scan_position_raw.csv"
            file_path_angle = directory + "/scan_angles.csv"
            file_path_angle_raw=directory + "/scan_angles_raw.csv"
            file_path_correction = directory + "/scan_correction.csv"
            file_path_correction_raw = directory + "/scan_correction_raw.csv"
            file_path_xposition_raw = directory + "/scan_xpositions.csv"
            file_path_yposition_raw = directory + "/scan_ypositions.csv"
            file_path_rposition_raw = directory + "/scan_rpositions.csv"
            file_path_lastscan=directory+"/scan_copylastscan.csv"
            scancsv=None
            action=None
            # Check if the file exists
            if os.path.exists(file_path):
                # Read the CSV file using the built-in csv module
                scancsv=pd.read_csv(file_path)
                print(f"File {file_path} exist.")

            else:
                print(f"File {file_path} does not exist.")


                if "READ" in actions_filter:
                    print("Doing Scanning data...")
                    doscan=True
                    action = "READ"

            if not os.path.exists(file_path_location):
                print(f"File {file_path_location} does not exist.")


                if "LOCATION" in actions_filter:
                    print("Doing Location ...")
                    doscan=True
                    action = "LOCATION"

            file_path_update = directory+"/scan_update.csv"
            file_path_update_read= directory+"/scan_update_read.csv"
            file_path_update_error= directory+"/scan_update_error.csv"
            dfupdate=None
            # Check if the file exists
            update_mac_filter=[]
            if os.path.exists(file_path_update):
                try:
                    # Read the CSV file using the built-in csv module
                    # scan_updatecsv=pd.read_csv(file_path_update)
                    if "UPDATE" in actions_filter:
                        action = "UPDATE"
                        doscan = True
                        print("Doing Updating and updating data...")
                    dfupdate=pd.read_csv(file_path_update)
                    dfupdate=pd.read_csv(file_path_update)
                    dfupdate_read=dfupdate.copy()
                    idupdate=dfupdate['mac'].values
                    update_mac_filter=[x.replace(":","") for x in idupdate]
                    recupdate = dfupdate.copy()

                except Exception as e:
                    print("file reading error: {0}".format(file_path_update))
                    print(e)
            else:
                print(f"File {file_path_update} does not exist.")

            # await scanner.start()
            # await asyncio.sleep(1.0)
            # await scanner.stop()
            # try:  # used try so that if user pressed other than the given key error will not be shown
            #     if keyboard.is_pressed('q'):  # if key 'q' is pressed
            #         print('You Pressed A Key!')
            #         break  # finishing the loop
            # except:
            #     break
            scannaddress = []

            nscan=0

        time_process=time.time()
        if app.webcancel and not doscan:
            webcancelprocess = True

        if app.page_selected == "page_configuration_detail":
            uuid_data_type_filter = "detail"
        elif app.page_selected == "page_configuration_configuration":
            uuid_data_type_filter = "configuration"
        else:
            uuid_data_type_filter = "base"

        #check if MQTTT locators and server are running. If not start them
        if action == "LOCATION" :  srv_antenna_anchor=checkmqttservers(srv_antenna_anchor)

        if action == "LOCATION":
            mqttsrv_status=True
            for ix in srv_antenna_anchor.keys():
                mqttsrv_status=srv_antenna_anchor[ix]["status"] & mqttsrv_status
            if not mqttsrv_status:
                for ix in srv_antenna_anchor.keys():
                    if not srv_antenna_anchor[ix]["status"] and srv_antenna_anchor[ix]["enabled"]:
                        print(
                            "MQTT ANTENNAS POLLING SERVER NOT RUNINNG!!!!!!!!!!!!!!!!!!!!!!!-------------------->>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> {0}".format(srv_antenna_anchor[ix]["bat_file"]))
                    if srv_antenna_anchor[ix]["enabled"]:
                        print("Anchor {0} is disabled".format(srv_antenna_anchor[ix]["bat_file"]))

        if doscan:
            #start tag scanning for requstd operation
            read_nfc_done = False
            scan_mac_filter=app.mac_filter

            scan_mac_filter_address = []
            if len(scan_mac_filter)>0:
                # if (len(scan_mac_filter[0].split("-"))>1):
                #     kaux=""
                #     for k in scan_mac_filter:
                #         for mk in k.split("-"):
                #             if len(kaux)>0:
                #                 kaux =kaux+"-" + [":".join( [scan_mac_filter[0][x] + scan_mac_filter[0][x + 1] for x in range(0, len(mac), 2)]) for mac in [mk]][0]
                #             else:
                #                 kaux=[":".join([scan_mac_filter[0][x] + scan_mac_filter[0][x + 1] for x in range(0, len(mac), 2)]) for mac in [mk]][0]
                #         scan_mac_filter_address.append(kaux)
                if len(scan_mac_filter[0])>30:
                    scan_mac_filter_address = scan_mac_filter
                else:
                    scan_mac_filter_address=[":".join([scan_mac_filter[0][x]+scan_mac_filter[0][x+1] for x in range(0,len(mac),2)]) for mac in scan_mac_filter]

            startCTE_address_filter=app.mac_filter if len(scan_control["tag_re_scan"])==0 else scan_control["tag_re_scan"]
            if len(startCTE_address_filter) >0 : MaxTags=len(startCTE_address_filter)
            if len(scan_mac_filter) > 0: MaxTags = len(scan_mac_filter)
            if dfupdate is not None: scan_mac_filter_address.extend(list(dfupdate["mac"].values))
            app.print_statuslog(f'action: {doscan}')
            service=None
            # rssi_host_scan={}
            scanstarted=True
            bscanner.rssi_host_scan_reset=True


            devcount=0
            myDevice = None
            myDevice_1 = None
            nscan=0

            #MQTT AoA scaning initialization

            init_location=False
            start_mqtt=True
            if discover_rssi:
                # discover_rssi_start=True
                bscanner.discover_rssi_collect=True
                # await scanner.start()
                # await bscanner.discover_rssi_start()


                #await scanner.stop()
            devices_processed=[]
            scannaddress_trim=[]

            scan_parameters=None
            try:
                scan_parameters=app.scan_parameters
            except Exception as e:
                print(e)
            if scan_parameters is not None:
                MaxScan=scan_parameters["maximum_retries"]
                param_keep_data= scan_parameters["keep_data"]
                param_scan_new_tags= scan_parameters["scan_new_tags"]
                param_enable_disable_tags= scan_parameters["enable_disable_tags"]

                scan_max_retry= scan_parameters["maximum_retries"]
                scan_max_scans= scan_parameters["scan_max_scans"]
                connect_max_retry= scan_parameters["connect_max_retry"]
                connect_timeout= scan_parameters["connect_timeout"]
                max_BoldTags= scan_parameters["max_BoldTags"]
                timeout_scanner= 15 #scan_parameters["timeout_scanner"]
            while (nscan < MaxScan and len(scannaddress) <MaxTags and not (sum([0 if x in scannaddress_trim else 1 for x in startCTE_address_filter])==0 and len(startCTE_address_filter)>0)
                   and not (sum([0 if x in scannaddress_trim else 1 for x in scan_mac_filter])==0 and len(scan_mac_filter)>0) #not ((len(scan_mac_filter)>0) and (len(scannaddress)==len(scan_mac_filter)))
                    and not (sum([0 if x in scannaddress_trim else 1 for x in update_mac_filter])==0 and len(update_mac_filter)>0)):  #((len(update_mac_filter)>0) and (len(scannaddress)==len(update_mac_filter)))):
                #srv_antenna_anchor = checkmqttservers(srv_antenna_anchor)
                #await asyncio.sleep(1.0)
                if app.webcancel:
                    webcancelprocess = True
                    break

                if action == "READ" or action == "UPDATE":
                    if not redo_location and nscan==0:
                        try:
                            #TODO implement when multiple BLE adapters are implemented , otherwise multople scans wull disconnect connected devicesin previous scanns
                            scan_max_scans=1
                            scan_max_retry=1
                            timeout_scanner=15
                            scan_mac_banned=[]
                            max_BoldTags=10000
                            connect_timeout=25
                            new_tags,existing_tags=await bscanner.scan_tags(connect=True,max_retry=scan_max_retry, max_scans=scan_max_scans,
                                                                            max_tags=max_BoldTags,scan_mac_banned=scan_mac_banned,scan_mac_filter_address=scan_mac_filter_address,
                                                                            timeout_scanner=timeout_scanner,timeout=connect_timeout,param_scan_new_tags=param_scan_new_tags)
                            # new_tags,existing_tags=await bscanner.scan_tags(connect=True,max_retry=scan_max_retry, max_scans=scan_max_scans,
                            #                                                 max_tags=max_BoldTags,scan_mac_banned=scan_mac_banned,scan_mac_filter_address=scan_mac_filter,
                            #                                                 timeout_scanner=timeout_scanner,timeout=connect_timeout,param_scan_new_tags=param_scan_new_tags)
                        except Exception as e:
                            print(e)

                        if app.webcancel:
                            webcancelprocess = True
                            break
                    if param_scan_new_tags:
                        scan_parameters["scan_new_tags"]=False
                        app.scan_parameters=scan_parameters
                        param_scan_new_tags=False
                        #         # Create asyncio tasks for each device connection
                        #         tasks = [bscanner.tags.connect(max_retry=connect_max_retry, index=x.index,timeout=connect_timeout) for x in tag_found]
                        #
                        #         # Run all connection tasks in parallel
                        #         await asyncio.gather(*tasks)
                        # except Exception as e:
                        #     print(e)
                # try:
                #     # tag_found = [x for x in bscanner.tags.items]
                #     if (bscanner.tags.limit>0):
                #         try:
                #             # res_conn={}
                #             ncount=0
                #             while ncount<4:
                #                 ncount=ncount+1
                #                 for tag in bscanner.tags.items: #tag_found:
                #                     if tag.address not in devprocessed:
                #                         res=await tag.connect(max_retry=1,timeout=15)
                #                         # res=x.connected
                #                         # res=await bscanner.tags.connect(max_retry=1, index=x.index, timeout=5)
                #                         if app.webcancel:
                #                             webcancelprocess = True
                #                             break
                #                         # res_conn[x.address] = res
                #                     # else:
                #                         # res_conn[x.address]=True
                #
                #                 if app.webcancel:
                #                     webcancelprocess = True
                #                     break
                #                 # if (all([res_conn[x] for x in res_conn.keys()]) and len(res_conn.keys())==bscanner.tags.limit): break
                #                 if bscanner.all_connected():
                #                     break
                #         except Exception as e:
                #             print(e)
                # except Exception as e:
                #     print(e)

                connect_max_retry=1;
                connect_max_retry=1
                webcancelprocess=await bscanner.check_and_reconect(devprocessed, nRetries=connect_max_retry, max_retry=connect_max_retry, timeout=15,scan_mac_filter_address=scan_mac_filter_address)
                if app.webcancel:
                    webcancelprocess = True
                    break

                nscan=nscan+1
                #devices = await scanner.discover()
                print("Scan %d" % nscan)
                app.print_statuslog("Scan %d" % nscan)

                totaldevices_general =bscanner.tags.limit # sum([0 if d.name is None else 1 if d.name.startswith("BoldTag") else 0 for d in devices])
                app.print_statuslog("Total devices found and connected: {}".format(totaldevices_general))
                dev=0


                devices_filter = []
                devices_filter.extend(startCTE_address_filter)
                devices_filter.extend(update_mac_filter)
                devices_filter.extend(scan_mac_filter)
                devices_filter = list(set(devices_filter))

                devices_filter_mac = []
                if len(devices_filter) > 0:
                    if len(devices_filter[0]) > 30:
                        devices_filter_mac = devices_filter
                    else:
                        devices_filter_mac = [ x[0:2] + ":" + x[2:4] + ":" + x[4:6] + ":" + x[6:8] + ":" + x[8:10] + ":" + x[10:12] for x in devices_filter]

                devices_connected=[]
                if bscanner.tags.limit > 0:
                    devices_connected = bscanner.tags_connected()
                if len(devices_filter) > 0:
                    # devices_filtered = [x for x in bscanner.tags.items if x.connected and x.address in devices_filter_mac]
                    devices_filtered = [address for address in devices_connected if address in devices_filter_mac]
                else:
                    devices_filtered=devices_connected
                    # devices_filtered = [x for x in bscanner.tags.items if x.connected] #[x for x in [x if ((x.name == "BoldTag")) else "" for x in bscanner.tags] if x != "" and x.connected]
                totaldevices = len(devices_filtered)
                for address in devices_filtered:
                    d=bscanner.tags.get_tag_by_address(address)
                    if app.webcancel:
                        webcancelprocess = True
                        break
                    addressdetected = [x for x in list(set([x.address if x.name == "BoldTag" else "" for x in bscanner.tags.items])) if x != ""]
                    #All detected devices were already processed - break
                    if sum([1 if x in devprocessed else 0 for x in addressdetected]) == len(addressdetected):
                        break

                    #if a filter exists and all devices in the filtrer were prosssed break the for
                    devprocessed_trim=[x.replace(":","") for x in devprocessed]
                    if action=="LOCATION":
                        if len(startCTE_address_filter)>0:
                            if sum([1 if x in devprocessed_trim else 0 for x in startCTE_address_filter]) == len(startCTE_address_filter):
                                break
                        # if len(startCTE_address_filter)>0:
                        #     if sum([1 if x in [x.replace(":","") for x in devprocessed] else 0 for x in startCTE_address_filter]) == len(startCTE_address_filter):
                        #         break

                    if action=="READ":
                        if len(scan_mac_filter)>0:
                            if sum([1 if x in devprocessed_trim else 0 for x in scan_mac_filter]) == len(scan_mac_filter):
                                break

                    if action=="UPDATE":
                        if len(update_mac_filter)>0:
                            if sum([1 if x in devprocessed_trim else 0 for x in update_mac_filter]) == len(update_mac_filter):
                                break

                    if action=="LOCATION" : srv_antenna_anchor = checkmqttservers(srv_antenna_anchor)
                    address_trim=d.address.replace(":","")
                    #process the devic if  a filter exists and it is in the filter or there is no filter
                    if (d.name is not None):
                            # and (
                            # (( address_trim  in startCTE_address_filter and len(startCTE_address_filter)>0) or len(startCTE_address_filter)==0) and action=="LOCATION") or
                            # (( (address_trim in scan_mac_filter and len(scan_mac_filter)>0) or len(scan_mac_filter)==0) and action=="READ") or
                            # (( (address_trim in update_mac_filter and len(update_mac_filter)>0) or len(update_mac_filter)==0) and action=="UPDATE")):
                        nconerr=0
                        if d.name.startswith("BoldTag"):
                            dev = dev + 1

                            while nconerr>=0 and nconerr<MaxErrorLoops:
                                #print(d.address)
                                if app.webcancel:
                                    webcancelprocess = True
                                    break
                                address_trim=d.address.replace(":","")
                                if (action is not None and (d.address not in scannaddress ) and
                                        ( ((action=="LOCATION") and  (d.address not in devprocessed)) or
                                          (((d.address not in devprocessed ) and (action=="READ") and ((len(scan_mac_filter)==0) or (address_trim in scan_mac_filter))) or
                                        (((d.address in idupdate) and (d.address not in devprocessed ) ) and
                                         (action=="UPDATE"))))):
                                    if (nconerr==0):
                                        devcount = devcount + 1
                                    myDevice_1 = d
                                    myDevice_1 = d
                                    # TxPower_cal_k =-57.25
                                    # dist=np.power(10, (TxPower_cal_k - myDevice_1.rssi) / 10)
                                    # print(dist)
                                    if myDevice_1 is not None:
                                        address= str(myDevice_1.address)
                                        print('{}% -->> Processing {} {} '.format(int(dev/totaldevices*100.0), myDevice_1.name, address))
                                        app.print_statuslog('{}% -->> Processing {} {} '.format(int(dev/totaldevices*100.0), myDevice_1.name, address))

                                        # csv_row_new=csv_row.copy()
                                        # csv_row_new["mac"]=address
                                        # csv_row_new["name"]=myDevice_1.name
                                        print("address {}".format(address))

                                        location_fx=((address.replace(":", "") in startCTE_address_filter ) or (
                                                address.replace(":", "") in scan_control["tag_re_scan"] )) or (len(startCTE_address_filter) == 0 and len(
                                                scan_control["tag_re_scan"]) == 0)
                                        if not location_fx and action=="LOCATION":
                                            scannaddress.append(d.address)
                                            devprocessed.append(address)

                                        if (location_fx and action=="LOCATION" ) or action!="LOCATION":
                                            #try:
                                            #try to connect
                                            if action=="LOCATION" :
                                                srv_antenna_anchor = checkmqttservers(srv_antenna_anchor)
                                                if not init_location:
                                                    Stop_collecting = False
                                                    datadf = {}
                                                    janhors_processed = []
                                                    datadf_pos = {}
                                                    datadf_corr = {}
                                                    jmpos_processed = []
                                                    jang_corr_processed = []
                                            try:
                                                scannaddress.append(d.address)
                                                devprocessed.append(address)
                                                # ix = bscanner.tags.find_tag(address)
                                                if (d.connected):
                                                    # bscanner.tags.set_current(ix)
                                                    res=await d.tag_functions(action=action,uuid_filter_id=None,
                                                                                uuid_data_type_filter=uuid_data_type_filter,
                                                                                init_location=init_location,dfupdate=dfupdate,
                                                                                keep_connected=True,csv_read_data=csv_read_data,
                                                                                          param_enable_disable_tags=param_enable_disable_tags,
                                                                                          janhors_processed=janhors_processed,start_mqtt=start_mqtt)
                                                    ressult = res["result"]
                                                    dfupdate_read = res["dfupdate_read"]
                                                    csv_read_data = res["csv_read_data"]
                                                    recupdate = res["recupdate"]
                                                    devices_processed_location = res["devices_processed_location"]
                                                    init_location=res["init_location"]
                                                    start_mqtt=res["start_mqtt"]


                                            except Exception as e:
                                                print(e)
                                                app.print_statuslog("Error {0}".format(e))
                                else:
                                    nconerr=-1
                                if app.webcancel:
                                    nconerr=MaxErrorLoops
                                    webcancelprocess = True
                    else:
                        print("..")
                        #pass
                print("Loop {0} devices_filtered={1}".format(nscan, devices_filtered))
                print("Next Loop {0} devcount={1}".format(nscan, devcount))
                app.print_statuslog("Next Loop {0} devices_filtered={1}".format(nscan, devices_filtered))
                app.print_statuslog("Next Loop {0} devcount={1}".format(nscan, devcount))
                scannaddress_trim=[x.replace(":", "") for x in scannaddress]
                if app.webcancel:
                    nscan=MaxScan
                    webcancelprocess = True

            if discover_rssi:
                discover_rssi_start=False
                bscanner.discover_rssi_collect = True
                # await scanner.stop()

        else:
            scanstarted=False
            # time.sleep(1)
            await asyncio.sleep(1.0)

        Stop_collecting = True
        if (action == "UPDATE"):
            try:
                print("Process time {}".format(int(time.time() - time_process)))
                app.print_statuslog("Process time {} sec".format(int(time.time() - time_process)))

                if os.path.exists(file_path_update_error):
                    # Delete the file
                    os.remove(file_path_update_error)
                    print(f"File {file_path_update_error} has been deleted.")
                else:
                    print(f"File {file_path_update_error} does not exist.")
                if os.path.exists(file_path_update):
                    # Delete the file
                    os.remove(file_path_update)
                    print(f"File {file_path_update} has been deleted.")
                else:
                    print(f"File {file_path_update} does not exist.")
                if recupdate.shape[0]>0:
                    print(f"New file with errors {file_path_update_error} ")
                    recupdate.to_csv(file_path_update_error)
                dfupdate_read.to_csv(file_path_update_read, index=False)
                app.read_nfc_done = read_nfc_done
            except Exception as e:
                print("UPDATE file error")
                print(e)

        dataavg = None
        if (action == "LOCATION"):

            #if CTE was on during scan, last time to give last device time to be detected
            if keepactive_all_CTE_during_location:
                time.sleep(CTE_Wait_Time_posscan)

            try:
                Stop_collecting=True
                print("Stoping MQTT server")
                app.print_statuslog("Stoping MQTT server")
                if use_MQTT:
                    if not keep_mqtt_on: mqttclient.loop_stop()
                #time.sleep(1)
            except Exception as e:
                start_mqtt = False
                print("ERROR Stoping MQTT server")
                app.print_statuslog("ERROR Stoping MQTT server")

            if keepactive_all_CTE_during_location and not keepCTE_ON_aftert_location:
                for address in devprocessed:
                    try:
                        ix=bscanner.tags.find_tag(address=address)
                        bscanner.tags.scanner_param(ix)
                        # bscanner.tags.gatewaydb.set_csv_cfg_row_id(id="enable_cte", value=0)
                        # dfupdate_cfg = bscanner.tags.gatewaydb.dfupdate_cfg()
                        # res_tag = await bscanner.tags.tag_functions(action="UPDATE",uuid_data_type_filter="configuration",dfupdate=dfupdate_cfg)
                        bscanner.tags.gatewaydb.set_csv_row_id(id="enable_cte", value=0)
                        dfupdate_cfg = bscanner.tags.gatewaydb.dfupdate()
                        res_tag = await bscanner.tags.tag_functions(action="UPDATE",uuid_data_type_filter="configuration",dfupdate=dfupdate)

                    except Exception as e:
                        print(e)

            try:
                rssi_host_scan = bscanner.rssi_host_scan
                resdf, dataavg, data_posavg,scan_control, cancel_process = filter_location(file_path_angle,file_path_correction,file_path_angle_raw, file_path_correction_raw,file_path_position_raw,
                                                                           rssi_host_scan,scan_control,file_path_xposition_raw,file_path_yposition_raw,file_path_rposition_raw,
                                                                           startCTE_address_filter,val_outliers)

            except Exception as e:
                print("Location calculation error")
                app.print_statuslog("Location calculation error")
                print(e)

            if not scan_control["redo_scan"] or app.webcancel:

                print("Process time {} sec".format(int(time.time() - time_process)))
                app.print_statuslog("Process time {}".format(int(time.time() - time_process)))
                if not app.webcancel and not cancel_process:
                    if os.path.exists(file_path_location) :
                        # Delete the file
                        os.remove(file_path_location)
                        print(f"File {file_path_location} has been deleted.")
                    if os.path.exists(file_path_position):
                        # Delete the file
                        os.remove(file_path_position)
                        print(f"File {file_path_position} has been deleted.")
                    if resdf is not None:
                        if len(scan_mac_filter) > 0 and os.path.exists(file_path_location_copy) :
                            rsdf_copy=pd.read_csv(file_path_location_copy)
                            if 'index' in rsdf_copy.columns: rsdf_copy = rsdf_copy.drop(['index'], axis=1)
                            rsdf_copy=rsdf_copy.merge(resdf[["tag_mac","x", "y","std"]],left_on="tag_mac", right_on="tag_mac",how="left")
                            rsdf_copy.loc[rsdf_copy[(np.isnan(rsdf_copy["x_y"]) == False) | (np.isnan(rsdf_copy["y_y"]) == False)].index, "x_x"] =rsdf_copy.loc[rsdf_copy[(np.isnan(rsdf_copy["x_y"]) == False) | (np.isnan(rsdf_copy["y_y"]) == False)].index, "x_y"]
                            rsdf_copy.loc[rsdf_copy[(np.isnan(rsdf_copy["x_y"]) == False) | (np.isnan(rsdf_copy["y_y"]) == False)].index, "y_x"] = rsdf_copy.loc[rsdf_copy[(np.isnan(rsdf_copy["x_y"]) == False) | (np.isnan(rsdf_copy["y_y"]) == False)].index, "y_y"]
                            rsdf_copy.loc[rsdf_copy[(np.isnan(rsdf_copy["x_y"]) == False) | (np.isnan(rsdf_copy["y_y"]) == False)].index, "std_x"] = rsdf_copy.loc[rsdf_copy[(np.isnan(rsdf_copy["x_y"]) == False) | (np.isnan(rsdf_copy["y_y"]) == False)].index, "std_y"]
                            rsdf_copy.rename(columns={"x_x": "x", "y_x": "y", "std_x": "std"}, inplace=True)
                            rsdf_copy = rsdf_copy.drop(['x_y','y_y','std_y'], axis=1)
                            dnew = resdf.merge(rsdf_copy[["tag_mac", "x", "y", "std"]], left_on="tag_mac",
                                               right_on="tag_mac", how="left")
                            dnew=dnew[np.isnan(dnew["x_y"]) | np.isnan(dnew["y_y"])]
                            dnew.rename(columns={"x_x": "x", "y_x": "y", "std_x": "std"}, inplace=True)
                            dnew = dnew.drop(['x_y', 'y_y', 'std_y'], axis=1)
                            dnew=dnew[rsdf_copy.columns]
                            rsdf_copy = rsdf_copy._append(dnew, ignore_index=True)
                            rsdf_copy.to_csv(file_path_location, index=False)
                        else:
                            resdf.to_csv(file_path_location, index=False)

                    if data_posavg is not None:
                        data_posavg.to_csv(file_path_position, index=False)

                    if os.path.exists(file_path):   #startCTE_address_filter
                        try:
                            df_res=pd.read_csv(file_path)
                            # cols=[x for x in list(df_res.columns) if x not in ['x','y']]
                            # df_res=df_res[cols]
                            df_res = mergelocation(resdf, df_res,app_scan_columnIds, len(scan_mac_filter)>0)
                            df_res.to_csv(file_path,index=False)
                            app.anchors_init=anchors_init
                        except Exception as e:
                            print(e)


                else:
                    scan_control = {"tag_re_scan": [], "scan": 0, "redo_scan": False, "scan_loop": 0}
                    webcancelprocess = True
                    if os.path.exists(file_path_location):
                        try:
                            try:
                                # Copy file and metadata, and overwrite if it already exists
                                shutil.copy(file_path_location, file_path_location_copy)
                                print(f"File copied successfully from {file_path_location_copy} to {file_path_location}")
                            except Exception as e:
                                print(f"Error occurred: {e}")

                            os.remove(file_path_location_copy)
                            print(f"File '{file_path_location_copy}' has been deleted.")
                            # return True
                        except Exception as e:
                            print(f"An error occurred while deleting the file: {e}")
                            # return False
                    else:
                        print(f"File '{file_path_location_copy}' does not exist.")
                        columnIds_location = ["tag_mac", "out_prob", "out_prob_k", "anchors", "result", "x", "y"]
                        pd.DataFrame(columns=columnIds_location).to_csv(file_path_location, index=False)


        if (action == "READ"):
            #scan location
            print("Process time {} sec".format(int(time.time() - time_process)))
            app.print_statuslog("Process time {}".format(int(time.time() - time_process)))
            print(uuid_data_type_filter, csv_read_data)
            if len(csv_read_data)>0:
                try:
                    if len(csv_read_data) > 1:
                        df = pd.DataFrame(csv_read_data)
                    else:
                        df = pd.DataFrame(csv_read_data)

                    
                    # if df.shape[0]>0 :df["status"]="read" uuid_data_type_filter
                    df["status_base"] = "unknown"
                    df["status_detail"] = "unknown"
                    df["status_config"] = "unknown"

                    if uuid_data_type_filter == 'base':
                        df["status_base"]="read"
                    elif uuid_data_type_filter == 'detail':
                        df["status_detail"]="read"
                    elif uuid_data_type_filter == 'configuration':
                        df["status_config"]="read"

                    #x and y always the last rows
                    cols = [x for x in list(df.columns) if x not in ["x", "y"]]
                    cols.extend(["x", "y"])
                    df=df[cols]

                    if len(scan_mac_filter)>0 or param_keep_data:
                        try:
                            if os.path.exists(file_path_lastscan):
                                df_back = pd.read_csv(file_path_lastscan)

                                #in cas change in file format
                                for x in app.columnIds:
                                    if x not in list(df_back.columns):
                                        df_back[x]=None

                                #update existing records with new data
                                df_back["status"]="unknown"
                                if sum(df_back["mac"].isin(list(df["mac"].values)))>0:
                                    for ix in df_back[df_back["mac"].isin(list(df["mac"].values))].index:
                                        for k in app.columnIds[1:-2]:
                                            if k not in ['status_base', 'status_detail', 'status_config']:
                                                df_back.loc[ix,k]=df[df["mac"]==df_back.loc[ix,"mac"]][k].values[0]

                                        df_back.loc[ix, "status"] = \
                                        df.loc[df_back.loc[ix, "mac"] == df["mac"], "status"].values[0]

                                        if uuid_data_type_filter == 'base':
                                            df_back.loc[ix, "status_base"] = \
                                            df.loc[df_back.loc[ix, "mac"] == df["mac"], "status"].values[0]
                                        elif uuid_data_type_filter == 'detail':
                                            df_back.loc[ix, "status_detail"] = \
                                            df.loc[df_back.loc[ix, "mac"] == df["mac"], "status"].values[0]
                                        elif uuid_data_type_filter == 'configuration':
                                            df_back.loc[ix, "status_config"] = \
                                            df.loc[df_back.loc[ix, "mac"] == df["mac"], "status"].values[0]

                                    df_back=df_back[app.columnIds[:-2]]

                                #add new records
                                ix=[x  for x in df["mac"].values if x not in df_back["mac"].values ]
                                if len(ix)>0:
                                    ixr=df["mac"].isin(ix)
                                    df_back=pd.concat([df_back,df.loc[ixr,app.columnIds[:-2]]], ignore_index=True)

                                df=df_back
                        except Exception as e:
                            print(e)

                    # Check if the file exists
                    if os.path.exists(file_path):
                        # Delete the file
                        os.remove(file_path)
                        print(f"File {file_path} has been deleted.")
                    else:
                        print(f"File {file_path} does not exist.")

                    print(f"Writing new  {file_path} ....")
                    app.print_statuslog(f"Writing new  {file_path} ....")
                    df=df.reset_index(drop=True)
                    if os.path.exists(file_path_location):
                        resdf = pd.read_csv(file_path_location)
                    else:
                        resdf=None
                    if location_filter and resdf is not None:
                        try:
                            df["mac_strip"] = [x.replace(":", "") for x in df['mac'].values]
                            #df[~df['mac_strip'].isin([x[7:] for x in dataavg[dataavg["inout"] == True]['tag_mac'].values])]
                            # df_res = df[~df['mac_strip'].isin([x[7:] for x in resdf[resdf["out_prob_k"] > 0.25]['tag_mac'].values])]
                            df_res = df[~df['mac_strip'].isin(
                                [x[7:] for x in resdf[resdf["result"] == "OUT"]['tag_mac'].values])]
                            df_res = df_res.drop('mac_strip', axis=1)
                        except Exception as e:
                            print("Merge BLE and Location data error - LOcation data ignored")
                            app.print_statuslog("Merge BLE and Location data error - LOcation data ignored")
                            print(e)
                            df_res=df

                    else:
                        df_res = df
                    df_res_1=mergelocation(resdf, df_res, app_scan_columnIds)
                    df_res_1.to_csv(file_path,index=False) # if tags found

                except Exception as e:
                    print("UPDATE file error")
                    app.print_statuslog("UPDATE file error")
                    webcancelprocess=True
                    print(e)
            else:
                scan_control = {"tag_re_scan": [], "scan": 0, "redo_scan": False, "scan_loop": 0}
                if len(scan_mac_filter) == 0 or  param_keep_data:
                    if os.path.exists(file_path_lastscan):
                        try:
                            try:
                                # Copy file and metadata, and overwrite if it already exists
                                shutil.copy(file_path_lastscan, file_path)
                                print(f"File copied successfully from {file_path} to {file_path_lastscan}")
                            except Exception as e:
                                print(f"Error occurred: {e}")

                            os.remove(file_path_lastscan)
                            print(f"File '{file_path_lastscan}' has been deleted.")
                            # return True
                        except Exception as e:
                            print(f"An error occurred while deleting the file: {e}")
                            # return False
                    else:
                        print(f"File '{file_path_lastscan}' does not exist.")
                        # pd.DataFrame(columns=scan_columnIds).to_csv(file_path, index=False)
                        pd.DataFrame(columns=app.columnIds).to_csv(file_path, index=False)

                    #mark as not read
                    if os.path.exists(file_path):
                        df = pd.read_csv(file_path)
                        # webcancelprocess=True
                        if df.shape[0]>0:
                            if len(scan_mac_filter)>0:
                                ix = df["mac"].isin(scan_mac_filter)
                                df.loc[ix, "status"] = "not read"
                            else:
                                df["status"] = "not read"
                            df.to_csv(file_path, index=False) # writes if no tags detected
                    else:
                        pd.DataFrame(columns=app.scan_columnIds).to_csv(file_path, index=False)
                        df.to_csv(file_path, index=False)
                else:
                    #remove records, nothing found
                    pd.DataFrame(columns=app.scan_columnIds).to_csv(file_path, index=False)
                    df.to_csv(file_path, index=False)
                    # webcancelprocess = True

        if webcancelprocess or app.webcancel :
            app.webcancel=False
            webcancelprocess = False
            app.print_statuslog("------------------CANCEL---------------")


    print("-----------------------------------------")
    #thread.join()
    for ix in srv_antenna_anchor.keys():
        if srv_antenna_anchor[ix]["status"]:
            print(f"terminate_process(process) {ix}")
            process = srv_antenna_anchor[ix]["process"]
            # Terminate the process if needed
            terminate_process(process)
            monitor_thread = srv_antenna_anchor[ix]["monitor_thread"]
            # Wait for the monitor thread to finish
            monitor_thread.join()
            # Check the final status of the process
            exit_code = process.poll()
            print(f"Process finished with exit code {exit_code}")





#Run
asyncio.run(main())
print('ff')