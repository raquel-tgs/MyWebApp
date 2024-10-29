# This is a working prototype. DO NOT USE IT IN LIVE PROJECTS
# https://github.com/bowdentheo/BLE-Beacon-Scanner/blob/master/ScanUtility.py

# https://github.com/hbldh/bleak
# https://koen.vervloesem.eu/blog/decoding-bluetooth-low-energy-advertisements-with-python-bleak-and-construct/
# import const

import asyncio

import bleak
import pandas as pd
from bleak import BleakScanner
from bleak import BleakClient
from uuid import UUID
from construct import Array, Byte, Const, Int8sl, Int16ub, Struct
from construct.core import ConstError
import keyboard
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
import numpy as np
import time

ibeacon_format = Struct(
    "type_length" / Const(b"\x02\x15"),
    "uuid" / Array(16, Byte),
    "major" / Int16ub,
    "minor" / Int16ub,
    "power" / Int8sl,

)

address = []
m1 = []
m2 = []
p1 = []
p2 = []

uuuds = []
uuuds.append("a3e68a83-4c4d-4778-bd0a-829fb434a7a1")

find_milwakiee = True
find_dewalt = False
print_no_manufacturer_data = False


def device_found(device: BLEDevice, advertisement_data: AdvertisementData):
    """Decode iBeacon."""
    try:
        bres = False
        # print("device.name -------------------> %s" % device.name)
        # print("nservice_uuids %s" % advertisement_data.service_uuids)
        # print("nmanufacturer_data %s" % advertisement_data.manufacturer_data)
        # print("local_name --------->>%s" % advertisement_data.local_name)
        # print("service_data %s" % advertisement_data.service_data)
        # print("rssi %s" % advertisement_data.rssi)
        btag=False
        if device.name is None:
                #print( device.address)
                pass
        if device.name is not None:
            if device.name.startswith("BoldTag"):
                btag=True
                print("{} {} {}".format( time.strftime("%H:%M:%S"),device.name, device.address))
                if len(advertisement_data.manufacturer_data.items()) > 0:
                    pass

        # if device.name.startswith("Tag"):
        #     print(device.name)

        if len(advertisement_data.manufacturer_data.items()) > 0 and btag:
            if advertisement_data.local_name == "Venus_0CDC7E44A066" or advertisement_data.local_name == "Linksys": return
            if True in [x[0] == int.from_bytes(b'\x4C\x00', byteorder="little", signed=True) for x in
                        advertisement_data.manufacturer_data.items()]:
                return  # Apple 76
            if True in [(x[0] == 6) for x in advertisement_data.manufacturer_data.items()]:
                return  # Microsoft 6
            if True in [x[0] == int.from_bytes(b'\x75\x00', byteorder="little", signed=True) for x in
                        advertisement_data.manufacturer_data.items()]:
                return  # samsung 117
            if True in [x[0] == int.from_bytes(b'\x02\x25', byteorder="little", signed=True) for x in
                        advertisement_data.manufacturer_data.items()]:
                return  # nesspresso 9474
            if True in [x[0] == int.from_bytes(b'\x5C\x00', byteorder="little", signed=True) for x in
                        advertisement_data.manufacturer_data.items()]:
                return  # linksys  92
            if not find_milwakiee:
                if (True in [x[0] == int.from_bytes(b'\x01\x65', byteorder="big", signed=True) for x in
                             advertisement_data.manufacturer_data.items()]) or (
                        True in [x[0] == int.from_bytes(b'\x01\x65', byteorder="little", signed=True) for x in
                                 advertisement_data.manufacturer_data.items()]):
                    return  # Milwakiew
            if (True in [x[0] == int.from_bytes(b'\xFD\x84', byteorder="big", signed=True) for x in
                         advertisement_data.manufacturer_data.items()]) or (
                    True in [x[0] == int.from_bytes(b'\xFD\x84', byteorder="little", signed=True) for x in
                             advertisement_data.manufacturer_data.items()]):
                return  # To;e
            if not find_dewalt:
                if True in [x[0] == int.from_bytes(b'\xFE\x00', byteorder="little", signed=True) for x in
                            advertisement_data.manufacturer_data.items()]:
                    bres = True  # Black & Decker
                    manID = int.from_bytes(b'\xFE\x00', byteorder="little", signed=True)

            # print("nservice_uuids %s"%advertisement_data.service_uuids)
            # print("nmanufacturer_data %s"%advertisement_data.manufacturer_data)
            # print("nmanufacturer_data %s" % advertisement_data.local_name)
            # print("nmanufacturer_data %s" % advertisement_data.service_data)
            # print("nmanufacturer_data %s" % advertisement_data.rssi)

            if not find_milwakiee:
                if True in ["a3e68a83-4c4d-4778-bd0a-829fb434a7a1" == i for i in advertisement_data.service_uuids]:
                    # print("")
                    bres = True

                if True in ["0000fdf5-0000-1000-8000-00805f9b34fb" == i for i in advertisement_data.service_uuids]:
                    # print("")
                    bres = True

                if (True in [x[0] == int.from_bytes(b'\x01\x65', byteorder="big", signed=True) for x in
                             advertisement_data.manufacturer_data.items()]) or (
                        True in [x[0] == int.from_bytes(b'\x01\x65', byteorder="little", signed=True) for x in
                                 advertisement_data.manufacturer_data.items()]):
                    bres = True
                    if True in [x[0] == int.from_bytes(b'\x01\x65', byteorder="big", signed=True) for x in
                                advertisement_data.manufacturer_data.items()]:
                        manID = int.from_bytes(b'\x01\x65', byteorder="big", signed=True)
                    if True in [x[0] == int.from_bytes(b'\x01\x65', byteorder="little", signed=True) for x in
                                advertisement_data.manufacturer_data.items()]:
                        manID = int.from_bytes(b'\x01\x65', byteorder="little", signed=True)

            if bres:  # and device.address not in ["C7:8E:58:90:4C:E3","F1:02:54:F8:9B:D1","76:79:15:85:6E:D8"]:
                val = str(advertisement_data.service_uuids) + device.address
                if val not in address:
                    address.append(str(advertisement_data.service_uuids) + device.address)
                    print("address %s" % device.address)
                    print("nmanufacturer_data %s" % advertisement_data.manufacturer_data)
                    print("[%d] service_uuids %s" % (
                    len(advertisement_data.service_uuids), advertisement_data.service_uuids))
                    # 25857 eq 165  = int.from_bytes(b'\x01\x65',byteorder="little",signed=True)
                    # manID=int.from_bytes(b'\x01\x65',byteorder="little",signed=True)
                    manufacturer_data = advertisement_data.manufacturer_data[manID]
                    print("manufacturer_data %s" % manufacturer_data)
                    mpbid = advertisement_data.manufacturer_data[manID][0:6]
                    print("mpbid %s\n" % mpbid)
        # #ibeacon =  ibeacon_format.parse(apple_data)
        # uuid = UUID(bytes=bytes(ibeacon.uuid))
        # print(f"UUID     : {uuid}")
        # print(f"Major    : {ibeacon.major}")
        # print(f"Minor    : {ibeacon.minor}")
        # print(f"TX power : {ibeacon.power} dBm")
        # print(f"RSSI     : {device.rssi} dBm")
        # print(47 * "-")
        # if ibeacon.minor==1:
        #     m1.append(device.rssi)
        #     p1.append(ibeacon.power)
        # if ibeacon.minor==2:
        #     m2.append(device.rssi)
        #     p2.append(ibeacon.power)
        else:
            if print_no_manufacturer_data:
                print("No manufacturer_data")
                print("                                                             address %s" % device.address)
                print(
                    "                                                             nservice_uuids %s" % advertisement_data.service_uuids)
                print("                                                             bluetooth_address %s" %
                      device.details[0].bluetooth_address)

    except KeyError:
        # Apple company ID (0x004c) not found
        pass
    except ConstError:
        # No iBeacon (type 0x02 and length 0x15)
        pass

async def notify_callback_notifications(sender: bleak.BleakGATTCharacteristic, data: bytearray):
    print("notify_callback_notifications")
    print(f"{sender}: {data}")

async def notify_callback_indications(sender: bleak.BleakGATTCharacteristic, data: bytearray):
    print("notify_callback_indications")
    print(f"{sender}: {data}")
async def notify_callback_Custom_Characteristic(sender: bleak.BleakGATTCharacteristic, data: bytearray):
    print("notify_callback_Custom_Characteristic")
    print(f"{sender}: {data}")


async def notify_callback_tag_id_Characteristic(sender: bleak.BleakGATTCharacteristic, data: bytearray):
    print("notify_callback_Custom_Characteristic")
    print(f"{sender}: {data}")

async def notify_callback_asset_id_Characteristic(sender: bleak.BleakGATTCharacteristic, data: bytearray):
    print("notify_callback_Custom_Characteristic")
    print(f"{sender}: {data}")

async def main():
    """Scan for devices."""

    scanner = BleakScanner()
    scanner.register_detection_callback(device_found)

    while True:
        await scanner.start()
        await asyncio.sleep(1.0)
        await scanner.stop()
        try:  # used try so that if user pressed other than the given key error will not be shown
            if keyboard.is_pressed('q'):  # if key 'q' is pressed
                print('You Pressed A Key!')
                break  # finishing the loop
        except:
            break

        devices = await scanner.discover()
        myDevice = None
        myDevice_1 = None
        scannaddress=[]
        connect=True
        for d in devices:
            # if KeyValueCoding.getKey(d.details, 'name') == 'awesomecoolphone':
            if d.name is not None:
                if d.name.startswith("BoldTag")  :
                    address=d.address
                    #print(d.name, address)
                    scannaddress.append({"address": address, "client": None, "connected": True,"device":d})
                    ix=len(scannaddress)-1
                    if connect:
                        conn = False
                        ncount = 0
                        while not conn and ncount < 3:
                            ncount=ncount+1
                            try:
                                    client= BleakClient(address)
                                    scannaddress[ix]["client"]=client
                                    scannaddress[ix]["connected"]=True
                                    conn=True
                            except Exception as e:
                                print(e)
                                scannaddress[ix]["connected"]=False
                    #print(scannaddress[ix])
                    char_uuid_enable_cte="c92c584f-7b9e-473a-ad4e-d9965e0cd678"
                    char_uuid_update_nfc="1b9bba4d-34c0-4542-8d94-0da1036bd64f"
                    char_uuid_tag_enabled="886eb62a-2c17-4e8e-9579-1c5483973577"


        if len(scannaddress)>0:
            for i in range(len(scannaddress)):
                tags=scannaddress[i]
                result,dfupdate=tag_command_update(tags, "enable_cte", new_value=1)
                result, dfupdate = tag_command_update(tags, "enable_cte", new_value=0)

            else:
                #print("..")
                pass
            # if d.name=="Blinky ExampleC":
            #     print('Found it')
            #     myDevice = d
            #     break
            # if d.name=="BoldTag":
            #     print('Found it')
            #     myDevice_1 = d
            #     # myDevice = d
            #     break
        if False:
            if myDevice_1 is not None:
                address = str(myDevice_1.address)  # details.adv.bluetooth_address)
                async with BleakClient(address) as client:
                    try:
                        connected =  client.is_connected
                        if connected:
                            print("Connected to Device")
                            char_uuid_asset_id="7db7b5e3-168e-48fd-aadb-94607557b832"
                            char_uuid_tag_id ="c01cdf18-2465-4df6-956f-fde4867e2bc1"
                            serv_uuid_Custom_Service = "87e29466-8be6-4ede-9ffb-04a7121938da"
                            char_uuid_update_nfc = "1b9bba4d-34c0-4542-8d94-0da1036bd64f"

                            asset_id = bytes( await client.read_gatt_char(char_uuid_asset_id))
                            print("asset_id: {0}".format(asset_id))

                            tag_id =bytes( await client.read_gatt_char(char_uuid_tag_id))
                            print("tag_id: {0}".format( tag_id))

                            svcs = await client.get_services()
                            print("Services:")
                            service=None
                            for service_1 in svcs:
                                # if service_1.uuid==serv_uuid_Throughput_Test_Service_uuid:
                                if service_1.uuid == serv_uuid_Custom_Service:
                                    service=service_1
                                    break
                            if service is not None:

                                #char_uuid_Custom_Characteristic
                                res = await client.write_gatt_char(service.get_characteristic(char_uuid_asset_id),bytearray("0888dfhfghdfghdfgh8888888", 'utf-8'),response=True)
                                print(res)
                                asset_id = bytes( await client.read_gatt_char(char_uuid_asset_id))
                                print("asset_id: {0}".format(asset_id))

                                res = await client.write_gatt_char(service.get_characteristic(char_uuid_tag_id),bytearray("AAA008", 'utf-8'),response=True)
                                print(res)
                                tag_id = bytes( await client.read_gatt_char(char_uuid_tag_id))
                                print("tag_id: {0}".format(tag_id))

                                res = await client.write_gatt_char(service.get_characteristic(char_uuid_update_nfc),bytearray("1", 'utf-8'),response=True)
                                print(res)
                                update_nfc = bytes( await client.read_gatt_char(char_uuid_tag_id))
                                print("char_uuid_update_nfc: {0}".format(update_nfc))

                                pass

                            while True:
                                if not connected:
                                    break
                                await asyncio.sleep(1.0)
                                # transmission_on = bytes( await client.read_gatt_char(char_uuid_Transmission_ON))
                                # print("transmission_on: {0}".format(transmission_on))
                                # Throughput_result = bytes( await client.read_gatt_char(char_uuid_Throughput_result))
                                # print("Throughput_result: {0}".format(Throughput_result))



                        else:
                            print(f"Failed to connect to Device")
                    except Exception as e:
                        print(e)
            if myDevice is not None:
                # address = str(myDevice.details.identifier)
                address= str(myDevice.address)# details.adv.bluetooth_address)
                async with BleakClient(address) as client:
                    svcs = await client.get_services()
                    print("Services:")
                    for service in svcs:
                        print("")
                        print("uuid:%s description:%s"%(service.uuid,service.description))
                        characteristics = service.characteristics
                        if characteristics  is not None:
                            print("characteristics:")
                            for characteristic in characteristics:
                                print("uuid:%s description:%s"%(characteristic.uuid,characteristic.description))
                                if characteristic.uuid=="be6b6be1-cd8a-4106-9181-5ffe2bc67718":
                                    print("d")
                                if characteristic.uuid=="efe221d3-2f75-4e8e-9e42-1e2e968b3628":
                                    print("ff")
                                    # client.read_gatt_char(service.get_characteristic(characteristic.uuid))
                                    # client.write_gatt_char(service.get_characteristic(characteristic.uuid),b'HHHH',response=True)
                                    model_number = await client.read_gatt_char(characteristic.uuid)
                                    print("Model Number: {0}".format("".join(map(chr, model_number))))
                                    res = await client.write_gatt_char(service.get_characteristic(characteristic.uuid), b'HHasdfasdfasdfHH',
                                                           response=True)
                                    print(res)

            print("-----------------------------------------")
asyncio.run(main())
print('ff')