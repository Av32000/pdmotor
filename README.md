# PDMOVIE Motor Mini Reverse Engineering

This repository contains a small library for controlling a PDMOVIE Motor Mini via Bluetooth Low Energy (BLE). The library allows you to connect to the motor, calibrate it, set its position, and disconnect.

* `pdmotor`: The main library for controlling the PDMOVIE Motor Mini.
* `pdcli`: A small command-line interface (CLI) tool that uses the `pdmotor` library to control the motor from the terminal.

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

More information about the protocol can be found in the library README file: [pdmotor/README.md](pdmotor/README.md).