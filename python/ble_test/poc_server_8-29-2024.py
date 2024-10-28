# This is a working prototype. DO NOT USE IT IN LIVE PROJECTS
# https://github.com/bowdentheo/BLE-Beacon-Scanner/blob/master/ScanUtility.py

# https://github.com/hbldh/bleak
# https://koen.vervloesem.eu/blog/decoding-bluetooth-low-energy-advertisements-with-python-bleak-and-construct/
# import const

import asyncio
import os
import time
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
from math import sqrt, pi, exp
from threading import Thread


#MQTT
broker ='localhost' #'broker.emqx.io' "test.mosquitto.org"#
port = 1883
topic_angle="silabs/aoa/angle/#"
topic_location="silabs/aoa/position/positioning-test_room/#"
topic_correction="silabs/aoa/correction/#"


datadf={}
datadf_pos = {}
datadf_corr = {}
Stop_collecting=True
disableCTE=False
CTE_Wait_Time=10

location_filter=True
MaxScan=3
MaxTags=10
SamplesPerTag=10
NumAnchors=4

uuuds = []
uuuds.append("a3e68a83-4c4d-4778-bd0a-829fb434a7a1")

find_milwakiee = True
find_dewalt = False
print_no_manufacturer_data = False

anchors_init = {}
anchors_init["0C4314F46AF2"] = {'x': 0, "y": 0, "z": 0, "max_azimut_min":-90,"max_azimut_max":0,"max_elevation_min": -90,"max_elevation_max":90}
anchors_init["0C4314F46D3D"] = {'x': 0, "y": 0, "z": 0, "max_azimut_min":-180,"max_azimut_max":-90,"max_elevation_min": -90,"max_elevation_max":90}
anchors_init["0C4314F46C1D"] = {'x': 0, "y": 0, "z": 0, "max_azimut_min":0,"max_azimut_max":90,"max_elevation_min": -90,"max_elevation_max":90}
anchors_init["0C4314F46CC0"] = {'x': 0, "y": 0, "z": 0, "max_azimut_min":90,"max_azimut_max":180,"max_elevation_min": -90,"max_elevation_max":90}


# max_azimut_min = -135
# max_azimut_max = -45
# max_elevation_min = -90
# max_elevation_max = +90


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
        print(topic)
        if not Stop_collecting:
            if topic.startswith(topic_angle[:-2]):
                print("Processing {0}".format(topic))
                janhors = pass_to_func_and_pub(message.payload.decode('utf-8'))
                anchor = topic.split("/")[3]
                tag = topic.split("/")[4]
                janhors['tag_mac'] = tag.split("-")[2]
                janhors['anchor_mac'] = anchor.split("-")[2]
                datadf[len(datadf)] = janhors

            if topic.startswith(topic_location[:-2]):
                print("Processing {0}".format(topic))
                jmpos = pass_to_func_and_pub(message.payload.decode('utf-8'))
                topic_pos = message.topic
                tag = topic_pos.split("/")[4]
                jmpos['tag_mac'] = tag.split("-")[2]
                datadf_pos[len(datadf_pos)] = jmpos

            if topic.startswith(topic_correction[:-2]):
                print("Processing {0}".format(topic))
                jang_corr = pass_to_func_and_pub(message.payload.decode('utf-8'))
                topic_corr = message.topic
                anchor = topic_corr.split("/")[3]
                tag = topic_corr.split("/")[4]
                jang_corr['tag_mac'] = tag.split("-")[2]
                jang_corr['anchor_mac'] = anchor.split("-")[2]
                datadf_corr[len(datadf_corr)] = jang_corr


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
def est_kalmann(data_last_scan,measurement_sig = 2.,mu = 0.,sig = 10000., y_name="rssi"):
    try:
        # initial parameters
        # measurement_sig = 2.
        # motion_sig = 2.
        # mu = 0.
        # sig = 10000.
        k_mu = "k_{0}_mu".format(y_name)
        k_sig = "k_{0}_sig".format(y_name)

        data = pd.DataFrame(data_last_scan)
        data[k_mu] = 0
        data[k_sig] = 0

        for i in range(len(data.groupby(["tag_mac"]).count().reset_index()["tag_mac"])):
            d1 = data[data["tag_mac"] == (data.groupby(["tag_mac"]).count().reset_index()["tag_mac"][i])]
            for j in range(len(d1.groupby(["anchor_mac"]).count().reset_index()["anchor_mac"])):
                fd1 = data["tag_mac"] == (data.groupby(["tag_mac"]).count().reset_index()["tag_mac"][i])
                fd2 = d1["anchor_mac"] == (d1.groupby(["anchor_mac"]).count().reset_index()["anchor_mac"][j])
                f = (fd1 & fd2)
                # d2=data[f]
                # d2 = d1[d1["node"] == (d1.groupby(["node"]).count().reset_index()["node"][j])]
                measurements = data[f][y_name].values
                # motions = data.loc[f,["rssi"]].values
                ## TODO: Loop through all measurements/motions
                # this code assumes measurements and motions have the same length
                # so their updates can be performed in pairs
                for n in range(len(measurements)):
                    # measurement update, with uncertainty
                    print('measurement: [{}, ]'.format(measurements[n]))
                    mu, sig = update(mu, sig, measurements[n], measurement_sig)
                    print('Update: [{}, {}]'.format(mu, sig))
                    # motion update, with uncertainty
                    # mu, sig = predict(mu, sig, motions[n], motion_sig)
                    # print('Predict: [{}, {}]'.format(mu, sig))

                # print the final, resultant mu, sig
                print('\n')
                print('Final result: [{}, {}]'.format(mu, sig))
                data.loc[f, [k_mu]] = mu
                data.loc[f, [k_sig] ]= sig

        i = 0
        for x in data_last_scan:
            x[k_mu] = data.loc[i][k_mu]
            x[k_sig] = data.loc[i][k_sig]
            i = i + 1

    except Exception as e:
        # logging.error('Error at %s', 'division', exc_info=e)
        print('Error at %s'%e)
    return data_last_scan

#---------------------------------------------------------------------#
# END  Kalmann Filter
#---------------------------------------------------------------------#



#---------------------------------------------------------------------#
#                 Scan Location
#
#---------------------------------------------------------------------#
def pass_to_func_and_pub(data_to_pub):
    print("Raw data: ", data_to_pub)
    try:
        unpacked_json = json.loads(data_to_pub)
    except Exception as e:
        print("Couldn't parse raw data: %s" % data_to_pub, e)
    else:
        print("JSON:", unpacked_json)
    return unpacked_json

def filter_location(nmaxtags=10):
    # # bchange = True
    # datadf={}
    # datadf_corr={}
    # datadf_pos={}
    # ix=0
    # anchors = []
    # tags = []
    # Nmax=20#nmaxtags*10*4
    # n=0
    # caltest=[]
    # while n<Nmax:
    #     n=n+1
    #     print("MQTT progress %f", int(n/Nmax*100.0))
    #     try:
    #         manhors=subscribe.simple("silabs/aoa/angle/#", hostname="localhost", port=1883)
    #         janhors = pass_to_func_and_pub(manhors.payload.decode('utf-8'))
    #         topic = manhors.topic
    #         anchor = topic.split("/")[3]
    #         tag = topic.split("/")[4]
    #         janhors['tag_mac'] = tag.split("-")[2]
    #         janhors['anchor_mac'] = anchor.split("-")[2]
    #
    #         mpos = subscribe.simple("silabs/aoa/position/positioning-test_room/#", hostname="localhost", port=1883, keepalive=1)
    #         jmpos = pass_to_func_and_pub(mpos.payload.decode('utf-8'))
    #         topic_pos = mpos.topic
    #         tag = topic_pos.split("/")[4]
    #         jmpos['tag_mac'] = tag.split("-")[2]
    #
    #         mang_corr = subscribe.simple("silabs/aoa/correction/#", hostname="localhost", port=1883, keepalive=1)
    #         jang_corr = pass_to_func_and_pub(mang_corr.payload.decode('utf-8'))
    #         topic_corr = mang_corr.topic
    #         anchor = topic_corr.split("/")[3]
    #         tag = topic_corr.split("/")[4]
    #         jang_corr['tag_mac'] = tag.split("-")[2]
    #         jang_corr['anchor_mac'] = anchor.split("-")[2]
    #
    #         datadf[ix]=janhors
    #         datadf_pos[ix] = jmpos
    #         datadf_corr[ix] = jang_corr
    #
    #     except Exception as e:
    #         print(f"Failed to subscribe.simple('silabs/#', hostname='localhost', port=1883)")
    #         print(e)
    #     ix=ix+1
    data=pd.DataFrame.from_dict(datadf, orient="index")
    data_pos = pd.DataFrame.from_dict(datadf_pos, orient="index")
    data_corr = pd.DataFrame.from_dict(datadf_corr, orient="index")

    dataavg1 = data.groupby(['anchor_mac', 'tag_mac']).mean().reset_index()
    data_posavg = data_pos.groupby([ 'tag_mac']).mean().reset_index()
    data_corravg = data_corr.groupby(['anchor_mac', 'tag_mac']).mean().reset_index()


    # caltest.append(data_posavg.values[0])
    # data_cal = pd.DataFrame(caltest)
    # data_cal.columns = data_pos.columns

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
    return resdf,dataavg,data_posavg


#---------------------------------------------------------------------#
# END  Scan Location
#---------------------------------------------------------------------#



#---------------------------------------------------------------------#
#               Main Scan BLE
#---------------------------------------------------------------------#


#Gatt database
#--------------------
char_uuid = {}
char_uuid[0]={"id": "tag_id", "uuid": "c01cdf18-2465-4df6-956f-fde4867e2bc1", "value": "","scan":True,'type':"UTF-8","length":12}
char_uuid[1]={"id": "asset_id", "uuid": "7db7b5e3-168e-48fd-aadb-94607557b832", "value": "", "scan": True, 'type': "UTF-8","length":128}
char_uuid[2]={"id": "update_nfc", "uuid": "1b9bba4d-34c0-4542-8d94-0da1036bd64f", "value": "","scan":False,'type':"HEX","length":1}
char_uuid[3]={"id": "data_hash", "uuid": "cfdd75b8-5ed3-43cd-96cd-35129f648c5d", "value": "","scan":False,'type':"HEX","length":64}
char_uuid[4]={"id": "certificate_id", "uuid": "fd052ad3-b4d3-426f-be19-b6b3107ab535", "value": "","scan":True,'type':"UTF-8","length":128}
char_uuid[5]={"id": "type", "uuid": "d1251886-0135-4757-a6a4-233ed79914f3", "value": "","scan":True,'type':"UTF-8","length":128}
char_uuid[6]={"id": "expiration_date", "uuid": "04f7c038-5717-4da6-b0af-4441388bf938", "value": "","scan":True,'type':"UTF-8","length":8}
char_uuid[7]={"id": "color", "uuid": "3ef6ebcc-db6e-4b65-ab42-81bedf9c95a5", "value": "","scan":True,'type':"UTF-8","length":16}
char_uuid[8]={"id": "series", "uuid": "b68a7594-7bf0-4da5-9067-cf986fa2e91d", "value": "","scan":True,'type':"UTF-8","length":32}
char_uuid[9]={"id": "asset_images_file_extension", "uuid": "c53ff832-45ae-4a94-8bb9-26bea6b64c2c", "value": "","scan":True,'type':"UTF-8","length":3}

#cahracteristics
char_uuid_update_nfc="1b9bba4d-34c0-4542-8d94-0da1036bd64f"
char_uuid_constant_tone_extension_enable ="00002bad-0000-1000-8000-00805f9b34fb"
char_uuid_enable_cte ="c92c584f-7b9e-473a-ad4e-d9965e0cd678"

serv_uuid_Custom_Service = "87e29466-8be6-4ede-9ffb-04a7121938da"
serv_uuid_Generic_Service = "00001800-0000-1000-8000-00805f9b34fb"
serv_uuid_Constant_Tone_Service="0000184a-0000-1000-8000-00805f9b34fb"


charfile_uuid=[]
charfile_uuid.append({"id": "buffer_read", "uuid": "68ed3fb7-03c6-48cd-b385-baa4c8bce505", "value": "","scan":True,'type':"HEX","length":255})
charfile_uuid.append({"id": "buffer_write", "uuid": "715016b1-abd0-41cd-80d9-9a997f87c642", "value": "", "scan": True,'type': "HEX", "length": 255})
charfile_uuid.append({"id": "file_length", "uuid": "d86480ed-95f1-4cf9-9b7a-dd3ff2cdeb35", "value": "", "scan": True, 'type': "HEX","length": 4})
charfile_uuid.append({"id": "file_transfer_status", "uuid": "3d03d488-34b8-4f94-b9a1-0f7e339b7878", "value": "", "scan": True, 'type': "HEX", "length": 1})
charfile_uuid.append({"id": "file_length_sent", "uuid": "89bc1cd2-cee7-46a6-ba38-d3497678a777", "value": "", "scan": True, 'type': "HEX","length": 4})
serv_uuid_Custom_File_Transfer_Service = "4c209b89-3330-4f18-b26e-d90f8653306e"


csv_row={'mac':"","name":"",'tag_id':"",'asset_id':"",'certificate_id':"",'type':"",'expiration_date':"",'color':"",'series':"",'asset_images_file_extension':""}

#
# def disbale_cte(service, client, char_uuid_id=char_uuid_enable_cte):
#     try:
#         res = client.write_gatt_char(
#             service.get_characteristic(char_uuid_id),
#             bytearray([0x00]),
#             response=True)
#     except Exception as e:
#         print(e)
#
#
# def enable_cte(service, client, char_uuid_id=char_uuid_enable_cte):
#     try:
#         res = client.write_gatt_char(
#             service.get_characteristic(char_uuid_id),
#             bytearray([0x01]),
#             response=True)
#     except Exception as e:
#         print(e)


# def findservices(client):
#     svcs = client.get_services()
#     print("Services:")
#     service = None
#     service_generic = None
#     servicecConstant_tone = None
#     for service_1 in svcs:
#         # if service_1.uuid==serv_uuid_Throughput_Test_Service_uuid:
#         if service_1.uuid == serv_uuid_Custom_Service:
#             service = service_1
#         if service_1.uuid == serv_uuid_Generic_Service:
#             service_generic = service_1
#         if service_1.uuid == serv_uuid_Constant_Tone_Service:
#             servicecConstant_tone = service_1
#     return service, service_generic, servicecConstant_tone

async def main():
    """Scan for devices."""
    #scan_location()
    client=run_mqtt()
    thread = Thread(target = threaded_function, kwargs={'client':client},daemon=True)
    thread.start()
    # thread.join()
    print("thread finished...exiting")

    scanner = BleakScanner()


    while True:
        csv_read_data = []
        devprocessed=[]
        idupdate = []
        # Specify the directory path
        directory = "c:/tgspoc"

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
        file_path_position = directory + "/scan_position.csv"
        scancsv=None
        action=None
        # Check if the file exists
        if os.path.exists(file_path):
            # Read the CSV file using the built-in csv module
            scancsv=pd.read_csv(file_path)
            print(f"File {file_path} exist.")

        else:
            print(f"File {file_path} does not exist.")
            print("Doing Scanning data...")
            action = "READ"
            doscan=True

        file_path_update = directory+"/scan_update.csv"
        file_path_update_error= directory+"/scan_update_error.csv"
        dfupdate=None
        # Check if the file exists
        if os.path.exists(file_path_update):
            try:
                # Read the CSV file using the built-in csv module
                # scan_updatecsv=pd.read_csv(file_path_update)
                action = "UPDATE"
                print("Doing Updating and updating data...")
                dfupdate=pd.read_csv(file_path_update)
                idupdate=dfupdate['mac'].values
                recupdate = dfupdate.copy()
                doscan=True
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
        if doscan:
            service=None

            # #Disable  CTE in all devices
            # service_generic=None
            # servicecConstant_tone=None
            # devices = await scanner.discover()
            # print("Scan %d" % nscan)
            # for d in devices:
            #     if d.name is not None:
            #         if d.name.startswith("TGS_"):
            #             address = str(d.address)
            #             print("Disableing CTE tone in {}".format(address))
            #             async with BleakClient(address) as client:
            #                 try:
            #                     if service is None:
            #                         svcs = await client.get_services()
            #                         print("Services:")
            #                         for service_1 in svcs:
            #                             # if service_1.uuid==serv_uuid_Throughput_Test_Service_uuid:
            #                             if service_1.uuid == serv_uuid_Custom_Service:
            #                                 service = service_1
            #                             if service_1.uuid == serv_uuid_Generic_Service:
            #                                 service_generic = service_1
            #                             if service_1.uuid == serv_uuid_Constant_Tone_Service:
            #                                 servicecConstant_tone = service_1
            #                         if servicecConstant_tone is not None and disableCTE:
            #                             disbale_cte(service, client)
            #                         await client.disconnect()
            #
            #                 except Exception as e:
            #                     print(e)

            devcount=0
            myDevice = None
            myDevice_1 = None
            nscan=0

            #MQTT AoA scaning initialization
            datadf = {}
            datadf_pos = {}
            datadf_corr = {}
            Stop_collecting=False

            while nscan < MaxScan and len(scannaddress) <MaxTags:
                nscan=nscan+1
                devices = await scanner.discover()
                print("Scan %d" % nscan)
                for d in devices:
                    # if KeyValueCoding.getKey(d.details, 'name') == 'awesomecoolphone':
                    if d.name is not None:
                        nconerr=0
                        if d.name.startswith("TGS_"):
                            while nconerr>=0 and nconerr<2:
                                print(d.address)
                                if (action is not None and (d.address not in scannaddress ) and
                                        ((((d.address not in devprocessed ) and (action=="READ")) or
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
                                        print('Processing {} {} '.format(myDevice_1.name, address))
                                        csv_row_new=csv_row.copy()
                                        csv_row_new["mac"]=address
                                        csv_row_new["name"]=myDevice_1.name
                                        print("address {}".format(address))
                                        try:
                                            async with BleakClient(address) as client:
                                                try:
                                                    scannaddress.append(d.address)
                                                    devprocessed.append(address)
                                                    nconerr = -1
                                                    connected = client.is_connected
                                                    if connected:
                                                        print("Connected to Device")
                                                        print("Performing action {}".format(action))
                                                        svcs = await client.get_services()

                                                        print("Services:")
                                                        service = None
                                                        service_generic = None
                                                        for service_1 in svcs:
                                                            # if service_1.uuid==serv_uuid_Throughput_Test_Service_uuid:
                                                            if service_1.uuid == serv_uuid_Custom_Service:
                                                                service = service_1
                                                            if service_1.uuid == serv_uuid_Generic_Service:
                                                                service_generic = service_1

                                                        if (action=="READ"):
                                                            if service is not None:

                                                                if disableCTE:
                                                                    # Sart advertisement
                                                                    #char_uuid_enable_cte = "c92c584f-7b9e-473a-ad4e-d9965e0cd678"
                                                                    res = await client.write_gatt_char(
                                                                        service.get_characteristic(char_uuid_enable_cte),
                                                                        bytearray([0x01]),
                                                                        response=True)

                                                                for k in range(len(char_uuid)):
                                                                    try:
                                                                        char_uuid_id = char_uuid[k]['uuid']
                                                                        id=char_uuid[k]['id']
                                                                        scan = char_uuid[k]['scan']
                                                                        char_uuid_val = bytes(await client.read_gatt_char(char_uuid_id))
                                                                        print("{0} ({1}): {2}".format(id,scan,char_uuid_val))
                                                                        if scan:
                                                                            if type(char_uuid_val) is bytes:
                                                                                val=char_uuid_val.decode('utf-8')
                                                                            else:
                                                                                val = str(char_uuid_val)
                                                                            char_uuid[k]['value'] = val
                                                                            if id in csv_row_new.keys():
                                                                                csv_row_new[id]= val
                                                                    except Exception as e:
                                                                        print("address: {0}".format(address))
                                                                        print("char_uuid_id: {0}".format(char_uuid_id))
                                                                        print(e)
                                                                csv_read_data.append(csv_row_new)

                                                        if (action == "UPDATE"):

                                                            if service is not None:
                                                                rec=dfupdate[dfupdate["mac"] == myDevice_1.address]

                                                                # # Sart advertisement
                                                                # #char_uuid_enable_cte = "c92c584f-7b9e-473a-ad4e-d9965e0cd678"
                                                                # res = await client.write_gatt_char(
                                                                #     service.get_characteristic(char_uuid_enable_cte),
                                                                #     bytearray([0x01]),
                                                                #     response=True)

                                                                for k in range(len(char_uuid)):
                                                                    try:
                                                                        scan = char_uuid[k]['scan']
                                                                        if scan:
                                                                            char_uuid_id = char_uuid[k]['uuid']
                                                                            id = char_uuid[k]['id']
                                                                            print("Updating {0}".format(id))
                                                                            newval=str(rec[id].values[0])

                                                                            res = await client.write_gatt_char(
                                                                                service.get_characteristic(char_uuid_id),
                                                                                bytearray(newval, 'utf-8'),
                                                                                response=True)
                                                                            # print(res)
                                                                            valread_raw=await client.read_gatt_char(char_uuid_id)
                                                                            if valread_raw is not None:
                                                                                if type(valread_raw) is bytearray:
                                                                                    valread = bytes(valread_raw)
                                                                                else:
                                                                                    pass
                                                                            else:
                                                                                valread=bytes(b'')
                                                                            if type(valread) is bytes:
                                                                                val = valread.decode('utf-8')
                                                                            else:
                                                                                val = str(valread)
                                                                            print("id read: {0}".format(val))


                                                                    except Exception as e:
                                                                        print("address: {0}".format(address))
                                                                        print("char_uuid_id: {0}".format(char_uuid_id))
                                                                        print(e)

                                                                recupdate.drop(recupdate[recupdate["mac"] == myDevice_1.address].index,
                                                                               inplace=True)
                                                                #Update NFC
                                                                res = await client.write_gatt_char(
                                                                    service.get_characteristic(char_uuid_update_nfc),
                                                                    bytearray("1", 'utf-8'),
                                                                    response=True)
                                                                print(res)

                                                                pass

                                                        if disableCTE:
                                                            #Stop advertisement
                                                            time.sleep(CTE_Wait_Time)
                                                            res = await client.write_gatt_char(
                                                                service.get_characteristic(char_uuid_enable_cte),
                                                                bytearray([0x00]),
                                                                response=True)

                                                        await client.disconnect()


                                                    else:
                                                        print(f"Failed to connect to Device")
                                                except Exception as e:
                                                    print(e)
                                        except Exception as e:
                                            print(f"Failed to connect to Device {0}".format(address))
                                            print(e)
                                            nconerr=nconerr+1
                                else:
                                    nconerr=-1
                    else:
                        #print("..")
                        pass
                print("Next Loop {0} devcount={1}".format(nscan, devcount))
        else:
            time.sleep(5)

        Stop_collecting = True
        if (action == "UPDATE"):
            try:
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
            except Exception as e:
                print("UPDATE file error")
                print(e)
        if (action == "READ"):
            #scan location

            if len(csv_read_data)>0:
                try:
                    dataavg=None
                    try:
                        if location_filter:
                            resdf,dataavg,data_posavg  = filter_location(MaxTags)

                    except Exception as e:
                        print("Location error")
                        print(e)

                    if len(csv_read_data) > 1:
                        df = pd.DataFrame(csv_read_data)
                    else:
                        df = pd.DataFrame(csv_read_data)
                    # Check if the file exists
                    if os.path.exists(file_path):
                        # Delete the file
                        os.remove(file_path)
                        print(f"File {file_path} has been deleted.")
                    else:
                        print(f"File {file_path} does not exist.")
                    if os.path.exists(file_path_location):
                        # Delete the file
                        os.remove(file_path_location)
                        print(f"File {file_path_location} has been deleted.")
                    if os.path.exists(file_path_position):
                        # Delete the file
                        os.remove(file_path_position)
                        print(f"File {file_path_position} has been deleted.")



                    print(f"Writing new  {file_path} ....")
                    df=df.reset_index(drop=True)
                    if location_filter and dataavg is not None:
                        try:
                            df["mac_strip"] = [x.replace(":", "") for x in df['mac'].values]
                            #df[~df['mac_strip'].isin([x[7:] for x in dataavg[dataavg["inout"] == True]['tag_mac'].values])]
                            df_res = df[~df['mac_strip'].isin([x[7:] for x in resdf[resdf["out_prob"] > 0.50]['tag_mac'].values])]
                            df_res = df_res.drop('mac_strip', axis=1)
                        except Exception as e:
                            print("Merge BLE and Location data error - LOcation data ignored")
                            print(e)
                            df_res=df

                    else:
                        df_res = df
                    df_res.to_csv(file_path,index=False)
                    resdf.to_csv(file_path_location,index=False)
                    data_posavg.to_csv(file_path_position, index=False)
                    # if d.name=="Blinky ExampleC":
                    #     print('Found it')
                    #     myDevice = d
                    #     break
                    # if d.name=="TGS_Tag_77":
                except Exception as e:
                    print("UPDATE file error")
                    print(e)





        print("-----------------------------------------")
    thread.join()

asyncio.run(main())
print('ff')