# Point after first spinning command success 

**Bluetooth Low Energy (BLE) Profile & UUIDs**

* **Service UUID**: `0000fff0-0000-1000-8000-00805f9b34fb` [cite: 2]
* **RX Characteristic** (Commands sent to the motor): `0000fff2-0000-1000-8000-00805f9b34fb` (mapped specifically to handle `0x0025` on the physical motor)
* **TX Characteristic** (Telemetry/notifications sent back): `0000fff1-0000-1000-8000-00805f9b34fb` [cite: 2]

**Initialization Handshake Sequence**

* Sent immediately upon connection (typically repeated three times in rapid succession) [cite: 1]:
* `@00070\n` – General broadcast initialization ping [cite: 1]
* `@13F04\n` – Motor 1 link/enable command [cite: 1]
* `@83F0D\n` – Secondary axis (e.g., zoom/iris) activation command [cite: 1]



**Command Packet Structure**

* All packets are ASCII-encoded text strings strictly terminated by a newline character (`\n` or `0x0A`) [cite: 1].
* **Format**: `@` + `[Motor ID]` + `[Command ID]` + `[Little-Endian Hex Payload]` + `[XOR Checksum]` + `\n` [cite: 1]
* **Header (`@`)**: Start-of-frame delimiter [cite: 1].
* **Motor ID (`1`)**: Target motor index [cite: 1].
* **Command ID (`00`)**: Opcode for absolute position target [cite: 1].
* **Payload (`201C`)**: 16-bit unsigned integer formatted as a 4-character little-endian hex string (byte-swapped; e.g., `0x1C20` equals decimal `7200`) [cite: 1].
* **Checksum (`01`)**: 2-character hex XOR sum of all preceding ASCII character byte values in the command [cite: 1].



**Position Scaling & Range**

* **Minimum / Zero Limit**: `0` ($0x0000$, encoded as `@100000071\n`) [cite: 1]
* **Midpoint Reference**: `3605` ($0x0E15$, encoded as `@100150E00\n` variants) [cite: 1]
* **Maximum / Top Limit**: `7200` ($0x1C20$, encoded as `@100201C01\n`) [cite: 1]

**Keep-Alive / Heartbeat Packet**

* Broadcast continuously when the wheel is idle or holding position:
* `@10071\n` (5-character short packet containing its own valid XOR checksum) [cite: 1]



What part of this protocol would you like to map or automate next?
