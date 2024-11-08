class MyClass:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def display(self):
        print(f"{self.name}: {self.value}")



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
        self.custom_service=None
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

        self.gatewaydb = gatewaydb()
        self.gatewaydb.set_mac(self.address)
        self.csv_row_previous = {}
        self.csv_row_last = {}
        self.csv_row = self.gatewaydb.csv_row
        # self.csv_cfg_row = self.gatewaydb.csv_cfg_row
        # self.csv_det_row = self.gatewaydb.csv_det_row
        self.connect_retries=0
        self.max_connect_retries=max_connect_retries




class MyClass2:
    def __init__(self, name, value):
        # Create instances of MyClass
        # obj1 = ble_tag("Object1", 10)
        # obj2 = ble_tag("Object2", 20)
        # obj3 = ble_tag("Object3", 30)
        #
        # Add instances to a list
        # class_collection = [obj1, obj2, obj3]
        # self.class_collection=None
        # self.class_collection.append(obj1)
        # self.class_collection.append(obj1)
        # self.class_collection.append(obj3)

    def __iter__(self):
        self._index=-1
        return self

    async def new(self,obj1):
        obj1 = ble_tag("Object1", 10)
        if a==1:
            self.class_collection1 = []
        self.class_collection1.append(obj1)
        item=self.class_collection1[0]
        return item

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


    async def test(self):
        # Modify an instance through the list
        self.class_collection[0]
        # Access and use the instances from the list
        for obj in self.class_collection1:
            obj.display()







class boldtag:

    serv_uuid_Custom_Service = "87e29466-8be6-4ede-9ffb-04a7121938da"

    def __init__(self,scanner_param, webapp=None,rssi_tag_scan=None,directory="//"):
        self.scanner_param=scanner_param
        self.webapp=webapp
        self.limit = 0
        # self.index = 0
        self.items = []
        # self.current= None
        self._index = 0
        self.directory=directory
        self.rssi_tag_scan=rssi_tag_scan


        # self.gatewaydb = gatewaydb()

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

    async def new(self, device, connect=False, max_retry=3, timeout=15):
        # add new data
        try:
            item = None
            # item=ble_tag(device=device, webapp=self.webapp, index=self.index,scanner_param=self.scanner_param)
            self.items.append(MyClass())

            self.limit = self.limit + 1
            self._index = self.limit - 1  # self.set_current(self.limit-1)
            item = self.items[self._index]
            if connect:
                res = False
                # try:
                #     await self.items[self._index].connect(max_retry=max_retry, timeout=timeout)
                #     res = self.items[self._index].connected
                # except Exception as e:
                #     print(e)
                #
                # if res:
                #     self.webapp.print_statuslog("BoldTag {} connected!".format(self.items[self._index].address))
                # else:
                #     self.webapp.print_statuslog("BoldTag {} fail to connect".format(self.items[self._index].address))
                # # msg="BoldTag {} Added and connected".format(device.address)
                # print(msg)
                # if (self.webapp is not None): self.webapp.print_statuslog(msg)
            else:
                msg = "BoldTag {} Added fail to connect".format(device.address)
                # print(msg)
                # if (self.webapp is not None): self.webapp.print_statuslog(msg)
        except Exception as e:
            print(e)
            # msg = "BoldTag {} error: {} ".format(device.address, e)
            # if (self.webapp is not None): self.webapp.print_statuslog(msg)
        return item