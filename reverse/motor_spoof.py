import asyncio
import subprocess
from bless import (
    BlessServer,
    BlessGATTCharacteristic,
    GATTCharacteristicProperties,
    GATTAttributePermissions,
)

SERVICE_UUID = "0000fff0-0000-1000-8000-00805f9b34fb"
TX_CHAR_UUID = "0000fff1-0000-1000-8000-00805f9b34fb"  # Motor -> Handwheel
RX_CHAR_UUID = "0000fff2-0000-1000-8000-00805f9b34fb"  # Handwheel -> Motor

server = None


def read_request(characteristic: BlessGATTCharacteristic, **kwargs) -> bytearray:
    val = characteristic.value or b""
    print(f"\n[READ REQ] UUID: {characteristic.uuid} | Val: {val.hex(' ').upper()}")
    return characteristic.value


def write_request(characteristic: BlessGATTCharacteristic, value: bytes, **kwargs):
    hex_val = value.hex(" ").upper()
    print(f"\n>>> [WRITE REQ RECEIVED] UUID: {characteristic.uuid} | DATA: {hex_val}")
    characteristic.value = value


async def main():
    global server

    print("1. Starting fake motor server on Pi...")
    server = BlessServer(name="REMOTE AIR")
    server.read_request_func = read_request
    server.write_request_func = write_request

    await server.add_new_service(SERVICE_UUID)

    # Handwheel writes commands here (RX)
    await server.add_new_characteristic(
        SERVICE_UUID,
        RX_CHAR_UUID,
        GATTCharacteristicProperties.write
        | GATTCharacteristicProperties.write_without_response
        | GATTCharacteristicProperties.read,
        b"\x00",
        GATTAttributePermissions.readable | GATTAttributePermissions.writeable,
    )

    # Motor sends telemetry/status here (TX) - add notify + indicate + read
    await server.add_new_characteristic(
        SERVICE_UUID,
        TX_CHAR_UUID,
        GATTCharacteristicProperties.notify
        | GATTCharacteristicProperties.read
        | GATTCharacteristicProperties.indicate,
        b"\x00",
        GATTAttributePermissions.readable | GATTAttributePermissions.writeable,
    )

    await server.start()

    print("2. Waiting for BlueZ to stabilize...")
    await asyncio.sleep(2)

    print("3. Injecting iBeacon Manufacturer Data...")
    try:
        subprocess.run(
            [
                "sudo",
                "hcitool",
                "-i",
                "hci0",
                "cmd",
                "0x08",
                "0x0008",
                "1E",
                "02",
                "01",
                "06",
                "1A",
                "FF",
                "4C",
                "00",
                "02",
                "15",
                "52",
                "41",
                "44",
                "49",
                "55",
                "53",
                "4E",
                "45",
                "54",
                "57",
                "4F",
                "52",
                "4B",
                "53",
                "43",
                "4F",
                "00",
                "01",
                "00",
                "02",
                "D2",
                "00",
            ],
            check=True,
        )
    except Exception as e:
        print(f"Failed to inject: {e}")

    print("\n--- PROXY RUNNING: Turn on your handwheel and spin the wheel ---")

    try:
        await asyncio.sleep(36000)
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        await server.stop()


if __name__ == "__main__":
    asyncio.run(main())
