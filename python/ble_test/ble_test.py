# This is a working prototype. DO NOT USE IT IN LIVE PROJECTS
# https://github.com/bowdentheo/BLE-Beacon-Scanner/blob/master/ScanUtility.py

# https://github.com/hbldh/bleak
# https://koen.vervloesem.eu/blog/decoding-bluetooth-low-energy-advertisements-with-python-bleak-and-construct/
# import const

import asyncio

import bleak
from bleak import BleakScanner
from bleak import BleakClient
from uuid import UUID
from construct import Array, Byte, Const, Int8sl, Int16ub, Struct
from construct.core import ConstError
import keyboard
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData



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

address_log=[]
def device_found(device: BLEDevice, advertisement_data: AdvertisementData):
    """Decode iBeacon."""
    try:
        global address_log
        bres = False
        # print("device.name -------------------> %s" % device.name)
        # print("nservice_uuids %s" % advertisement_data.service_uuids)
        # print("nmanufacturer_data %s" % advertisement_data.manufacturer_data)
        # print("local_name --------->>%s" % advertisement_data.local_name)
        # print("service_data %s" % advertisement_data.service_data)
        # print("rssi %s" % advertisement_data.rssi)

        if device.name is not None:
            if device.name.startswith("TGS"):
                address=device.address.replace(":","")
                rssi=advertisement_data.rssi
                print("RSSI {0}:{1}".format(address,rssi))
                if address not in address_log:
                    address_log.append(address)
                print("\n\n {}".format(address_log))


        # if device.name.startswith("Tag"):
        #     print(device.name)

        if len(advertisement_data.manufacturer_data.items()) > 0:
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
        for d in devices:
            # if KeyValueCoding.getKey(d.details, 'name') == 'awesomecoolphone':
            print(d.name)
            # if d.name=="Blinky ExampleC":
            #     print('Found it')
            #     myDevice = d
            #     break
            if d.name=="TGS_Tag_7":
                print('Found it')
                myDevice_1 = d
                # myDevice = d
                break
        if myDevice_1 is not None:
            address = str(myDevice_1.address)  # details.adv.bluetooth_address)
            async with BleakClient(address) as client:
                try:
                    connected =  client.is_connected
                    if connected:
                        print("Connected to Device")
                        char_uuid_notifications_data_array="47b73dd6-dee3-4da1-9be0-f5c539a9a4be"
                        char_uuid_indications_data_array="6109b631-a643-4a51-83d2-2059700ad49f"
                        char_uuid_Transmission_ON="be6b6be1-cd8a-4106-9181-5ffe2bc67718"
                        char_uuid_Throughput_result="adf32227-b00f-400c-9eeb-b903a6cc291b"
                        char_uuid_Custom_Characteristic="22dc182e-95fa-4b5a-9230-867655b7b261"
                        char_uuid_tag_id="c01cdf18-2465-4df6-956f-fde4867e2bc1"
                        char_uuid_asset_id = "7db7b5e3-168e-48fd-aadb-94607557b832"
                        serv_uuid_Custom_Service = "87e29466-8be6-4ede-9ffb-04a7121938da"


                        await client.start_notify(char_uuid_notifications_data_array, notify_callback_notifications)
                        await client.start_notify(char_uuid_indications_data_array, notify_callback_indications)
                        await client.start_notify(char_uuid_Custom_Characteristic, notify_callback_Custom_Characteristic)
                        await client.start_notify(char_uuid_tag_id,
                                                  notify_callback_tag_id_Characteristic)
                        await client.start_notify(char_uuid_asset_id,
                                                  notify_callback_asset_id_Characteristic)

                        transmission_on =bytes(  await client.read_gatt_char(char_uuid_Transmission_ON))
                        print("transmission_on: {0}".format(  transmission_on))


                        serv_uuid_Throughput_Test_Service_uuid = "bbb99e70-fff7-46cf-abc7-2d32c71820f2"
                        serv_uuid_Throughput_Information_Service="ba1e0e9f-4d81-bae3-f748-3ad55da38b46"
                        serv_uuid_Custom_Service="0684a9ec-5f5b-4078-91bb-721b52942c66"


                        char_uuid_PDU_size="30cc364a-0739-268c-4926-36f112631e0c"
                        PDU_size = bytes( await client.read_gatt_char(char_uuid_PDU_size))
                        print("PDU_size: {0}".format(PDU_size))

                        char_uuid_Connection_interval="0a32f5a6-0a6c-4954-f413-a698faf2c664"
                        Connection_interval =bytes( await client.read_gatt_char(char_uuid_Connection_interval))
                        print("Connection_interval: {0}".format( Connection_interval))


                        char_uuid_Responder_latency="ff629b92-332b-e7f7-975f-0e535872ddae"
                        Responder_latency =bytes( await client.read_gatt_char(char_uuid_Responder_latency))
                        print("Responder_latency: {0}".format(Responder_latency))


                        char_uuid_Supervision_timeout="67e2c4f2-2f50-914c-a611-adb3727b056d"
                        Supervision_timeout =bytes(await client.read_gatt_char(char_uuid_Supervision_timeout))
                        print("Supervision_timeout: {0}".format(Supervision_timeout))

                        char_uuid_MTU_size="3816df2f-d974-d915-d26e-78300f25e86e"
                        MTU_size = bytes(await client.read_gatt_char(char_uuid_MTU_size))
                        print("MTU_size: {0}".format(MTU_size))


                        svcs = await client.get_services()
                        print("Services:")
                        service=None
                        for service_1 in svcs:
                            # if service_1.uuid==serv_uuid_Throughput_Test_Service_uuid:
                            if service_1.uuid == serv_uuid_Custom_Service:
                                service=service_1
                                break
                        if service is not None:
                            # res = await client.write_gatt_char(service.get_characteristic(char_uuid_Transmission_ON),b'\x01',response=True)
                            # print(res)
                            # transmission_on = bytes( await client.read_gatt_char(char_uuid_Transmission_ON))
                            # print("transmission_on: {0}".format( transmission_on))

                            # res = await client.write_gatt_char(service.get_characteristic(char_uuid_notifications_data_array),bytearray("08888888888888888888", 'utf-8'),response=True)
                            # print(res)
                            # notifications_data_array = bytes( await client.read_gatt_char(char_uuid_notifications_data_array))
                            # print("notifications_data_array: {0}".format(notifications_data_array))

                            #char_uuid_Custom_Characteristic
                            res = await client.write_gatt_char(service.get_characteristic(char_uuid_Custom_Characteristic),bytearray("08888888888888888888", 'utf-8'),response=True)
                            print(res)
                            Custom_Characteristic = bytes( await client.read_gatt_char(char_uuid_Custom_Characteristic))
                            print("Custom_Characteristic: {0}".format(Custom_Characteristic))

                            res = await client.write_gatt_char(service.get_characteristic(char_uuid_tag_id),bytearray("088888", 'utf-8'),response=True)
                            print(res)
                            tag_id_Characteristic = bytes( await client.read_gatt_char(char_uuid_tag_id))
                            print("Custom_Characteristic: {0}".format(tag_id_Characteristic))

                            res = await client.write_gatt_char(service.get_characteristic(char_uuid_asset_id),bytearray("088888", 'utf-8'),response=True)
                            print(res)
                            asset_id_Characteristic = bytes( await client.read_gatt_char(char_uuid_asset_id))
                            print("Custom_Characteristic: {0}".format(asset_id_Characteristic))


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

r = min(len(m2), len(m1))
rssi_data = {a: {} for a in const.ANCHORS}

anchor_mac = '1'
device_mac = '1'
for a in range(r):
    rssi = m1[a]
    if device_mac in rssi_data[anchor_mac]:
        rssi_data[anchor_mac][device_mac].append(rssi)
    else:
        ## Filtering out target nodes
        rssi_data[anchor_mac][device_mac] = [rssi]

anchor_mac = '2'
device_mac = '1'
for a in m2:
    rssi = m2[a]
    if device_mac in rssi_data[anchor_mac]:
        rssi_data[anchor_mac][device_mac].append(rssi)
    else:
        ## Filtering out target nodes
        rssi_data[anchor_mac][device_mac] = [rssi]

# https://github.com/ani8897/RSSI-based-Localization-using-ESP32/blob/master/backend/util.py
import const
from math import exp
from scipy.optimize import minimize


def sq_dist(a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


def dist(a, b):
    return sq_dist(a, b) ** 0.5


def rssi_model(rssi):
    return exp((rssi - const.A) / const.B)


def get_position(device_mac):
    if device_mac in const.positions:
        return const.positions[device_mac][0]
    else:
        return const.ANCHORS['1']


def localize(rssi_data):
    """
    Localizes devices based on the rssi data passed
    """

    def loss(e, device_mac):
        return sum([(dist(e, const.ANCHORS[a]) - rssi_model(rssi_data[a][device_mac])) ** 2 for a in const.ANCHORS])

    anchor_check = {}
    for a in rssi_data:
        for d in rssi_data[a]:

            if d in anchor_check:
                anchor_check[d].append(a)
            else:
                anchor_check[d] = [a]

            if len(anchor_check[d]) == len(const.ANCHORS):
                res = minimize(loss, get_position(d), args=(d))
                const.positions[d] = (res.x, res.success)