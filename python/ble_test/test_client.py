from bleak import BleakClient, BleakScanner

import asyncio

# Replace with the UUID of the GATT characteristic you want to read
CHARACTERISTIC_UUID = "c01cdf18-2465-4df6-956f-fde4867e2bc1"


async def read_gatt_characteristic(client, uuid):
    """Reads the specified GATT characteristic from a connected device."""
    try:
        value = await client.read_gatt_char(uuid)
        print(f"Read value from {client.address}: {value}")
        return value
    except Exception as e:
        print(f"Error reading characteristic from {client.address}: {e}")
        return None


async def connect_and_read():
    # Scan for nearby BLE devices
    devices = await BleakScanner.discover()
    connected_clients = []

    for device in devices:
        if device.name is not None:
            if device.name=="BoldTag":
                client = BleakClient(device.address)
                try:
                    res=await client.connect()
                    if res:
                        if res:
                            print(f"Connected to {device.name} ({device.address})")
                            connected_clients.append(client)

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