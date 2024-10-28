# This is a working prototype. DO NOT USE IT IN LIVE PROJECTS
# https://github.com/bowdentheo/BLE-Beacon-Scanner/blob/master/ScanUtility.py

# https://github.com/hbldh/bleak
# https://koen.vervloesem.eu/blog/decoding-bluetooth-low-energy-advertisements-with-python-bleak-and-construct/
# import const

import asyncio
import os
import time

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
import json

# ibeacon_format = Struct(
#     "type_length" / Const(b"\x02\x15"),
#     "uuid" / Array(16, Byte),
#     "major" / Int16ub,
#     "minor" / Int16ub,
#     "power" / Int8sl,
#
# )

# address = []
# m1 = []
# m2 = []
# p1 = []
# p2 = []

location_filter=False
timeout_scanner=10

uuuds = []
uuuds.append("a3e68a83-4c4d-4778-bd0a-829fb434a7a1")

find_milwakiee = True
find_dewalt = False
print_no_manufacturer_data = False

def pass_to_func_and_pub(data_to_pub):
    print("Raw data: ", data_to_pub)
    try:
        unpacked_json = json.loads(data_to_pub)
    except Exception as e:
        print("Couldn't parse raw data: %s" % data_to_pub, e)
    else:
        print("JSON:", unpacked_json)
    return unpacked_json


anchors_init = {}
anchors_init["ble-pd-0C4314F46BF4"] = {'x': 0, "y": 0, "z": 0}
anchors_init["ble-pd-0C4314F46BF5"] = {'x': 0, "y": 0, "z": 0}
anchors_init["ble-pd-0C4314F46BF6"] = {'x': 0, "y": 0, "z": 0}
anchors_init["ble-pd-0C4314F46BF7"] = {'x': 0, "y": 0, "z": 0}

max_azimut_min = -45
max_azimut_max = 45
max_elevation_min = -45
max_elevation_max = +45

def scan_location():
    bchange = True
    datadf={}
    ix=0
    anchors = []
    tags = []
    Nmax=100
    n=0
    while bchange or n<Nmax:
        n=n+1
        manhors=subscribe.simple("silabs/#", hostname="localhost", port=1883)
        janhors = pass_to_func_and_pub(manhors.payload.decode('utf-8'))
        topic=manhors.topic
        anchor = topic.split("/")[3]
        tag = topic.split("/")[4]
        janhors['tag_mac'] = tag
        janhors['anchor_mac'] = anchor
        bchange = False
        if tag not in tags:
            tags.append(tag)
            bchange = True
        if anchor not in anchors:
            anchors.append(anchor)
            bchange=True
        if bchange: datadf[ix]=janhors
        ix=ix+1
    data=pd.DataFrame.from_dict(datadf, orient="index")
    dataavg = data.groupby(['anchor_mac', 'tag_mac']).mean().reset_index()
    dataavg["inout"] = False
    for ix,rec in dataavg.groupby("anchor_mac"):
        if rec['azimuth'].values[0]<max_azimut_min or rec['azimuth'].values[0]>max_azimut_max or \
            rec['elevation'].values[0]<max_elevation_min or  rec['elevation'].values[0]>max_elevation_max:
            dataavg["inout"] = True

    return dataavg

# async def notify_callback_notifications(sender: bleak.BleakGATTCharacteristic, data: bytearray):
#     print("notify_callback_notifications")
#     print(f"{sender}: {data}")
#
# async def notify_callback_indications(sender: bleak.BleakGATTCharacteristic, data: bytearray):
#     print("notify_callback_indications")
#     print(f"{sender}: {data}")
# async def notify_callback_Custom_Characteristic(sender: bleak.BleakGATTCharacteristic, data: bytearray):
#     print("notify_callback_Custom_Characteristic")
#     print(f"{sender}: {data}")
#
#
# async def notify_callback_tag_id_Characteristic(sender: bleak.BleakGATTCharacteristic, data: bytearray):
#     print("notify_callback_Custom_Characteristic")
#     print(f"{sender}: {data}")
#
# async def notify_callback_asset_id_Characteristic(sender: bleak.BleakGATTCharacteristic, data: bytearray):
#     print("notify_callback_Custom_Characteristic")
#     print(f"{sender}: {data}")

async def main():
    """Scan for devices."""
    scanner = BleakScanner()
    # scanner.register_detection_callback(device_found)
    char_uuid = {}
    char_uuid[0]={"id": "tag_id", "uuid": "c01cdf18-2465-4df6-956f-fde4867e2bc1", "value": "","scan":True,'type':"UTF-8","length":12}
    char_uuid[1]={"id": "asset_id", "uuid": "7db7b5e3-168e-48fd-aadb-94607557b832", "value": "", "scan": True, 'type': "UTF-8","length":128}
    #char_uuid[2]={id": "iop_test_stack_version", "uuid": "eb0571b1-88a7-4598-8d47-debdd9c98967", "value": "","scan":True,'type':"HEX","length":8}
    char_uuid[2]={"id": "update_nfc", "uuid": "1b9bba4d-34c0-4542-8d94-0da1036bd64f", "value": "","scan":False,'type':"HEX","length":1}
    char_uuid[3]={"id": "data_hash", "uuid": "cfdd75b8-5ed3-43cd-96cd-35129f648c5d", "value": "","scan":False,'type':"HEX","length":64}
    char_uuid[4]={"id": "certificate_id", "uuid": "fd052ad3-b4d3-426f-be19-b6b3107ab535", "value": "","scan":True,'type':"UTF-8","length":128}
    char_uuid[5]={"id": "type", "uuid": "d1251886-0135-4757-a6a4-233ed79914f3", "value": "","scan":True,'type':"UTF-8","length":128}
    char_uuid[6]={"id": "expiration_date", "uuid": "04f7c038-5717-4da6-b0af-4441388bf938", "value": "","scan":True,'type':"UTF-8","length":8}
    char_uuid[7]={"id": "color", "uuid": "3ef6ebcc-db6e-4b65-ab42-81bedf9c95a5", "value": "","scan":True,'type':"UTF-8","length":16}
    char_uuid[8]={"id": "series", "uuid": "b68a7594-7bf0-4da5-9067-cf986fa2e91d", "value": "","scan":True,'type':"UTF-8","length":32}
    char_uuid[9]={"id": "asset_images_file_extension", "uuid": "c53ff832-45ae-4a94-8bb9-26bea6b64c2c", "value": "","scan":True,'type':"UTF-8","length":3}
    # char_uuid[10] = {"id": "name", "uuid": "00002a00-0000-1000-8000-00805f9b34fb", "value": "", "scan": True,
    #                 'type': "UTF-8", "length": 12}
    char_uuid_update_nfc="1b9bba4d-34c0-4542-8d94-0da1036bd64f"
    serv_uuid_Custom_Service = "87e29466-8be6-4ede-9ffb-04a7121938da"
    serv_uuid_Generic_Service = "00001800-0000-1000-8000-00805f9b34fb"


    charfile_uuid=[]
    charfile_uuid.append({"id": "buffer_read", "uuid": "68ed3fb7-03c6-48cd-b385-baa4c8bce505", "value": "","scan":True,'type':"HEX","length":255})
    charfile_uuid.append({"id": "buffer_write", "uuid": "715016b1-abd0-41cd-80d9-9a997f87c642", "value": "", "scan": True,'type': "HEX", "length": 255})
    charfile_uuid.append({"id": "file_length", "uuid": "d86480ed-95f1-4cf9-9b7a-dd3ff2cdeb35", "value": "", "scan": True, 'type': "HEX","length": 4})
    charfile_uuid.append({"id": "file_transfer_status", "uuid": "3d03d488-34b8-4f94-b9a1-0f7e339b7878", "value": "", "scan": True, 'type': "HEX", "length": 1})
    charfile_uuid.append({"id": "file_length_sent", "uuid": "89bc1cd2-cee7-46a6-ba38-d3497678a777", "value": "", "scan": True, 'type': "HEX","length": 4})
    serv_uuid_Custom_File_Transfer_Service = "4c209b89-3330-4f18-b26e-d90f8653306e"


    csv_row={'mac':"","name":"",'tag_id':"",'asset_id':"",'certificate_id':"",'type':"",'expiration_date':"",'color':"",'series':"",'asset_images_file_extension':""}


    while True:
        time.sleep(5)
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
        MaxScan=10
        nscan=0
        if doscan:
            devices = await scanner.discover(timeout=timeout_scanner)
            myDevice = None
            myDevice_1 = None
            for nscan in range(MaxScan):
                print("Scan %d" % nscan)
                for d in devices:
                    # if KeyValueCoding.getKey(d.details, 'name') == 'awesomecoolphone':
                    if d.name is not None:
                        if d.name.startswith("TGS_")  :
                            print(d.address)
                            if action is not None and d.address not in scannaddress and ((((d.address not in devprocessed) and (action=="READ")) or
                                    (((d.address in idupdate) and (d.address not in devprocessed) ) and (action=="UPDATE")))):
                                scannaddress.append(d.address)
                                myDevice_1 = d
                                # myDevice = d
                                if myDevice_1 is not None:
                                    address= str(myDevice_1.address)
                                    print('Processing {} {} '.format(myDevice_1.name, address))
                                    devprocessed.append(address)
                                    csv_row_new=csv_row.copy()
                                    csv_row_new["mac"]=address
                                    csv_row_new["name"]=myDevice_1.name
                                    print("address {}".format(address))
                                    try:
                                        async with BleakClient(address) as client:
                                            try:
                                                connected = client.is_connected
                                                if connected:
                                                    print("Connected to Device")
                                                    print("Performing action {}".format(action))
                                                    if (action=="READ"):
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
                                                        svcs = await client.get_services()

                                                        print("Services:")
                                                        service = None
                                                        service_generic=None
                                                        for service_1 in svcs:
                                                            # if service_1.uuid==serv_uuid_Throughput_Test_Service_uuid:
                                                            if service_1.uuid == serv_uuid_Custom_Service:
                                                                service = service_1
                                                            if service_1.uuid == serv_uuid_Generic_Service:
                                                                service_generic = service_1

                                                        if service is not None:
                                                            rec=dfupdate[dfupdate["mac"] == myDevice_1.address]
                                                            for k in range(len(char_uuid)):
                                                                try:
                                                                    scan = char_uuid[k]['scan']
                                                                    if scan:
                                                                        char_uuid_id = char_uuid[k]['uuid']
                                                                        id = char_uuid[k]['id']
                                                                        print("Updating {0}".format(id))
                                                                        newval=str(rec[id].values[0])

                                                                        if char_uuid[k]['id']=="name":
                                                                            if service_generic is not None:
                                                                                res = await client.write_gatt_char(
                                                                                    service_generic.get_characteristic(
                                                                                        char_uuid_id),
                                                                                    bytearray(newval, 'utf-8'),
                                                                                    response=True)
                                                                        else:
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

                                                            #
                                                            # res = await client.write_gatt_char(
                                                            #     service.get_characteristic(char_uuid_tag_id),
                                                            #     bytearray("AAA008", 'utf-8'), response=True)
                                                            # print(res)
                                                            # tag_id = bytes(await client.read_gatt_char(char_uuid_tag_id))
                                                            # print("tag_id: {0}".format(tag_id))
                                                            #
                                                            # res = await client.write_gatt_char(
                                                            #     service.get_characteristic(char_uuid_update_nfc),
                                                            #     bytearray("1", 'utf-8'), response=True)
                                                            # print(res)
                                                            # update_nfc = bytes(await client.read_gatt_char(char_uuid_tag_id))
                                                            # print("char_uuid_update_nfc: {0}".format(update_nfc))

                                                            pass
                                                    await client.disconnect()
                                                    # while True:
                                                    #     if not connected:
                                                    #         break
                                                    #     await asyncio.sleep(1.0)
                                                        # transmission_on = bytes( await client.read_gatt_char(char_uuid_Transmission_ON))
                                                        # print("transmission_on: {0}".format(transmission_on))
                                                        # Throughput_result = bytes( await client.read_gatt_char(char_uuid_Throughput_result))
                                                        # print("Throughput_result: {0}".format(Throughput_result))



                                                else:
                                                    print(f"Failed to connect to Device")
                                            except Exception as e:
                                                print(e)
                                    except Exception as e:
                                        print(f"Failed to connect to Device {0}".format(address))
                                        print(e)

                    else:
                        #print("..")
                        pass
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
                            dataavg = scan_location()
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
                    print(f"Writing new  {file_path} ....")
                    df=df.reset_index(drop=True)
                    if location_filter and dataavg is not None:
                        try:
                            df["mac_strip"] = [x.replace(":", "") for x in df['mac'].values]
                            df[~df['mac_strip'].isin([x[7:] for x in dataavg[dataavg["inout"] == True]['tag_mac'].values])]
                            df_res = df[~df['mac_strip'].isin([x[7:] for x in dataavg[dataavg["inout"] == True]['tag_mac'].values])]
                            df_res = df_res.drop('mac_strip', axis=1)
                        except Exception as e:
                            print("Merge BLE and Location data error - LOcation data ignored")
                            print(e)
                            df_res=df

                    else:
                        df_res = df
                    df_res.to_csv(file_path,index=False)
                    # if d.name=="Blinky ExampleC":
                    #     print('Found it')
                    #     myDevice = d
                    #     break
                    # if d.name=="TGS_Tag_77":
                except Exception as e:
                    print("UPDATE file error")
                    print(e)





        print("-----------------------------------------")
asyncio.run(main())
print('ff')