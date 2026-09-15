import asyncio
from bleak import BleakClient

MOTOR_MAC = "91:03:BE:3B:FA:E1"
RX_CHAR_UUID = "0000fff2-0000-1000-8000-00805f9b34fb"


def encode_position(position: int) -> bytes:
    # Clamp position to the valid 0-7200 range
    position = max(0, min(7200, int(position)))

    # Convert to 4-character hex and swap bytes (Little-Endian)
    hex_val = f"{position:04X}"
    payload = f"{hex_val[2:4]}{hex_val[0:2]}"

    # Construct the base command string
    cmd_base = f"@100{payload}"

    # Calculate the XOR checksum
    chk = 0
    for char in cmd_base:
        chk ^= ord(char)

    # Append the 2-character hex checksum AND the newline terminator!
    final_cmd = f"{cmd_base}{chk:02X}\n"
    return final_cmd.encode("ascii")


async def main():
    print(f"Connecting to motor at {MOTOR_MAC}...")

    async with BleakClient(MOTOR_MAC) as client:
        print("\n>>> CONNECTED! <<<")

        print("Sending initialization handshake...")
        # The handshake packets, appended with \n
        handshake_packets = [b"@00070\n", b"@13F04\n", b"@83F0D\n"]

        for packet in handshake_packets:
            # Send each 3 times just like the handwheel does
            for _ in range(3):
                await client.write_gatt_char(RX_CHAR_UUID, packet, response=True)
                await asyncio.sleep(0.05)

        print("Handshake complete.")

        # Pause the script here and wait for the Enter key
        await asyncio.to_thread(
            input,
            "Press the 'restore calibration' button on the motor if needed, then press ENTER here to start...",
        )

        print("\nStarting movement sequence...")

        # Test a sequence: Zero -> Middle -> Top -> Middle -> Zero
        test_positions = [0, 200, 500, 1200, 2000, 3000, 4000, 5000, 6000, 7000, 7200]

        for pos in test_positions:
            packet = encode_position(pos)
            print(
                f"Commanding position: {pos} | Packet: {packet.decode('ascii').strip()} | Hex: {packet.hex()} | Binary: {' '.join(format(byte, '08b') for byte in packet)}"
            )

            # Send the command
            await client.write_gatt_char(RX_CHAR_UUID, packet, response=True)

            # Wait a second before the next movement
            await asyncio.sleep(1.0)

        print("Test complete.")


if __name__ == "__main__":
    asyncio.run(main())
