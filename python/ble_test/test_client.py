from bleak import BleakClient, BleakScanner

import asyncio

# Replace with the UUID of the GATT characteristic you want to read
CHARACTERISTIC_UUID = "c01cdf18-2465-4df6-956f-fde4867e2bc1"

CHARACTERISTIC_UUID_Tag_Enabled="886eb62a-2c17-4e8e-9579-1c5483973577"

async def read_gatt_characteristic(client, uuid):
    """Reads the specified GATT characteristic from a connected device."""
    try:
        value = await client.read_gatt_char(uuid)
        print(f"Read value from {client.address}: {value}")
        return value
    except Exception as e:
        print(f"Error reading characteristic from {client.address}: {e}")
        return None


async def write_gatt_characteristic(client, char_uuid_id,newval,length=1):
    """Reads the specified GATT characteristic from a connected device."""
    try:
        svcs = await client.get_services()
        for service_1 in svcs:
            # if service_1.uuid==serv_uuid_Throughput_Test_Service_uuid:
            if service_1.uuid == "87e29466-8be6-4ede-9ffb-04a7121938da":
                service=service_1
                break

        res = await client.write_gatt_char(service.get_characteristic(char_uuid_id), newval.to_bytes(length, byteorder='big',signed=False), response=True)
    except Exception as e:
        print(e)


async def conn(client):
    try:
        res=False
        res = await client.connect()
    except Exception as e :
        print(e)
    return res

async def connect_and_read():
    # Scan for nearby BLE devices
    devices = await BleakScanner.discover(25)
    connected_clients = []

    for device in devices:
        if device.name is not None:
            if device.name.startswith("BoldTag") or device.name.startswith("TGS") :
                client =  BleakClient(device.address)
                try:
                    # async with BleakClient(device.address) as client:
                    #     res=True
                    # res=await client.connect()
                    res= await conn(client)
                    if res:
                        if res:
                            print(f"Connected to {device.name} ({device.address})")
                            connected_clients.append(client)

                            newval=1
                            write_gatt_characteristic(client, CHARACTERISTIC_UUID_Tag_Enabled, newval, length=1)

                            # Read the GATT characteristic
                            await read_gatt_characteristic(client, CHARACTERISTIC_UUID)

                            try:
                                value = await client.read_gatt_char(CHARACTERISTIC_UUID)
                                print(f"Read value from {client.address}: {value}")
                                #return value
                            except Exception as e:
                                print(f"Error reading characteristic from {client.address}: {e}")
                                return None

                            try:
                                client=connected_clients[0]
                                value = await client.read_gatt_char(CHARACTERISTIC_UUID)
                                print(f"Read value from {client.address}: {value}")
                                #return value
                            except Exception as e:
                                print(f"Error reading characteristic from {client.address}: {e}")
                                return None

                except Exception as e:
                    print(f"Error connecting to {device.name} ({device.address}): {e}")
                finally:
                    # Disconnect each client after reading
                    if client.is_connected:
                        await client.disconnect()


# Run the async function
asyncio.run(connect_and_read())
print('ff')