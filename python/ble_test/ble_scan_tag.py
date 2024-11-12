
import asyncio
from xml.etree.ElementTree import indent

#from tarfile import TruncatedHeaderError
import sqlite3
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
import zlib


class ble_tag:

    char_uuid = {}
    char_uuid[0] = {"id": "tag_id", "uuid": "c01cdf18-2465-4df6-956f-fde4867e2bc1", "value": "", "scan": True,
                    'type': "UTF-8", "length": 50, "data_type": "base","NFC":False}
    char_uuid[1] = {"id": "asset_id", "uuid": "7db7b5e3-168e-48fd-aadb-94607557b832", "value": "", "scan": True,
                    'type': "UTF-8", "length": 150, "data_type": "base","NFC":False}
    char_uuid[2] = {"id": "update_nfc", "uuid": "1b9bba4d-34c0-4542-8d94-0da1036bd64f", "value": "", "scan": False,
                    'type': "HEX", "length": 1, "data_type": "configuration","NFC":False}
    char_uuid[3] = {"id": "ble_data_crc", "uuid": "cfdd75b8-5ed3-43cd-96cd-35129f648c5d", "value": "", "scan": False,
                    'type': "UTF-8", "length": 8, "data_type": "base","NFC":False}
    char_uuid[4] = {"id": "certificate_id", "uuid": "fd052ad3-b4d3-426f-be19-b6b3107ab535", "value": "", "scan": True,
                    'type': "UTF-8", "length": 60, "data_type": "base","NFC":False}
    char_uuid[5] = {"id": "type", "uuid": "d1251886-0135-4757-a6a4-233ed79914f3", "value": "", "scan": True,
                    'type': "UTF-8", "length": 150, "data_type": "base","NFC":False}
    char_uuid[6] = {"id": "expiration_date", "uuid": "04f7c038-5717-4da6-b0af-4441388bf938", "value": "", "scan": True,
                    'type': "UTF-8", "length": 10, "data_type": "base","NFC":False}
    char_uuid[7] = {"id": "color", "uuid": "3ef6ebcc-db6e-4b65-ab42-81bedf9c95a5", "value": "", "scan": True,
                    'type': "UTF-8", "length": 20, "data_type": "base","NFC":False}
    char_uuid[8] = {"id": "series", "uuid": "b68a7594-7bf0-4da5-9067-cf986fa2e91d", "value": "", "scan": True,
                    'type': "UTF-8", "length": 32, "data_type": "base","NFC":False}
    char_uuid[9] = {"id": "asset_images_file_extension", "uuid": "c53ff832-45ae-4a94-8bb9-26bea6b64c2c", "value": "",
                    "scan": True, 'type': "UTF-8", "length": 3, "data_type": "base","NFC":False}
    char_uuid[10] = {"id": "read_nfc", "uuid": "d2fe9b8c-fdfa-4006-b1ef-44969591fb1b", "value": "", "scan": True,
                     'type': "HEX", "length": 1, "data_type": "base","NFC":False}
    char_uuid[11] = {"id": "certification_company_name", "uuid": "d2bcecac-383d-4224-a60b-bb35ebc4defb", "value": "",
                     "scan": True, 'type': "UTF-8", "length": 50, "data_type": "detail","NFC":False}
    char_uuid[12] = {"id": "certification_company_id", "uuid": "91cdf87d-a278-486f-942c-ab1816565dc2", "value": "",
                     "scan": True, 'type': "UTF-8", "length": 50, "data_type": "detail","NFC":False}
    char_uuid[13] = {"id": "certification_place", "uuid": "b184ba24-a2ab-460d-8cb5-d9424017d730", "value": "",
                     "scan": True, 'type': "UTF-8", "length": 50, "data_type": "detail","NFC":False}
    char_uuid[14] = {"id": "certification_date", "uuid": "5d5d87d9-eafe-4197-8893-ffa5576cf657", "value": "",
                     "scan": True, 'type': "UTF-8", "length": 10, "data_type": "detail","NFC":False}
    char_uuid[15] = {"id": "test_type", "uuid": "183d8f3e-8276-4b6f-ac45-beb289ab4e21", "value": "", "scan": True,
                     'type': "UTF-8", "length": 150, "data_type": "detail","NFC":False}
    char_uuid[16] = {"id": "asset_diameter", "uuid": "b21f382a-9115-4236-958d-df714beee49a", "value": "", "scan": True,
                     'type': "UTF-8", "length": 10, "data_type": "detail","NFC":False}
    char_uuid[17] = {"id": "asset_comment", "uuid": "1984cab5-5f24-4e98-87d8-0559c96980d5", "value": "", "scan": True,
                     'type': "UTF-8", "length": 20, "data_type": "detail","NFC":False}
    char_uuid[18] = {"id": "batch_id", "uuid": "34992c7e-8d34-4b87-b9c8-8fbcc3641a27", "value": "", "scan": True,
                     'type': "UTF-8", "length": 50, "data_type": "detail","NFC":False}
    char_uuid[19] = {"id": "batch_date", "uuid": "9ac91987-9da4-41b3-a60c-5c407bc7881d", "value": "", "scan": True,
                     'type': "UTF-8", "length": 10, "data_type": "detail","NFC":False}
    char_uuid[20] = {"id": "machine_id", "uuid": "ed5c5d2b-486c-46ce-9812-6fc09d0a64b8", "value": "", "scan": True,
                     'type': "UTF-8", "length": 50, "data_type": "detail","NFC":False}
    char_uuid[21] = {"id": "status_code", "uuid": "d469aa23-63da-42c9-83ed-e2dc5601acd7", "value": "", "scan": True,
                     'type': "UTF-8", "length": 4, "data_type": "configuration","NFC":False}
    char_uuid[22] = {"id": "asset_images_crc", "uuid": "4bdbf8ed-53a9-4518-a907-c4376e43b62d", "value": "",
                     "scan": True, 'type': "UTF-8", "length": 4, "data_type": "detail","NFC":False}
    char_uuid[23] = {"id": "logo_images_crc", "uuid": "30dd3370-65e7-48ec-871d-1994bc9cc2fc", "value": "", "scan": True,
                     'type': "UTF-8", "length": 4, "data_type": "detail","NFC":False}
    char_uuid[24] = {"id": "signature_images_crc", "uuid": "028f73b8-e36b-4cd9-b99b-51f946e8888b", "value": "",
                     "scan": True, 'type': "UTF-8", "length": 4, "data_type": "detail","NFC":False}
    char_uuid[25] = {"id": "owner_company_name", "uuid": "5b7ef22d-72a9-490c-bdba-1bd225531e6f", "value": "",
                     "scan": True, 'type': "UTF-8", "length": 50, "data_type": "detail","NFC":False}
    char_uuid[26] = {"id": "owner_data", "uuid": "e46f56de-7341-4231-9f29-b8ae5e470a93", "value": "", "scan": True,
                     'type': "UTF-8", "length": 50, "data_type": "detail","NFC":False}
    char_uuid[27] = {"id": "ndir_id", "uuid": "8024d4a4-f212-497b-8499-4b1ebb467b48", "value": "", "scan": True,
                     'type': "UTF-8", "length": 50, "data_type": "detail","NFC":False}
    char_uuid[28] = {"id": "tag_mac", "uuid": "6a103778-d584-4ce6-b3e2-94f417673cfc", "value": "", "scan": True,
                     'type': "UTF-8", "length": 20, "data_type": "configuration","NFC":False}
    char_uuid[29] = {"id": "enable_cte", "uuid": "c92c584f-7b9e-473a-ad4e-d9965e0cd678", "value": "", "scan": True,
                     'type': "HEX", "length": 1, "data_type": "configuration","NFC":False}
    char_uuid[30] = {"id": "tag_enabled", "uuid": "886eb62a-2c17-4e8e-9579-1c5483973577", "value": "", "scan": True,
                     'type': "HEX", "length": 1, "data_type": "configuration","NFC":False}
    char_uuid[31] = {"id": "tag_advertisement_period", "uuid": "4f9c97c2-41c2-4215-ab22-8c0a9d3ba777", "value": "",
                     "scan": True, 'type': "HEX", "length": 4, "data_type": "configuration","NFC":False}
    char_uuid[32] = {"id": "ble_on_period", "uuid": "b13603ed-2ac4-4ee1-9b4d-21ee264543a4", "value": "", "scan": True,
                     'type': "HEX", "length": 4, "data_type": "configuration","NFC":False}
    char_uuid[33] = {"id": "ble_on_wakeup_period", "uuid": "41af4710-5494-4793-860f-31031c3148bd", "value": "",
                     "scan": True, 'type': "HEX", "length": 4, "data_type": "configuration","NFC":False}
    char_uuid[34] = {"id": "ble_off_period", "uuid": "ed407a07-5109-4525-894a-6182aacf8237", "value": "", "scan": True,
                     'type': "HEX", "length": 4, "data_type": "configuration","NFC":False}
    char_uuid[35] = {"id": "tag_periodic_scan", "uuid": "f178d4ee-af0a-418f-b302-47c051578047", "value": "",
                     "scan": True, 'type': "HEX", "length": 1, "data_type": "configuration","NFC":False}
    char_uuid[36] = {"id": "battery_voltage", "uuid": "9b9dcb7a-b2f5-4a3d-8e59-b96a9b88b6ef", "value": "", "scan": True,
                     'type': "HEX", "length": 4, "data_type": "configuration","NFC":False}
    char_uuid[37] = {"id": "read_battery_voltage", "uuid": "914254cd-dafe-4bb8-8517-048adb4e08ab", "value": "",
                     "scan": True, 'type': "HEX", "length": 1, "data_type": "configuration","NFC":False}
    char_uuid[38] = {"id": "altitude", "uuid": "6d139387-9f68-4827-8442-641956a94979", "value": "", "scan": True,
                     'type': "HEX", "length": 4, "data_type": "configuration","NFC":False}
    char_uuid[39] = {"id": "moved", "uuid": "e410f434-a1f1-4088-9578-19d08830a489", "value": "", "scan": True,
                     'type': "HEX", "length": 1, "data_type": "configuration","NFC":False}
    char_uuid[40] = {"id": "tag_firmware", "uuid": "ae795504-8f02-4d4c-bd37-b46935193fd2", "value": "", "scan": True,
                     'type': "UTF-8", "length": 10, "data_type": "configuration", "NFC": False}
    char_uuid[41] = {"id": "end_transac", "uuid": "4535350a-0794-43e5-89f6-74eae561a6aa", "value": "", "scan": False,
                     'type': "HEX", "length": 1, "data_type": "configuration", "NFC": False}


    char_uuid_nfc = ["certification_company_name", "certification_company_id", "certification_place",
                     "certification_date",
                     "certificate_id", "expiration_date", "test_type", "asset_id",
                     "tag_id", "type", "color", "series",
                     "asset_diameter", "asset_comment", "batch_id", "batch_date",
                     "machine_id", "status_code", "ble_data_crc", "asset_images_crc",
                     "logo_images_crc", "signature_images_crc", "owner_company_name", "owner_data",
                     "ndir_id", "asset_images_file_extension", "tag_mac", "gattdb_tag_periodic_scan"]

    # serv_uuid_Custom_Service = "87e29466-8be6-4ede-9ffb-04a7121938da"


    def __init__(self,device,webapp,index,scanner_param,serv_uuid_Custom_Service,max_connect_retries=4,directory="//"):
        self.device=device
        self.address=device.address
        self.connected=False
        self.client=None
        self.index=index
        self.name=device.name
        self.rssi_host_scan = None
        self.last_seen=None
        self.ble_data_crc="-"
        self.asset_images_crc="-"
        self.rssi_tag_scan=None
        self.webapp=webapp
        self.serv_uuid_Custom_Service=serv_uuid_Custom_Service
        self.directory=directory
        self.scanner_param=scanner_param
        self.error=None
        self.gatewaydb = gatewaydb()
        self.gatewaydb.set_mac(self.address)
        self.csv_row_previous = {}
        self.csv_row_last = {}
        self.csv_row = self.gatewaydb.csv_row
        # self.csv_cfg_row = self.gatewaydb.csv_cfg_row
        # self.csv_det_row = self.gatewaydb.csv_det_row
        self.connect_retries=0
        self.max_connect_retries=max_connect_retries
        try:
            for ix in self.char_uuid.keys():
                if self.char_uuid[ix]["id"] in self.char_uuid_nfc:
                    self.char_uuid[ix]["NFC"]=True
        except Exception as e:
            print(e)

        self.set_client()
        # self.client = BleakClient(self.address)
        # self.client.set_disconnected_callback(self.handle_disconnect)

    def set_client(self):
        self.client = BleakClient(self.address)
        self.client.set_disconnected_callback(self.handle_disconnect)
        self.connected=False
    def set_custom_service(self,custom_service):
        self.custom_service=custom_service

    def read_db(self):
        try:
            for ix in self.char_uuid.keys():
                if self.char_uuid[ix]["id"] in self.char_uuid_nfc:
                    self.char_uuid[ix]["NFC"]=True
        except Exception as e:
            print(e)

    def handle_disconnect(self, device):
        try:
            self.connected=False
        except Exception as e:
            print(e)

    # async def connect(self,max_retry=3, timeout=15):
    #     # res_scan=True
    #     # if index is not None:
    #     #     res_scan=self.set_current(index)
    #     # res=False
    #     # if res_scan:
    #     ncount = 0
    #     res=self.connected
    #     error=False
    #     try:
    #         # if self.client  is not None:
    #         #     try:
    #         #         res=await self.client.is_connected()
    #         #     except Exception as e:
    #         #         print(e)
    #         #         res=False
    #         #         error=True
    #         #
    #         # if error == True:
    #         #     try:
    #         #         self.client.disconnect()
    #         #         self.client=None
    #         #     except Exception as e:
    #         #         print(e)
    #
    #         res=self.connected
    #         while res!=True and ncount < max_retry : # and self.connect_retries<self.max_connect_retries:
    #             print("connecting to {} retry:{}".format(self.address,ncount ))
    #             ncount = ncount + 1
    #             try:
    #                 if self.client is None:
    #                     self.client = BleakClient(self.address)
    #                     self.client.set_disconnected_callback(self.handle_disconnect)
    #                 #self.client.set_disconnected_callback(self.disconnected_callback)
    #                 #await self.client.connect()
    #                 self.connect_retries=self.connect_retries+1
    #                 # await asyncio.wait_for(self.client.connect(), timeout=timeout)
    #                 res=await self.client.connect()
    #                 # self.connected= await self.client.is_connected()
    #                 self.connected=res
    #                 if res:
    #                     self.webapp.print_statuslog("BoldTag {} connected!".format(self.address))
    #                 else:
    #                     self.webapp.print_statuslog("BoldTag {} fail to connect".format(self.address))
    #             except Exception as e:
    #                 print(e)
    #                 self.webapp.print_statuslog("BoldTag {} dormant - {}".format(self.address,e))
    #
    #
    #             if self.connected:
    #                 print("BoldTag {} gathering services".format(self.address))
    #                 svcs = await self.client.get_services()
    #                 for service_1 in svcs:
    #                     # if service_1.uuid==serv_uuid_Throughput_Test_Service_uuid:
    #                     if service_1.uuid == self.scanner_param["serv_uuid_Custom_Service"]:
    #                         self.custom_service = service_1
    #                         break
    #                 # self.update_current()
    #
    #     except Exception as e:
    #         print(e)
    #         self.webapp.print_statuslog("Connection error for BoldTag  {} ".format(self.address))
    #     return res

    async def check_disconnect(self,timeout=15):
        try:
            # connected = False
            # if self.client is None:
            #     try:
            #         self.client = BleakClient(self.address)
            #         connected = await self.client.is_connected()
            #     except Exception as e:
            #         print(e)
            #         connected = False
            # ble_data_crc = ""
            # if self.client is not None:
            connected = self.connected #await self.client.is_connected()
            if not connected:
                try:
                    # await asyncio.wait_for(self.client.connect(), timeout=timeout) #await self.client.connect()
                    res=await self.client.connect()
                    self.connected = res #await self.client.is_connected()
                except Exception as e:
                    print(e)
                    connected = False
            try:
                char_uuid = self.filter_db(id="ble_data_crc")[0]["uuid"]
                self.ble_data_crc = bytes(await self.client.read_gatt_char(char_uuid))
                connected = True
            except Exception as e:
                print(e)
                connected = False

        except Exception as e:
            print(e)

            self.connected = connected
            # self.update_current()

        return self.connected, self.ble_data_crc

    def tag_command_update(self,uuid_id, new_value=None):
        res=None
        try:
            result=None
            action = "UPDATE"
            #char_uuid_id=[char_uuid[x] for x in char_uuid.keys() if char_uuid[x]["id"]=="enable_cte"][0]
            dfupdate = pd.DataFrame(columns=["id",uuid_id,"status"])
            new_row = {'id': uuid_id, uuid_id : new_value,'status': ""}
            dfupdate = dfupdate.append(new_row, ignore_index=True)
            result,dfupdate_read=self.tag_functions( action=action, dfupdate=dfupdate)
        except Exception as e:
            print(e)

        return result,dfupdate


    async def tag_functions(self, action="READ",
                            uuid_filter_id=None, uuid_data_type_filter="base",
                            init_location=False,
                            dfupdate=None, keep_connected=True,csv_read_data=[],
                            param_enable_disable_tags=False,janhors_processed=[],start_mqtt=False, columnsIds_filter=[]):

        client = self.client
        device = self.device
        service=self.custom_service

        app = self.webapp


        address=device.address
        # if uuid_data_type_filter=='base':
        #     csv_row_new = self.csv_row.copy()
        # elif uuid_data_type_filter=='detail':
        #     csv_row_new = self.csv_det_row.copy()
        # elif uuid_data_type_filter=='configuration':
        #     csv_row_new = self.csv_cfg_row.copy()
        # else:
        csv_row_new = self.csv_row.copy()
        # if columnsIds_filter is None:
        #     if uuid_data_type_filter=='base':
        #         columnsIds_filter = self.gatewaydb.scan_columnIds.copy()
        #     elif uuid_data_type_filter=='detail':
        #         columnsIds_filter = self.gatewaydb.scan_det_columnIds.copy()
        #     elif uuid_data_type_filter=='configuration':
        #         columnsIds_filter = self.gatewaydb.scan_cfg_columnIds.copy()
        #     else:
        #         columnsIds_filter = self.gatewaydb.scan_columnIds.copy()

        csv_row_new["mac"] = address
        csv_row_new["name"] = device.name
        manufacturer_data="0000000000000000"
        try:
            manufacturer_data=device.metadata["manufacturer_data"][767].hex()
        except Exception as e:
            print(e)
        csv_row_new["manufacturer_data"] =manufacturer_data
        csv_row_new["rssi_host"]=device.rssi

        csv_row_new["asset_images_crc"] =self.get_asset_images_crc() if  manufacturer_data=="0000000000000000" else manufacturer_data[:8] #
        csv_row_new["ble_data_crc"] =self.get_ble_data_crc() if  manufacturer_data=="0000000000000000" else  manufacturer_data[8:]#


        #serv_uuid_Custom_Service=self.scanner_param["serv_uuid_Custom_Service"]
        disableCTE_duringlocation=self.scanner_param["disableCTE_duringlocation"]
        keepactive_all_CTE_during_location =self.scanner_param["keepactive_all_CTE_during_location"]
        use_MQTT=self.scanner_param["use_MQTT"]
        mqttclient=self.scanner_param["mqttclient"]
        keep_mqtt_on =self.scanner_param["keep_mqtt_on"]
        wait_for_mqtt_angles =self.scanner_param["wait_for_mqtt_angles"]
        CTE_Wait_Time_prescan =self.scanner_param["CTE_Wait_Time_prescan"]
        CTE_Wait_Time =self.scanner_param["CTE_Wait_Time"]
        result = False
        dfupdate_read=None
        recupdate = None
        devices_processed_location=None
        ble_data_crc=None
        if service is not None:
            # try to connect
            try:

                last_seen=time.strftime("%m/%d/%Y %H:%M:%S")
                csv_row_new["last_seen"] = last_seen
                result = True
                self.last_seen=last_seen
                myDevice_1_address = device.address
                char_uuid_enable_cte = self.filter_db(id="enable_cte")[0]["uuid"]
                char_uuid_update_nfc = self.filter_db(id="update_nfc")[0]["uuid"]
                char_uuid_ble_data_crc= self.filter_db(id="ble_data_crc")[0]["uuid"]

                nconerr = -1
                # if client is not None:
                #     connected = client.is_connected
                #     if not connected:
                #         try:
                #             await client.connect()
                #             connected = client.is_connected
                #         except Exception as e:
                #             print(e)
                # else:
                #     try:
                #         connected = False
                #         client = BleakClient(address)
                #         connected = client.is_connected
                #     except Exception as e:
                #         print(e)
                data_valid = False
                # connected,ble_data_crc=await self.check_disconnect()
                # if connected:
                #     csv_row_new["ble_data_crc"]=ble_data_crc

                if "row_crc32" in list(self.csv_row_last.keys()):
                    if self.csv_row_last["row_crc32"]==csv_row_new["ble_data_crc"]:
                        data_valid=True
                if not data_valid:
                    if "row_crc32" in list(self.csv_row_previous.keys()):
                        if self.csv_row_previous["row_crc32"] == csv_row_new["ble_data_crc"]:
                            data_valid = True
                            self.csv_row_last=self.csv_row_previous.copy()
                if not self.csv_row_last=={}:
                    csv_row_new=self.csv_row_last.copy()
                result= self.connected
                if result:

                    print("Connected to Device")
                    print("Executing action {}".format(action))
                    if (app is not None): app.print_statuslog("Executing action {}".format(action))

                    if action == "READ" and not data_valid or action != "READ":

                        if (action == "READ"):
                            if service is not None:

                                scan_list = self.filter_db(id=uuid_filter_id, data_type=uuid_data_type_filter, scan=True)
                                scan_list.extend(self.filter_db(id="status_code"))
                                for k in range(len(scan_list)):
                                    try:
                                        char_uuid_id = scan_list[k]['uuid']
                                        id = scan_list[k]['id']
                                        scan = scan_list[k]['scan']
                                        # char_uuid_val = bytes(await client.read_gatt_char(char_uuid_id))
                                        char_uuid_val = await self.readgatt(char_uuid_id)
                                        if char_uuid_val is not None:
                                            char_uuid_val=bytes(char_uuid_val)
                                        print("{0} ({1}): {2}".format(id, scan, char_uuid_val))
                                        if scan and (id in columnsIds_filter or len(columnsIds_filter)==0):
                                            if (scan_list[k]['type'] == 'HEX'):
                                                val = int.from_bytes(char_uuid_val, byteorder='big')
                                            else:
                                                if type(char_uuid_val) is bytes:
                                                    if len( char_uuid_val.split(b'\x00')[0])>0:
                                                        val = char_uuid_val.split(b'\x00')[0].decode("Utf-8") #char_uuid_val.decode('utf-8')
                                                    else:
                                                        val = ""
                                                else:
                                                    val = str(char_uuid_val)
                                            scan_list[k]['value'] = val
                                            if (csv_row_new is not None):
                                                if id in csv_row_new.keys():
                                                    csv_row_new[id] = val
                                                    #TODO for the moement hex
                                                    # if id=="tag_id":
                                                    #     try:
                                                    #         csv_row_new[id]=int(val, 16)
                                                    #     except Exception as e:
                                                    #         print(e)
                                    except Exception as e:
                                        if type(e) is  bleak.exc.BleakDeviceNotFoundError: #THE_OBJECT_HAS_BEEN_CLOSED = 22
                                            msg="Connection closed for address:{} id:{} char_uuid_id:{}".format(address, id, char_uuid_id)
                                            if (app is not None): app.print_statuslog(msg)
                                            print(msg)
                                            print(e)
                                            # self.connected = False
                                            # self.client = None
                                            # self.update_current()
                                            break
                                        elif type(e) is OSError:
                                            if e.strerror== 'The object has been closed':
                                                msg = "Connection closed for address:{} id:{} char_uuid_id:{}".format(
                                                    address, id, char_uuid_id)
                                                if (app is not None): app.print_statuslog(msg)
                                                # self.connected = False
                                                # self.client = None
                                        else:
                                            msg="error address:{} id:{} char_uuid_id:{}".format(address, id, char_uuid_id)
                                            if (app is not None): app.print_statuslog(msg)
                                            print(msg)
                                            print(e)

                                        result = False

                                try:
                                    id = "tag_enabled"
                                    char_uuid_id = self.filter_db(id=id, data_type=None, scan=True)[0]["uuid"]
                                    valread_raw = await self.readgatt(char_uuid_id) #await client.read_gatt_char(char_uuid_id)
                                    if valread_raw is not None:
                                        if type(valread_raw) is bytearray:
                                            valread = int.from_bytes(bytes(valread_raw))
                                        else:
                                            pass
                                    else:
                                        valread = bytes(b'')
                                    csv_row_new[id] = valread
                                except Exception as e:
                                    print(e)

                                if param_enable_disable_tags!='none':
                                    try:
                                        id = "tag_enabled"
                                        char_uuid=self.filter_db(id=id, data_type=None, scan=True)
                                        if len(char_uuid)>0:
                                            char_uuid=char_uuid[0]
                                            char_uuid_id=char_uuid["uuid"]
                                            if param_enable_disable_tags == 'enable':
                                                newval=1
                                            else:
                                                newval=0
                                            res = await client.write_gatt_char(service.get_characteristic(char_uuid_id),
                                                            newval.to_bytes(char_uuid['length'], byteorder='big',
                                                                    signed=False),response=True)

                                            valread_raw = await self.readgatt(char_uuid_id) #await client.read_gatt_char(char_uuid_id)
                                            if valread_raw is not None:
                                                if type(valread_raw) is bytearray:
                                                    valread = int.from_bytes(bytes(valread_raw))
                                                else:
                                                    pass
                                            else:
                                                valread = bytes(b'')
                                            csv_row_new[id] = valread
                                            if valread==newval:
                                                msg="tag enabled/diabled successful for :{} value:{} ".format(address, valread)
                                            else:
                                                msg = "tag enabled/diabled failed for :{} value:{} ".format(address,valread)
                                            if (app is not None): app.print_statuslog(msg)
                                            print(msg)

                                    except Exception as e:
                                        if (app is not None): app.print_statuslog(
                                            "error at param_enable_disable_tags address:{} ".format(address, ))
                                        print("error at param_enable_disable_tags address:{}".format(address,))
                                        print(e)
                                if result:
                                    csv_row_new["status"]="read"
                                else:
                                    csv_row_new["status"]="read error"
                                self.csv_row_previous = self.csv_row_last.copy()
                                csv_row_new_crc = self.gatewaydb.generate_crc32(csv_row_new)
                                if csv_row_new_crc is None:
                                    csv_row_new["row_crc32"] = "-"
                                else:
                                    csv_row_new = csv_row_new_crc
                                csv_read_data.append(csv_row_new)
                                self.csv_row_last = csv_row_new.copy()

                                # df=pd.DataFrame(csv_row_new, index=[0])
                                # if self.csv_row_last.shape[0]>0:
                                #     ix=df["mac"]==self.csv_row_last["mac"]
                                #     if len(ix)>0:
                                #         self.csv_row_last.drop(self.csv_row_last[ix].index, inplace=True)
                                #         self.csv_row_last = pd.concat([self.csv_row_last, df], ignore_index=True, axis=0, sort=False)
                                # else:
                                #     self.csv_row_last=df.copy()

                        if (action == "LOCATION"):
                            ini_loc = False
                            if not init_location:
                                # Stop_collecting = False
                                # datadf = {}
                                janhors_processed = []
                                # datadf_pos = {}
                                # datadf_corr = {}
                                # jmpos_processed = []
                                # jang_corr_processed = []

                                init_location = True
                                start_mqtt = True
                                try:
                                    ini_loc = True
                                    print("Starting MQTT server")
                                    if (app is not None): app.print_statuslog("Starting MQTT server")
                                    if use_MQTT and mqttclient is not None:
                                        if not keep_mqtt_on: mqttclient.loop_start()
                                    # time.sleep(CTE_Wait_Time_prescan)
                                except Exception as e:
                                    start_mqtt = False
                                    print("ERROR starting MQTT server")
                                    if (app is not None): app.print_statuslog("ERROR starting MQTT server")
                                    result = False

                            if service is not None and start_mqtt:
                                # devices_processed.append(address)  # device should remain ON until finished the scan
                                devices_processed_location=address
                                if disableCTE_duringlocation or keepactive_all_CTE_during_location:
                                    # char_uuid_enable_cte = "c92c584f-7b9e-473a-ad4e-d9965e0cd678"
                                    res = await client.write_gatt_char(service.get_characteristic(char_uuid_enable_cte),bytearray([0x01]),response=True)
                                    # if ini_loc: time.sleep(CTE_Wait_Time_prescan)
                                dev_found = False
                                n = 0
                                t1 = time.time()
                                while (wait_for_mqtt_angles and not dev_found or not wait_for_mqtt_angles) and (
                                        n <= CTE_Wait_Time_prescan or CTE_Wait_Time_prescan == 0) and ini_loc:
                                    n = n + 1
                                    # print("Staring Location for address: {0}".format(address))
                                    # app.print_statuslog("Staring Location for address: {0}".format(address))
                                    dev_found = (address.replace(":", "") in janhors_processed)
                                    if (address.replace(":", "") in janhors_processed):
                                        print("..angles? {0}={1}..".format(address.replace(":", ""),
                                                                           address.replace(":", "") in janhors_processed))
                                    time.sleep(1)
                                print("Delta time {}".format(time.time() - t1))
                                for n in range(CTE_Wait_Time):
                                    time.sleep(1)
                                    print("..{0}%%".format(int(n / CTE_Wait_Time * 100.0)), end="")
                                    if app is not None:app.print_statuslog("..{0}%%".format(int(n / CTE_Wait_Time * 100.0)), addLFCR=False)

                                print("")
                                if not keepactive_all_CTE_during_location: print(
                                    "Finish Location for address: {0}".format(address))

                                # Stop advertisement CTE
                                if disableCTE_duringlocation:
                                    res = await client.write_gatt_char(service.get_characteristic(char_uuid_enable_cte),bytearray([0x00]),response=True)
                                # else:
                                #    print("disableCTE is FALSE!! - no scan")

                        if (action == "UPDATE"):
                            scan_list = self.filter_db(id=None, data_type=uuid_data_type_filter, scan=True)
                            # scan_list.extend(self.filter_db(id="end_transac"))
                            dfupdate_read = dfupdate.copy()
                            recupdate = dfupdate.copy()
                            if service is not None:
                                rec = dfupdate[dfupdate["mac"] == myDevice_1_address]
                                fupdate = False

                                # #char_uuid_enable_cte = "c92c584f-7b9e-473a-ad4e-d9965e0cd678"
                                # res = await client.write_gatt_char(
                                #     service.get_characteristic(char_uuid_enable_cte),
                                tag_updated = False
                                error_update = False
                                read_nfc = False

                                index_update = rec.index
                                for k in range(len(scan_list)):
                                    try:
                                        scan = scan_list[k]['scan']
                                        if scan:
                                            char_uuid_id = scan_list[k]['uuid']
                                            id = scan_list[k]['id']
                                            if not rec[id].isna().values[0] and scan_list[k]["id"] !="mac":  # only update what is not None (value has changed)
                                                print("Updating {0}".format(id))
                                                if app is not None:app.print_statuslog(
                                                    "Updating {0}".format(id))
                                                if scan_list[k]['type'] == 'UTF-8':
                                                    newval = str(rec[id].values[0])
                                                elif (scan_list[k]['type'] == 'HEX'):
                                                    if np.isnan(rec[id].values[0]):
                                                        newval = int(0)
                                                    else:
                                                        newval = int(rec[id].values[0])

                                                else:
                                                    newval = ""

                                                if not read_nfc and (scan_list[k]["id"] == "read_nfc"):
                                                    read_nfc = (newval == 1)
                                                    # index_read_nfc=rec.index
                                                    id_read_nfc = id
                                                    char_uuid_id_read_nfc = char_uuid_id
                                                    k_read_nfc = k

                                                # if not end_transac and (scan_list[k]["id"] == "end_transac"):
                                                #     end_transac = (newval == 1)
                                                #     k_end_transac = k
                                                #     id_end_transac = id


                                                if scan_list[k]["id"] != "read_nfc":# and scan_list[k]["id"] != "end_transac" :
                                                    if scan_list[k]['NFC'] == True:
                                                        fupdate = True

                                                    if (scan_list[k]['type'] == 'HEX'):
                                                        res = await client.write_gatt_char(service.get_characteristic(char_uuid_id),newval.to_bytes(scan_list[k]['length'], byteorder='big',signed=False),response=True)
                                                    else:
                                                        res = await client.write_gatt_char(service.get_characteristic(char_uuid_id),bytearray(newval, 'utf-8'),response=True)

                                                    # print(res)
                                                    valread_raw =  await self.readgatt(char_uuid_id)  #await client.read_gatt_char(char_uuid_id)
                                                    if valread_raw is not None:
                                                        if type(valread_raw) is bytearray:
                                                            valread = bytes(valread_raw)
                                                        else:
                                                            pass
                                                    else:
                                                        valread = bytes(b'')

                                                    if (scan_list[k]['type'] == 'HEX'):
                                                        val = int.from_bytes(valread, byteorder='big')
                                                    else:
                                                        if type(valread) is bytes:
                                                            val = valread.decode('utf-8')
                                                        else:
                                                            val = str(valread)
                                                    if (val != newval and not error_update):
                                                        error_update = True
                                                    else:
                                                        tag_updated = True
                                                    dfupdate_read.loc[rec.index, id] = val
                                                    print("{0} read: {1}".format(id, val))
                                                    if app is not None:app.print_statuslog("{0} read: {1}".format(id, val))

                                    except Exception as e:
                                        if app is not None:app.print_statuslog(str(e))
                                        print("Error address:{0} id:{1} char_uuid_id:{2}".format(address,id, char_uuid_id))
                                        print(e)
                                        if app is not None:app.print_statuslog("Error address:{0} id:{1} char_uuid_id:{2}".format(address,id, char_uuid_id))
                                        error_update = True
                                        dfupdate_read.loc[index_update, "status"] = "update error"

                                if (tag_updated and not error_update):
                                    dfupdate_read.loc[rec.index, "status"] = "updated"
                                if (error_update):
                                    dfupdate_read.loc[rec.index, "status"] = "update error"

                                recupdate.drop(recupdate[recupdate["mac"] == myDevice_1_address].index,
                                               inplace=True)
                                if fupdate:
                                    # Update NFC if not read NFC command
                                    try:
                                        res = await client.write_gatt_char(
                                            service.get_characteristic(char_uuid_update_nfc),
                                            bytearray("1", 'utf-8'),
                                            response=True)
                                        print(res)
                                        if (not error_update): dfupdate_read.loc[index_update, "status"] = "updated"
                                    except Exception as e:
                                        print(e)
                                        if app is not None:app.print_statuslog("Error {0}".format(e))
                                        dfupdate_read.loc[index_update, "status"] = "update error"

                                if read_nfc:
                                    try:
                                        read_nfc_done = True
                                        newval = newval.to_bytes(scan_list[k_read_nfc]['length'], byteorder='big',
                                                                 signed=False)
                                        res = await client.write_gatt_char(
                                            service.get_characteristic(char_uuid_id_read_nfc), newval, response=True)
                                        dfupdate_read.loc[index_update, id_read_nfc] = 0  # clear flag
                                        if (not error_update): dfupdate_read.loc[index_update, "status"] = "updated"
                                    except Exception as e:
                                        print(e)
                                        if app is not None:  app.print_statuslog("Error {0}".format(e))
                                        dfupdate_read.loc[index_update, "status"] = "update error"

                                if tag_updated:
                                    try:
                                        newval=1
                                        char_uuid_end_transac = self.filter_db(id="end_transac")[0]["uuid"]
                                        char_uuid_end_transac_length= self.filter_db(id="end_transac")[0]["length"]
                                        newval = newval.to_bytes(char_uuid_end_transac_length, byteorder='big', signed=False)
                                        res = await client.write_gatt_char(service.get_characteristic(char_uuid_end_transac), newval,response=True)
                                        #dfupdate_read.loc[index_update, id_end_transac] = 0  # clear flag

                                        if (not error_update): dfupdate_read.loc[index_update, "status"] = "updated"

                                        #update crc
                                        id="ble_data_crc"
                                        valread_raw =await self.readgatt(char_uuid_ble_data_crc) # await client.read_gatt_char(char_uuid_ble_data_crc)
                                        if valread_raw is not None:
                                            if type(valread_raw) is bytearray:
                                                valread = bytes(valread_raw)
                                            else:
                                                pass
                                        else:
                                            valread = bytes(b'')

                                        if type(valread) is bytes:
                                            val = valread.decode('utf-8')
                                        else:
                                            val = str(valread)
                                        #if id in list(dfupdate_read.columns): dfupdate_read.loc[index_update, id] = val
                                        #dfupdate_read.loc[index_update, "end_transac"] = 0
                                        self.ble_data_crc=val
                                        dfupdate_read["ble_data_crc"][0] = val
                                    except Exception as e:
                                        print(e)
                                        if app is not None:  app.print_statuslog("Error {0}".format(e))
                                        dfupdate_read.loc[index_update, "status"] = "update error"
                            else:
                                pass
                    else:
                        if (app is not None): app.print_statuslog("Historic data valid {}".format(action))

                    if not keep_connected: await client.disconnect()

                else:
                    print(f"Failed to connect to Device {address}")
                    if app is not None: app.print_statuslog(f"Failed to connect to Device {address}")
                    result = False

            except Exception as e:
                print(e)
                if app is not None:  app.print_statuslog("Error {0}".format(e))
                result = False

        res={"result":result, "dfupdate_read":dfupdate_read, "csv_read_data":csv_read_data,
             "recupdate":recupdate, "devices_processed_location":devices_processed_location,"init_location":init_location,"start_mqtt":start_mqtt}
        return res

    async def writegatt(self,char_uuid, value,response=True):
        try:
            service_char=self.custom_service.get_characteristic(char_uuid)
            res=await self.client.write_gatt_char(service_char, bytearray(value), response=True)
        except Exception as e:
            print(e)
            self.error=e
        return res

    async def readgatt(self,char_uuid_id):
        try:
            err=False
            char_uuid_val=None
            char_uuid_val = await self.client.read_gatt_char(char_uuid_id)
        except Exception as e:
            print(e)
            self.error = e
            # if type(e) is  bleak.exc.BleakDeviceNotFoundError: type(e) is OSError  e.strerror=="The object has been closed"

        return char_uuid_val

    def filter_db(self,id, data_type=None, scan=None):
        try:
            res = None
            if id is None:
                res = [y for y in [self.char_uuid[x] for x in list(self.char_uuid)] if
                       (y["scan"] == scan or scan is None) and (y["data_type"] == data_type or data_type is None)]
            else:
                if type(id) is list:
                    res = [y for y in [self.char_uuid[x] for x in list(self.char_uuid)] if
                           (y["scan"] == scan or scan is None) and (
                                       y["data_type"] == data_type or data_type is None) and y["id"] in id]
                else:
                    res = [y for y in [self.char_uuid[x] for x in list(self.char_uuid)] if
                           (y["scan"] == scan or scan is None) and (
                                       y["data_type"] == data_type or data_type is None) and y["id"] == id]#[0]
        except Exception as e:
            print(e)
        return res

    def get_ble_data_crc(self):
        res = "00000000"
        try:
            if self.rssi_tag_scan is not None:
                if self.address.replace(":", "") in list(self.rssi_tag_scan.keys()):
                    res = self.rssi_tag_scan[self.address.replace(":", "")]["ble_data_crc"]
        except Exception as e:
            print(e)
        return res

    def get_asset_images_crc(self):
        res = "00000000"
        try:
            if self.rssi_tag_scan is not None:
                if self.address.replace(":", "") in list(self.rssi_tag_scan.keys()):
                    res = self.rssi_tag_scan[self.address.replace(":", "")]["asset_image_crc"]
        except Exception as e:
            print(e)
        return res

class MyClass:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def display(self):
        print(f"{self.name}: {self.value}")

class boldtag:

    serv_uuid_Custom_Service = "87e29466-8be6-4ede-9ffb-04a7121938da"

    def __init__(self,scanner_param, webapp=None,rssi_tag_scan=None,directory="//"):
        self.scanner_param=scanner_param
        self.webapp=webapp
        self.limit = 0
        # self.index = 0
        # self.items = []
        # self.current= None
        self._index = -1
        self.directory=directory
        self.rssi_tag_scan=rssi_tag_scan


        self.gatewaydb = gatewaydb()

    def __iter__(self):
        self._index=-1
        return self

    def __next__(self):
        if self._index < self.limit-1:
            # self.set_current(self._index)
            self._index += 1
            return self.items[self._index]
        else:
            raise StopIteration  # Stops the iteration when the limit is reached

    def __getitem__(self, index):
        # self.update_current()
        if index < self.limit and index>=0:
            return self.items[index]
        else:
            self._index = 0
            raise IndexError("Index out of range")

    def __del__(self):
        for i in range(len(self.items)):
            self.dicconnect_and_remove(i)

    def __len__(self):
        # Returns the length of the list
        return self.limit

    async def new(self, device):#, connect=False, max_retry=3,timeout=15):
        #add new data
        try:
            res=-1
            # item=ble_tag(device=device, webapp=self.webapp, index=self.index,scanner_param=self.scanner_param)
            if self._index==-1:
                self.items = []
                self._index =0
            tag=ble_tag(device=device, webapp=self.webapp, index=self._index,scanner_param=self.scanner_param,serv_uuid_Custom_Service=self.serv_uuid_Custom_Service,directory=self.directory)
            self.items.append(tag)

            self.limit = self.limit + 1
            self._index=self.limit -1 # self.set_current(self.limit-1)
            # item=self.items[self._index]
            res=self._index
            # if connect:
            #     res=False
            #     try:
            #         await self.items[self._index].connect(max_retry=max_retry,timeout=timeout)
            #         res = self.items[self._index].connected
            #     except Exception as e:
            #         print(e)
            #
            #     if res:
            #         self.webapp.print_statuslog("BoldTag {} connected!".format(self.items[self._index].address))
            #     else:
            #         self.webapp.print_statuslog("BoldTag {} fail to connect".format(self.items[self._index].address))
            #     # msg="BoldTag {} Added and connected".format(device.address)
            #     # print(msg)
            #     # if (self.webapp is not None): self.webapp.print_statuslog(msg)
            # else:
            #     msg="BoldTag {} Added fail to connect".format(device.address)
            #     print(msg)
            #     if (self.webapp is not None): self.webapp.print_statuslog(msg)
        except Exception as e:
            print(e)
            msg = "BoldTag {} error: {} ".format(device.address, e)
            if (self.webapp is not None): self.webapp.print_statuslog(msg)
        return res

    async def dicconnect_and_remove(self, index=None):
        if index is None:
            index=self._index
        if index>=0 and index<self.limit:
            tag=self.items[index]
            if tag["connected"]:
                try:
                    await tag["client"].disconnect()
                except Exception as e:
                    print(e)
            self.items=self.items.pop[index]
            self.limit=len(self.items)
            if self._index-1>0:
                self._index=self._index-1
            elif self._index + 1 < self.limit:
                self._index = self._index + 1
            else:
                self._index=0

    def update_rssi_host_scan(self,address,rssi_host_scan):
        try:
            index = [x for x in range(len(self.items)) if self.items[x].address == address]
            if len(index) > 0:
                tag=self.items[index]
                tag.rssi_host_scan=rssi_host_scan
                # self.items[index]=tag
        except Exception as e:
            print(e)

    def find_tag(self, address):#, set_current=True):
        try:
            res=-1
            if self.limit>0:
                index=[x for x in range(len(self.items)) if self.items[x].address==address]
                if len(index)>0:
                    index=index[0]
                    # if set_current:
                    #     self.set_current(index)
                    res= index
        except Exception as e:
            print(e)
        return res

    def get_tag_by_address(self, address):#, set_current=True):
        try:
            res=None
            if self.limit > 0:
                index=[x for x in range(len(self.items)) if self.items[x].address==address]
                if len(index)>0:
                    index=index[0]
                    # if set_current:
                    #     self.set_current(index)
                    return self.items[index]
        except Exception as e:
            print(e)
        return res

    def get_tag_by_index(self, index):#, set_current=True):
        try:
            res=None
            if index >= 0 and index < self.limit:
                return self.items[index]
        except Exception as e:
            print(e)
        return res

    # async def connect(self,index, max_retry=3,timeout=15):
    #     # tag=self.get_tag_by_index(index)
    #     # if tag is not None:
    #     res=False
    #     try:
    #         tag=self.get_tag_by_index(index)
    #         res=await tag.connect(max_retry=max_retry,timeout=15)
    #     except Exception as e:
    #         print(e)
    #     return res

class gatewaydb:
    # csv_row = {"mac": "", "name": "", "tag_id": "", "asset_id": "", "certificate_id": "", "type": "",
    #            "expiration_date": "", "color": "", "series": "", "read_nfc": "", "status": "", "status_code": "",
    #            "asset_images_file_extension": "","manufacturer_data":"","rssi_host":"","last_seen":"", "asset_images_crc":"","ble_data_crc":"", "x": "", "y": ""}

    csv_row = {"mac": None, "name": None, "tag_id": None, "asset_id": None, "certificate_id": None, "type": None,
               "expiration_date": None, "color": None, "series": None, "read_nfc": None, "tag_mac": None,  "asset_images_file_extension": None,
               "certification_company_name": None, "certification_company_id": None, "certification_place": None,"certification_date": None, "test_type": None, "asset_diameter": None,
               "batch_id": None, "batch_date": None, "machine_id": None, "owner_company_name": None, "owner_data": None,"asset_comment": None, "logo_file_extension": None, "signature_image_file_extension": None,"ndir_id":None,
               "ble_data_crc": None,"asset_images_crc": None,"logo_images_crc": None, "signature_images_crc": None,
               "tag_advertisement_period": None,"ble_on_period": None, "ble_on_wakeup_period": None, "ble_off_period": None, "tag_periodic_scan": None,
               "update_nfc": None, "enable_cte": None, "tag_enabled": None,"read_battery_voltage": None,
               "tag_firmware": None,"altitude": None, "moved": None,"battery_voltage": None, "rssi_host": None, "last_seen": None,"manufacturer_data": None,"status_code": None,"status": None,"x": "", "y": ""}


    scan_columnIds = ["mac", "name", "tag_id", "asset_id", "certificate_id", "type", "expiration_date", "color",
                      "series", "read_nfc", "status", "status_code", "asset_images_file_extension","last_seen","asset_images_crc","ble_data_crc", "x", "y"]

    # csv_cfg_row = {"mac":"", "name": "","update_nfc":"","status_code":"","enable_cte":"","tag_enabled":"","tag_advertisement_period":"",
    #                "ble_on_period":"","ble_on_wakeup_period":"","ble_off_period":"","tag_periodic_scan":"","tag_mac":"","read_battery_voltage":"",
    #                "battery_voltage":"","altitude":"","moved":"","tag_firmware":"","manufacturer_data":"","rssi_host":"","last_seen":"","asset_images_crc":"","status":"","x":"","y":""}
    scan_cfg_columnIds = ["mac", "status_code", "enable_cte", "tag_enabled", "tag_advertisement_period",
                             "ble_on_period", "tag_mac", "read_battery_voltage",
                             "ble_on_wakeup_period", "ble_off_period", "tag_periodic_scan", "altitude", "moved",
                             "battery_voltage", "tag_firmware","manufacturer_data","rssi_host","last_seen","asset_images_crc","ble_data_crc", "status", "x", "y"]

    # csv_det_row = {"mac":"", "name": "","certification_company_name":"","certification_company_id":"","certification_place":"","certification_date":"","test_type":"","asset_diameter":"",
    #                  "batch_id":"","batch_date":"","machine_id":"","status_code":"","ble_data_crc":"","asset_images_crc":"","logo_images_crc":"","signature_images_crc":"",
    #                  "owner_company_name":"","owner_data":"","altitude":"","moved":"","battery_voltage":"","asset_comment":"","manufacturer_data":"","rssi_host":"","last_seen":"","status":"","x":"","y":""}
    scan_det_columnIds = ["mac", "certification_company_name",
                               "certification_company_id", "certification_place", "certification_date", "test_type",
                               "asset_diameter", "batch_id", "batch_date",
                               "machine_id", "status_code", "ble_data_crc", "asset_images_crc", "logo_images_crc",
                               "signature_images_crc", "owner_company_name",
                               "owner_data", "altitude", "moved", "battery_voltage", "asset_comment", "ndir_id","last_seen",
                               "status", "x", "y"]

    location_cvs_row = {"tag_mac": "", "out_prob": "", "out_prob_k": "", "anchors": "", "result": "", "x": "", "y": ""}
    location_cvs_columnIds = ["tag_mac", "out_prob", "out_prob_k", "anchors", "result", "x", "y"]

    # cloud_csv_row = {"mac": "", "logo_file_extension": "", "signature_image_file_extension": "", "is_machine": ""}
    cloud_scan_columnIds = ["mac", "logo_file_extension", "signature_image_file_extension", "is_machine"]

    #TODO uniformize 'asset_type', 'asset_color', 'asset_series'
    ble_crc_attributes=["tag_id", "asset_id", "certificate_id", "type",
                                       "expiration_date", "color", "series",
                                       "asset_images_file_extension", "enable_cte",
                                       "certification_company_name", "certification_company_id",
                                       "certification_place", "certification_date", "test_type",
                                       "asset_diameter", "asset_comment", "batch_id", "batch_date",
                                       "machine_id", "status_code", "asset_images_crc",
                                       "logo_images_crc", "signature_images_crc", "owner_company_name",
                                       "owner_data", "ndir_id", "tag_mac", "altitude",
                                       "moved"]


    def __init__(self):
        self.new_csv_row=None
        # self.new_csv_cfg_row=None
        # self.new_csv_det_row = None
        self.mac=None

    def set_mac(self,mac):
        self.mac=mac

    # Function to calculate CRC32 for a row
    def crc32_row(self, row):
        # Convert the row to a string or bytes, then calculate CRC32
        row_data = ''.join(str(value) for value in row).encode('utf-8')
        return zlib.crc32(row_data) & 0xFFFFFFFF  # Mask to ensure 32-bit unsigned

    def generate_crc32(self, data):
        try:
            res=None
            if type(data) is dict:
                all_keys_in_list = all(key in list(data.keys()) for key in self.ble_crc_attributes)
                if all_keys_in_list:
                    df = pd.DataFrame(data, index=[0])
                    df['row_crc32'] = df[self.ble_crc_attributes].apply(self.crc32_row, axis=1)
                    df['row_crc32'] = df['row_crc32'].apply(lambda x: hex(x)[2:])
                    res=df.to_dict(orient='records')[0] if df.shape[0]==1 else df.to_dict()
            elif type(data) is pd.DataFrame:
                all_keys_in_list = all(key in list(data.columns) for key in self.ble_crc_attributes)
                if all_keys_in_list:
                    data['row_crc32'] = data[self.ble_crc_attributes].apply(self.crc32_row, axis=1)
                    data['row_crc32'] = data['row_crc32'].apply(lambda x: hex(x)[2:])
                    res=data
        except Exception as e:
            print(e)
        return res
    def dfupdate(self,asdf=True, ):
        if asdf:
            res=pd.DataFrame.from_dict(self.new_csv_row)
        else:
            res=self.new_csv_row
        return  res

    def new_csv_row_id(self):
        if self.new_csv_row is None:
            self.new_csv_row=self.csv_row.copy()
            for x in self.new_csv_row.keys():
                self.new_csv_row[x]=np.nan

    def set_csv_row_id(self, id, value):
        self.new_csv_row_id()
        res=False
        if id in self.new_csv_row.keys():
            self.new_csv_row[id] = [value]
            self.new_csv_row["mac"] = [self.mac ]
            res = True
        return res


class boldscanner:
    DEVICE_NAME = "BoldTag"

    def __init__(self, disableCTE_duringlocation=True,keepactive_all_CTE_during_location=False,
                                use_MQTT = False, mqttclient = None, keep_mqtt_on = False,
                                wait_for_mqtt_angles = True, CTE_Wait_Time_prescan = 55, CTE_Wait_Time = 20,webapp=None,directory="//"):
        self.scanner_param={}
        self.scanner_param["serv_uuid_Custom_Service"] = ""#serv_uuid_Custom_Service
        self.scanner_param["disableCTE_duringlocation"] =disableCTE_duringlocation
        self.scanner_param["keepactive_all_CTE_during_location"] =keepactive_all_CTE_during_location
        self.scanner_param["use_MQTT"] =use_MQTT
        self.scanner_param["mqttclient"] =mqttclient
        self.scanner_param["keep_mqtt_on"] =keep_mqtt_on
        self.scanner_param["wait_for_mqtt_angles"] =wait_for_mqtt_angles
        self.scanner_param["CTE_Wait_Time_prescan"] =CTE_Wait_Time_prescan
        self.scanner_param["CTE_Wait_Time"] =CTE_Wait_Time
        self.directory=directory
        self.discover_rssi = False
        self.discover_rssi_collect = True

        self.scanner = BleakScanner(detection_callback=self.device_found)
        # self.scanner.register_detection_callback(self.device_found)

        self.webapp = webapp



        self.startCTE_address_filter=[]
        self.rssi_host_scan={}
        self.rssi_host_scan_reset = False
        self.rssi_host_scan_disable=False

        self.rssi_tag_scan = {}

        self.tags = boldtag(self.scanner_param, self.webapp, self.rssi_tag_scan,self.directory)
        self.tag_devices=[]
        self.scanner_param["serv_uuid_Custom_Service"] = self.tags.serv_uuid_Custom_Service




    def get_rssi_host_scan(self):
        self.rssi_host_scan_disable = True
        rssi_host_scan=self.rssi_host_scan.copy()
        self.rssi_host_scan_disable = False
        return rssi_host_scan


    def reset_rssi_host_scan(self):
        self.rssi_host_scan_reset=True

    async def discover_rssi_start(self):
        try:
            if self.discover_rssi == False:
                await self.scanner.start()
                #time.sleep(1)
                self.discover_rssi = True
        except Exception as e:
            print(e)

    async def discover_rssi_stop(self):
        try:
            if self.discover_rssi == True:
                await self.scanner.stop()
                self.discover_rssi = False
        except Exception as e:
            print(e)

            # ---------------------------------------------------------------------#
    # Call back advertisement
    #
    # ---------------------------------------------------------------------#
    async def device_found(self, device: BLEDevice, advertisement_data: AdvertisementData):
        """Decode iBeacon."""
        try:
            bres = False
            if device.name is not None and not self.rssi_host_scan_disable:
                if device.name.startswith(self.DEVICE_NAME):
                    address = device.address.replace(":", "")
                    rssi = advertisement_data.rssi
                    # print("RSSI {0}:{1}".format(address,rssi))
                    tag_data_crc = "0000000000000000"
                    try:
                        if len(advertisement_data.manufacturer_data.items()) > 0:
                            tag_data_crc = [x for x in advertisement_data.manufacturer_data.items()][0][1].hex()
                    except Exception as e:
                        print(e)
                    rssi_host_scan={"address": address, "rssi_host": rssi, "tag_data_crc": tag_data_crc}
                    if self.rssi_host_scan_reset==True:
                        self.rssi_host_scan={}
                        self.rssi_host_scan_reset=False

                    ble_data_crc = tag_data_crc[8:]
                    asset_image_crc = tag_data_crc[0:8]
                    if tag_data_crc!='0000000000000000':
                        self.rssi_tag_scan[address]={"time": time.strftime("%m/%d/%Y %H:%M:%S") , "rssi_host": rssi,"ble_data_crc":ble_data_crc,"asset_image_crc":asset_image_crc,"tag_data_crc":tag_data_crc}

                    if (address in self.startCTE_address_filter or len(self.startCTE_address_filter) == 0) and self.discover_rssi_collect:
                        self.rssi_host_scan[len(self.rssi_host_scan)] =rssi_host_scan# {"address": address, "rssi_host": rssi, "tag_data_crc": tag_data_crc}
                        self.tags.update_rssi_host_scan(address,rssi_host_scan)

        except Exception as e:
            print(f'error in device_found {e}')

    def tags_connected(self):
        try:
            tags=[]
            if self.tags.limit>0:
                for i in range(self.tags.limit):
                    tag= self.tags.get_tag_by_index(i)
                    if tag is not None:
                        if tag.connected:
                            tags.append(tag.address)
        except Exception as e:
            print(f'error in tags_connected {e}')
        return tags

    def all_connected(self):
        try:
            res=True
            if self.tags.limit>0:
                for i in range(self.tags.limit):
                    tag= self.tags.get_tag_by_index(i)
                    if tag is not None:
                        if not tag.connected:
                            res=False
                    else:
                        res=False
        except Exception as e:
            print(f'error in tags_connected {e}')
        return res


    async def check_and_reconect(self,devprocessed, nRetries=4,max_retry=1, timeout=15):
        try:
            webcancelprocess = False
            if (self.tags.limit > 0):
                try:
                    # res_conn={}
                    ncount = 0
                    while ncount < nRetries:
                        ncount = ncount + 1
                        for tag in self.tags.items:  # tag_found:
                            if tag.address not in devprocessed:
                                res = await self.connect(index=tag.index, max_retry=max_retry, timeout=timeout)
                                # res=x.connected
                                # res=await bscanner.tags.connect(max_retry=1, index=x.index, timeout=5)
                                if self.app.webcancel:
                                    webcancelprocess = True
                                    break
                                # res_conn[x.address] = res
                            # else:
                            # res_conn[x.address]=True

                        if self.app.webcancel:
                            webcancelprocess = True
                            break
                        # if (all([res_conn[x] for x in res_conn.keys()]) and len(res_conn.keys())==bscanner.tags.limit): break
                        if self.all_connected():
                            break
                except Exception as e:
                    print(e)
        except Exception as e:
            print(e)
        return webcancelprocess

    #multiple retris is possible if there is multiple BLE connectors, otehrwise the deices are disconnected!!!
    async def scan_tags(self,connect=False, max_retry=1, max_scans=4,timeout=15,max_tags=0,scan_mac_banned=[],scan_mac_filter_address=[],timeout_scanner=20):
        nscan = 0
        new_tags=[]
        existing_tags=[]
        filterout=sum([1 if self.tags.get_tag_by_address(mac) is not None else 0 for mac in scan_mac_filter_address])==len(scan_mac_filter_address) and len(scan_mac_filter_address)>0
        while nscan < max_scans and ((len(new_tags)+len(existing_tags))<max_tags or max_tags==0) and not filterout:
            try:
                nscan=nscan+1
                #scanner = BleakScanner()
                if self.tags.limit==0:
                    self.webapp.print_statuslog("Starting discovering...")
                    devices = await self.scanner.discover(timeout=timeout_scanner)
                    self.webapp.print_statuslog("Finishing discovering...")
                    self.webapp.print_statuslog("Starting filtering BoldTags...")
                else:
                    devices=self.tag_devices
                for device in devices:
                    if self.webapp.webcancel: break
                    if device.name is not None:
                        try:
                            if device.name.startswith("BoldTag"):
                                if device not in self.tag_devices:
                                    self.tag_devices.append(device)

                                if not (device.address in scan_mac_banned) and (device.address in scan_mac_filter_address or len(scan_mac_filter_address)==0) :

                                    if (self.webapp is not None): self.webapp.print_statuslog("BoldTag  found {}".format(device.address))
                                    ix=self.tags.find_tag(device.address)

                                    if ix==-1:
                                        self.webapp.print_statuslog("New BoldTags Found {} adding..".format(device.address))
                                        ix=await self.tags.new( device=device)#,max_retry=max_retry)
                                        if connect:
                                            self.webapp.print_statuslog("Trying to connect to {}..".format(device.address))
                                            await self.connect(index=ix, max_retry=max_retry, timeout=timeout)
                                        new_tags.append(device.address)

                                        filterout=sum([1 if self.tags.get_tag_by_address(mac) is not None else 0 for mac in scan_mac_filter_address])==len(scan_mac_filter_address) and len(scan_mac_filter_address)>0
                                        if filterout: break

                                    else:
                                        # self.tags.set_current(ix)
                                        # tag=self.tags.get_tag_by_index(ix)
                                        if connect:
                                            self.webapp.print_statuslog("Checking connection status for {}..".format(device.address))
                                            # await self.tags.connect(max_retry=max_retry)
                                            # await self.tags.connect(index=ix,max_retry=max_retry,timeout=timeout)
                                            await self.connect(index=ix, max_retry=max_retry, timeout=timeout)

                                        existing_tags.append(device.address)
                                else:
                                    if (self.webapp is not None and device.address in scan_mac_banned): self.webapp.print_statuslog(
                                        "BoldTag  banned {}".format(device.address))

                        except Exception as e:
                            print(e)

                if filterout:break

            except Exception as e:
                print(e)
        return {"new_tags":new_tags,"existing_tags":existing_tags}

    async def redo_tag(self,tag):
        try:
            await tag.client.disconnect()
            tag.set_client()
            # device=tag.device
            # index = await self.tags.new(device=device)  # ,max_retry=max_retry)
            # tag = self.tags.get_tag_by_index(index)
            # res = False
        except Exception as e:
            print(e)

    async def connect(self,index, max_retry=3, timeout=15):

        ncount = 0
        try:
            tag = self.tags.get_tag_by_index(index)
            res=False

            if tag is not None:
                res = tag.connected
                error = tag.error
                while res != True and ncount < max_retry:  # and self.connect_retries<self.max_connect_retries:
                    if error is not None:
                        self.webapp.print_statuslog("Redoing connection for {} ".format(tag.address))
                        if type(error) is OSError:
                            if error.strerror == "The object has been closed":
                                await self.redo_tag(tag)
                                res = False
                        elif type(error) is  bleak.exc.BleakDeviceNotFoundError:
                            await self.redo_tag(tag)
                            res = False
                        elif type(error) is bleak.exc.BleakError:
                            if error.args[0]=='Not connected':
                                await self.redo_tag(tag)
                                res = False
                        tag.error=None

                # while res != True and ncount < max_retry   :  # and self.connect_retries<self.max_connect_retries:
                    ncount = ncount + 1
                    print("connecting to {} retry:{}".format(tag.address, ncount))
                    self.webapp.print_statuslog("connecting to {} retry:{}".format(tag.address, ncount))
                    try:
                        tag.connect_retries = tag.connect_retries + 1
                        # await asyncio.wait_for(self.client.connect(), timeout=timeout)
                        res = await tag.client.connect()
                        tag.connected = res
                        if res:
                            self.webapp.print_statuslog("BoldTag {} connected!".format(tag.address))
                        else:
                            self.webapp.print_statuslog("BoldTag {} fail to connect".format(tag.address))
                    except Exception as e:
                        print(e)
                        tag.error=e
                        self.webapp.print_statuslog("BoldTag {} dormant - {}".format(tag.address, e))

                    if tag.connected:
                        print("BoldTag {} gathering services".format(tag.address))
                        svcs = await tag.client.get_services()
                        for service_1 in svcs:
                            # if service_1.uuid==serv_uuid_Throughput_Test_Service_uuid:
                            if service_1.uuid == tag.scanner_param["serv_uuid_Custom_Service"]:
                                tag.set_custom_service(service_1)
                                break
                        # self.update_current()

        except Exception as e:
            print(e)
            self.webapp.print_statuslog("Connection error for BoldTag  {} ".format(self.address))
        return res

    def totaltags(self):
        return self.tags.limit
    async def disconnect_all(self):
        while self.tags.limit>0:
            try:
                await self.tags.l.dicconnect_and_remove(0)
            except Exception as e :
                print(e)


async def main():
    """Scan for devices."""

    nmax=0
    ntags=0

    bscanner=boldscanner()
    await bscanner.scan_tags(connect=True)
    await bscanner.scan_tags(connect=True)

    # for x in bscanner.tags:
    #     print(x)

    res=None
    for i in range(bscanner.tags.limit):
        tag=bscanner.tags.get_tag_by_index(i)
        if tag.connected:
            # res_tag=await bscanner.tags.tag_functions(action="READ",uuid_filter_id="detail",uuid_data_type_filter="base")
            # print(res_tag)
            # res_tag = await bscanner.tags.tag_functions(action="READ", uuid_filter_id="status_code",uuid_data_type_filter=None)
            # print(res_tag)
            # res_tag = await bscanner.tags.tag_functions(action="READ", uuid_filter_id="enable_cte",uuid_data_type_filter=None)
            # print(res_tag)
            # bscanner.tags.gatewaydb.new_csv_row_id(id="asset_id", value="pepe")
            # dfupdate =bscanner.tags.gatewaydb.dfupdate()
            # res_tag = await bscanner.tags.tag_functions(action="UPDATE",uuid_data_type_filter=None,dfupdate=dfupdate)
            # print(res_tag)
            # tag.gatewaydb.set_csv_cfg_row_id(id="enable_cte", value=1)
            tag.gatewaydb.set_csv_row_id(id="enable_cte", value=1)
            # bscanner.tags.gatewaydb.set_csv_row_id(id="asset_id", value=np.nan)
            # dfupdate_cfg =tag.gatewaydb.dfupdate_cfg()
            dfupdate = tag.gatewaydb.dfupdate()
            # res_tag = await tag.tag_functions(action="UPDATE",uuid_data_type_filter="configuration",dfupdate=dfupdate_cfg)
            res_tag = await tag.tag_functions(action="UPDATE", uuid_data_type_filter="configuration",dfupdate=dfupdate)
            print(res_tag)
            res_tag = await tag.tag_functions(action="LOCATION", uuid_data_type_filter=None)
            print(res_tag)

        print(res)
    await bscanner.disconnect_all()

    print(res)


if __name__ == "__main__":
    asyncio.run(main())
    print('ff')