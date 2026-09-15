use anyhow::Result;
use pdmotor::PDMotor;
use tokio::io::{self, AsyncBufReadExt, BufReader};

#[tokio::main]
async fn main() -> Result<()> {
    println!("Hello, World!");

    let motor = PDMotor::connect().await?;
    println!("Connected to motor: {:?}", motor.device);

    motor.calibrate().await?;

    let mut stdin = BufReader::new(io::stdin());
    let mut line = String::new();

    loop {
        println!("Enter a position value (or press Ctrl+C to exit):");
        line.clear();

        let bytes_read = stdin.read_line(&mut line).await?;
        if bytes_read == 0 {
            break;
        }

        let input = line.trim();

        if input.is_empty() {
            continue;
        } else if input.eq_ignore_ascii_case("exit") {
            break;
        }

        match input.parse::<u16>() {
            Ok(pos) => {
                println!("Setting position to: {}", pos);
                if let Err(e) = motor.set_position(pos).await {
                    eprintln!("Failed to send command: {}", e);
                }
            }
            Err(_) => {
                eprintln!(
                    "Invalid input: '{}'. Please enter a valid positive number.",
                    input
                );
            }
        }
    }

    println!("Disconnecting from motor...");

    motor.disconnect().await?;

    Ok(())
}
