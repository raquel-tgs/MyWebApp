
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

class tag:
    def __init__(self,device,address,connected,client,custom_service,index,name):
        self.device=device
        self.address=address
        self.connected=connected
        self.client=client
        self.custom_service=custom_service
        self.index=index
        self.name=name

class boldtag:
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

    char_uuid_nfc = ["certification_company_name", "certification_company_id", "certification_place",
                     "certification_date",
                     "certificate_id", "expiration_date", "test_type", "asset_id",
                     "tag_id", "type", "color", "series",
                     "asset_diameter", "asset_comment", "batch_id", "batch_date",
                     "machine_id", "status_code", "ble_data_crc", "asset_images_crc",
                     "logo_images_crc", "signature_images_crc", "owner_company_name", "owner_data",
                     "ndir_id", "asset_images_file_extension", "tag_mac", "gattdb_tag_periodic_scan"]

    def __init__(self,scanner_param, webapp=None, csv_row=None):
        self.scanner_param=scanner_param
        self.webapp=webapp
        self.limit = 0
        self.index = 0
        self.items = []
        self.current= None
        self._index = 0
        self.device=None
        self.address=None
        self.connected=False
        self.client=None
        self.custom_service=None

        self.gatewaydb = gatewaydb()
        self.csv_row = self.gatewaydb.csv_row
        self.csv_cfg_row = self.gatewaydb.csv_cfg_row
        self.csv_det_row = self.gatewaydb.csv_det_row
        try:
            for ix in self.char_uuid.keys():
                if self.char_uuid[ix]["id"] in self.char_uuid_nfc:
                    self.char_uuid[ix]["NFC"]=True
        except Exception as e:
            print(e)

    def __iter__(self):
        self._index=0
        return self

    def __next__(self):
        if self._index < self.limit:
            self.set_current(self._index)
            self._index += 1
            return self.current
        else:
            raise StopIteration  # Stops the iteration when the limit is reached

    def __getitem__(self, index):
        self.update_current()
        if index < self.limit and index>=0:
            return self.items[index]
        else:
            raise IndexError("Index out of range")

    def __del__(self):
        for i in range(len(self.items)):
            self.dicconnect_and_remove(i)

    def __len__(self):
        # Returns the length of the list
        return self.limit

    def update_current(self):
        if self.index>=0 and self.index<self.limit and self.current is not None:
            self.current.device=self.device
            self.current.address=self.address
            self.current.connected=self.connected
            self.current.client=self.client
            self.current.name = self.name
            self.current.custom_service = self.custom_service
            self.current.index= self.index
            self.items[self.index]=self.current
    def set_current(self, index):
        self.update_current()
        if index!=self.index and index>=0 and index<self.limit :
            self.index=index
            self.current = self.items[self.index]
            self.device=self.current.device
            self.address=self.current.address
            self.connected=self.current.connected
            self.name = self.current.name
            self.client=self.current.client
            self.custom_service=self.current.custom_service
            self.gatewaydb.set_mac(self.address)

    def get_current(self):
        return self.current


    async def new(self, device, connect=False, max_retry=3):
        #add new data
        self.limit = self.limit + 1
        item=tag(client=None, connected=False, device=device, address=device.address,custom_service=None, index=self.index, name=device.name)
        self.items.append(item)
        self.set_current(self.limit-1)
        if connect:
            await self.connect(max_retry=max_retry)

    async def connect(self,max_retry=3):
        ncount = 0
        res=self.connected
        while not self.connected and ncount < max_retry:
            print("connecting to {} retry:{}".format(self.address,ncount ))
            ncount = ncount + 1
            try:
                self.client = BleakClient(self.address)
                await self.client.connect()
                self.connected= self.client.is_connected
                res=self.connected
            except Exception as e:
                print(e)
            if self.connected:
                print("connecting to {} connected".format(self.address))
                svcs = await self.client.get_services()
                for service_1 in svcs:
                    # if service_1.uuid==serv_uuid_Throughput_Test_Service_uuid:
                    if service_1.uuid == self.scanner_param["serv_uuid_Custom_Service"]:
                        self.custom_service = service_1
                        break
                self.update_current()

        return res

    async def dicconnect_and_remove(self, index=None):
        if index is None:
            index=self.index
        if index>0 and index<self.limit:
            tag=self.items[index]
            if tag["connected"]:
                try:
                    await tag["client"].disconnect()
                except Exception as e:
                    print(e)
            self.items=self.items.pop[index]
            self.limit=len(self.items)
            if self.index-1>0:
                self.index=self.index-1
            elif self.index + 1 < self.limit:
                self.index = self.index + 1
            else:
                self.index=0

    def find_tag(self, address, set_current=True):
        try:
            res=-1
            index=[x for x in range(len(self.items)) if self.items[x].address==address]
            if len(index)>0:
                index=index[0]
                if set_current:
                    self.set_current(index)
                res= index
        except Exception as e:
            print(e)
        return res

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

    async def check_disconnect(self,client,address):
        try:
            connected=False
            if client is None:
                try:
                    client = BleakClient(address)
                    connected = client.is_connected
                except Exception as e:
                    print(e)
                    connected = False

            if client is not None:
                connected = client.is_connected
                if not connected:
                    try:
                        await client.connect()
                        connected = client.is_connected
                    except Exception as e:
                        print(e)
                        connected=False
                try:
                    char_uuid = self.filter_db(id="tag_mac")[0]["uuid"]
                    char_uuid_val = bytes(await client.read_gatt_char(char_uuid))
                    connected = True
                except Exception as e:
                    print(e)
                    connected = False


        except Exception as e:
            print(e)

            self.connected = connected
            self.update_current()

        return connected

    async def tag_functions(self, action="READ",
                            uuid_filter_id=None, uuid_data_type_filter="base",
                            init_location=False,
                            dfupdate=None, keep_connected=True,csv_read_data=[],param_enable_disable_tags=False):
        client = self.client
        device = self.device
        service=self.custom_service

        app = self.webapp


        address=device.address
        if uuid_data_type_filter=='base':
            csv_row_new = self.csv_row.copy()
        elif uuid_data_type_filter=='detail':
            csv_row_new = self.csv_det_row.copy()
        elif uuid_data_type_filter=='configuration':
            csv_row_new = self.csv_cfg_row.copy()
        else:
            csv_row_new = self.csv_row.copy()

        csv_row_new["mac"] = address
        csv_row_new["name"] = device.name

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

        if service is not None:
            # try to connect
            try:
                result = True
                myDevice_1_address = device.address
                char_uuid_enable_cte = self.filter_db(id="enable_cte")[0]["uuid"]
                char_uuid_update_nfc = self.filter_db(id="update_nfc")[0]["uuid"]
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
                connected=await self.check_disconnect( client, address)

                if connected:
                    print("Connected to Device")
                    print("Performing action {}".format(action))
                    if (app is not None): app.print_statuslog("Performing action {}".format(action))

                    # svcs = await client.get_services()
                    #
                    # print("Services:")
                    # service = None
                    # for service_1 in svcs:
                    #     # if service_1.uuid==serv_uuid_Throughput_Test_Service_uuid:
                    #     if service_1.uuid == serv_uuid_Custom_Service:
                    #         service = service_1
                    #         break
                    if (action == "READ"):
                        if service is not None:

                            scan_list = self.filter_db(id=uuid_filter_id, data_type=uuid_data_type_filter, scan=True)
                            scan_list.extend(self.filter_db(id="status_code"))
                            for k in range(len(scan_list)):
                                try:
                                    char_uuid_id = scan_list[k]['uuid']
                                    id = scan_list[k]['id']
                                    scan = scan_list[k]['scan']
                                    char_uuid_val = bytes(await client.read_gatt_char(char_uuid_id))
                                    print("{0} ({1}): {2}".format(id, scan, char_uuid_val))
                                    if scan:
                                        if (scan_list[k]['type'] == 'HEX'):
                                            val = int.from_bytes(char_uuid_val, byteorder='big')
                                        else:
                                            if type(char_uuid_val) is bytes:
                                                val = char_uuid_val.decode('utf-8')
                                            else:
                                                val = str(char_uuid_val)
                                        scan_list[k]['value'] = val
                                        if (csv_row_new is not None):
                                            if id in csv_row_new.keys():
                                                csv_row_new[id] = val
                                except Exception as e:
                                    if e.errno==22: #THE_OBJECT_HAS_BEEN_CLOSED = 22
                                        msg="Connection closed for address:{} id:{} char_uuid_id:{}".format(address, id, char_uuid_id)
                                        if (app is not None): app.print_statuslog(msg)
                                        print(msg)
                                        print(e)
                                        self.connected = False
                                        self.update_current()
                                        break
                                    else:
                                        msg="error address:{} id:{} char_uuid_id:{}".format(address, id, char_uuid_id)
                                        if (app is not None): app.print_statuslog(msg)
                                        print(msg)
                                        print(e)

                                    result = False


                            csv_read_data.append(csv_row_new)

                            if param_enable_disable_tags!='none':
                                try:
                                    id == "tag_enabled"
                                    char_uuid=self.filter_db(id='tag_enabled', data_type=None, scan=True)
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

                                        valread_raw = await client.read_gatt_char(char_uuid_id)
                                        if valread_raw is not None:
                                            if type(valread_raw) is bytearray:
                                                valread = int.from_bytes(bytes(valread_raw))
                                            else:
                                                pass
                                        else:
                                            valread = bytes(b'')

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

                    if (action == "LOCATION"):
                        ini_loc = False
                        if not init_location:
                            init_location = True
                            start_mqtt = True
                            try:
                                Stop_collecting = False
                                datadf = {}
                                janhors_processed = []
                                datadf_pos = {}
                                datadf_corr = {}
                                jmpos_processed = []
                                jang_corr_processed = []
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
                                res = await client.write_gatt_char(
                                    service.get_characteristic(char_uuid_enable_cte),
                                    bytearray([0x01]),
                                    response=True)
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
                                res = await client.write_gatt_char(
                                    service.get_characteristic(char_uuid_enable_cte),
                                    bytearray([0x00]),
                                    response=True)
                            # else:
                            #    print("disableCTE is FALSE!! - no scan")

                    if (action == "UPDATE"):
                        scan_list = self.filter_db(id=None, data_type=uuid_data_type_filter, scan=True)
                        dfupdate_read = dfupdate.copy()
                        recupdate = dfupdate.copy()
                        if service is not None:
                            rec = dfupdate[dfupdate["mac"] == myDevice_1_address]
                            fupdate = False
                            # # Sart advertisement
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
                                        if not rec[id].isna().values[
                                            0] and scan_list[k]["id"] !="mac":  # only update what is not None (value has changed)
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

                                            if scan_list[k]["id"] != "read_nfc" :
                                                if scan_list[k]['NFC'] == True:
                                                    fupdate = True

                                                if (scan_list[k]['type'] == 'HEX'):
                                                    res = await client.write_gatt_char(
                                                        service.get_characteristic(
                                                            char_uuid_id),
                                                        newval.to_bytes(scan_list[k]['length'], byteorder='big',
                                                                        signed=False),
                                                        response=True)
                                                else:
                                                    res = await client.write_gatt_char(
                                                        service.get_characteristic(char_uuid_id),
                                                        bytearray(newval, 'utf-8'),
                                                        response=True)

                                                # print(res)
                                                valread_raw = await client.read_gatt_char(char_uuid_id)
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
                                    if app is not None:app.print_statuslog(e)
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
                        else:
                            pass

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
             "recupdate":recupdate, "devices_processed_location":devices_processed_location}
        return res

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


class gatewaydb:
    csv_row = {"mac": "", "name": "", "tag_id": "", "asset_id": "", "certificate_id": "", "type": "",
               "expiration_date": "", "color": "", "series": "", "read_nfc": "", "status": "", "status_code": "",
               "asset_images_file_extension": "", "x": "", "y": ""}

    csv_cfg_row = {"mac":"","update_nfc":"","status_code":"","enable_cte":"","tag_enabled":"","tag_advertisement_period":"",
                   "ble_on_period":"","ble_on_wakeup_period":"","ble_off_period":"","tag_periodic_scan":"","tag_mac":"","read_battery_voltage":"",
                   "battery_voltage":"","read_battery_voltage":"","altitude":"","moved":"","status":"","x":"","y":""}

    csv_det_row = {"mac":"","certification_company_name":"","certification_company_id":"","certification_place":"","certification_date":"","test_type":"","asset_diameter":"",
                     "batch_id":"","batch_date":"","machine_id":"","status_code":"","ble_data_crc":"","asset_images_crc":"","logo_images_crc":"","signature_images_crc":"",
                     "owner_company_name":"","owner_data":"","altitude":"","moved":"","battery_voltage":"","status":"","x":"","y":""}

    def __init__(self):
        self.new_csv_row=None
        self.new_csv_cfg_row=None
        self.new_csv_det_row = None
        self.mac=None

    def set_mac(self,mac):
        self.mac=mac

    def dfupdate(self,asdf=True, datatype='base'):
        if asdf:
            res=pd.DataFrame.from_dict(self.new_csv_row)
        else:
            res=self.new_csv_row
        return  res

    def dfupdate_cfg(self, asdf=True):
        if asdf:
            res=pd.DataFrame.from_dict(self.new_csv_cfg_row)
        else:
            res=self.new_csv_cfg_row
        return  res

    def dfupdate_det(self, asdf=True):
        if asdf:
            res=pd.DataFrame.from_dict(self.new_csv_det_row)
        else:
            res=self.new_csv_det_row
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

    def new_csv_cfg_row_id(self):
        if self.new_csv_cfg_row is None:
            self.new_csv_cfg_row = self.csv_cfg_row.copy()
            for x in self.new_csv_cfg_row.keys():
                self.new_csv_cfg_row[x] = np.nan

    def set_csv_cfg_row_id(self, id, value):
        self.new_csv_cfg_row_id()
        res=False
        if id in self.new_csv_cfg_row.keys():
            self.new_csv_cfg_row[id] = [value]
            self.new_csv_cfg_row["mac"] = [self.mac ]
            res = True
        return res

    def new_csv_det_row_id(self):
        if self.new_csv_det_row is None:
            self.new_csv_det_row = self.csv_det_row.copy()
            for x in self.new_csv_det_row.keys():
                self.new_csv_det_row[x] = np.nan

    def set_csv_det_row_id(self, id, value):
        self.new_csv_det_row_id()
        res=False
        if id in self.new_csv_det_row.keys():
            self.new_csv_det_row[id] = [value]
            self.new_csv_det_row["mac"] = [self.mac ]
            res = True
        return res

class boldscanner:

    def __init__(self, serv_uuid_Custom_Service = "87e29466-8be6-4ede-9ffb-04a7121938da",disableCTE_duringlocation=True,keepactive_all_CTE_during_location=False,
                                use_MQTT = False, mqttclient = None, keep_mqtt_on = False,
                                wait_for_mqtt_angles = True, CTE_Wait_Time_prescan = 55, CTE_Wait_Time = 20,webapp=None):
        self.scanner_param={}
        self.scanner_param["serv_uuid_Custom_Service"] = serv_uuid_Custom_Service
        self.scanner_param["disableCTE_duringlocation"] =disableCTE_duringlocation
        self.scanner_param["keepactive_all_CTE_during_location"] =keepactive_all_CTE_during_location
        self.scanner_param["use_MQTT"] =use_MQTT
        self.scanner_param["mqttclient"] =mqttclient
        self.scanner_param["keep_mqtt_on"] =keep_mqtt_on
        self.scanner_param["wait_for_mqtt_angles"] =wait_for_mqtt_angles
        self.scanner_param["CTE_Wait_Time_prescan"] =CTE_Wait_Time_prescan
        self.scanner_param["CTE_Wait_Time"] =CTE_Wait_Time

        # self.scanner.register_detection_callback(self.device_found)
        self.webapp = webapp

        self.tags=boldtag(self.scanner_param,self.webapp)


    def device_found(self,device: BLEDevice, advertisement_data: AdvertisementData):
        print(device.name,device.address)

    async def scan_tags(self,connect=False, max_retry=1):
        try:
            new_tags=[]
            existing_tags=[]
            scanner = BleakScanner()
            devices = await scanner.discover()
            for device in devices:
                # if KeyValueCoding.getKey(d.details, 'name') == 'awesomecoolphone':
                if device.name is not None:
                    try:
                        if device.name.startswith("BoldTag")  :
                            if (self.webapp is not None): self.webapp.print_statuslog("BoldTag  found {}".format(device.address))
                            ix=self.tags.find_tag(device.address)
                            if ix==-1:
                                await self.tags.new(connect=connect, device=device,max_retry=max_retry)
                                new_tags.append(device.address)
                                print("BoldTag {} Added ".format(device.address))
                                if (self.webapp is not None): self.webapp.print_statuslog("BoldTag {} Added ".format(device.address))
                            else:
                                self.tags.set_current(ix)
                                await self.tags.connect(max_retry=max_retry)
                                existing_tags.append(device.address)
                    except Exception as e:
                        print(e)
        except Exception as e:
            print(e)
        return {"new_tags":new_tags,"existing_tags":existing_tags}

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
        bscanner.tags.set_current(i)
        if bscanner.tags.connected:
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
            bscanner.tags.gatewaydb.set_csv_cfg_row_id(id="enable_cte", value=1)
            # bscanner.tags.gatewaydb.set_csv_row_id(id="asset_id", value=np.nan)
            dfupdate_cfg =bscanner.tags.gatewaydb.dfupdate_cfg()
            res_tag = await bscanner.tags.tag_functions(action="UPDATE",uuid_data_type_filter="configuration",dfupdate=dfupdate_cfg)
            print(res_tag)
            res_tag = await bscanner.tags.tag_functions(action="LOCATION", uuid_data_type_filter=None)
            print(res_tag)

        print(res)
    await bscanner.disconnect_all()

    print(res)


if __name__ == "__main__":
    asyncio.run(main())
    print('ff')