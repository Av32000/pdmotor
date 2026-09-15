# pdmotor

A small library for controlling a PDMOVIE Motor Mini via Bluetooth Low Energy (BLE). The library allows you to connect to the motor, calibrate it, set its position, and disconnect.

## Usage

The library is dead simple to use. Due to a limitation in [bluer](https://crates.io/crates/bluer), it requires an asynchronous runtime.

```rust
// Connect to the motor
let motor = PDMotor::connect().await?;

// Request motor calibration
motor.calibrate().await?;

// Set the position of the motor (0-7200)
motor.set_position(3600).await?;
```

## Reverse Engineering

The PDMOVIE Motor Mini advertises itself under the name **"REMOTE AIR"**.

A BLE service with UUID `0000fff0-0000-1000-8000-00805f9b34fb` is used for communication. Commands are sent to the motor using the characteristic with UUID `0000fff2-0000-1000-8000-00805f9b34fb`.

### Connection Handshake

When the device connects, a handshake is performed by sending the following commands three times:

* `@00070\n`
* `@13F04\n`
* `@83F0D\n`

### Protocol Commands

Once the handshake is complete, commands can be sent to the characteristic:

* **Calibration**: Send `@0FF70\n` to request motor calibration.
* **Set Position**: Send `@100XXXXYY\n`
* `XXXX`: The target position (`0`–`7200`) as a 16-bit unsigned integer, formatted as a 4-character little-endian hex string (e.g., decimal `7200` becomes `0x1C20`, which formats to `201C`).
* `YY`: A 2-character hex XOR checksum of all preceding ASCII byte values in the command string (including the leading `@`).