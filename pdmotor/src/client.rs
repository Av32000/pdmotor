use std::time::Duration;

use anyhow::Result;
use bluer::{
    Device, Session,
    gatt::remote::{Characteristic, CharacteristicWriteRequest},
};
use futures_util::StreamExt;
use tokio::time::sleep;
use uuid::Uuid;

const REMOTE_AIR_NAME: &str = "REMOTE AIR";
const RX_CHAR_UUID: Uuid = Uuid::from_u128(0x0000fff2_0000_1000_8000_00805f9b34fb);

const HANDSHAKE_PACKETS: [&[u8]; 3] = [b"@00070\n", b"@13F04\n", b"@83F0D\n"];

pub struct PDMotor {
    #[allow(dead_code)]
    session: Session,
    pub device: Device,
    rx_char: Characteristic,
}

impl Drop for PDMotor {
    fn drop(&mut self) {
        let device = self.device.clone();
        tokio::spawn(async move {
            device
                .disconnect()
                .await
                .expect("Failed to disconnect device");
        });
    }
}

impl PDMotor {
    pub async fn connect() -> Result<Self> {
        let session = Session::new().await?;

        let device = connect_motor(&session).await?;

        let mut target_char = None;
        for service in device.services().await? {
            for char in service.characteristics().await? {
                if char.uuid().await? == RX_CHAR_UUID {
                    target_char = Some(char);
                    break;
                }
            }
        }

        let rx_char = target_char.expect("Failed to find the RX Characteristic");
        let write_options = CharacteristicWriteRequest {
            op_type: bluer::gatt::WriteOp::Request,
            ..Default::default()
        };

        for packet in HANDSHAKE_PACKETS {
            for _ in 0..3 {
                rx_char.write_ext(&packet.to_vec(), &write_options).await?;
                sleep(Duration::from_millis(50)).await;
            }
        }

        Ok(PDMotor {
            session,
            device,
            rx_char,
        })
    }

    pub async fn send_packet(&self, packet: crate::PDMotorPacket) -> Result<()> {
        self.connection_check().await?;

        let encoded_packet = crate::codec::encode_packet(packet);

        println!("Sending packet: {:?}", encoded_packet);

        let write_options = CharacteristicWriteRequest {
            op_type: bluer::gatt::WriteOp::Request,
            ..Default::default()
        };
        self.rx_char
            .write_ext(&encoded_packet, &write_options)
            .await?;
        Ok(())
    }

    pub async fn send_raw(&self, data: &[u8]) -> Result<()> {
        self.connection_check().await?;

        println!("Sending raw data: {:?}", data);

        let write_options = CharacteristicWriteRequest {
            op_type: bluer::gatt::WriteOp::Request,
            ..Default::default()
        };
        self.rx_char
            .write_ext(&data.to_vec(), &write_options)
            .await?;
        Ok(())
    }

    pub async fn disconnect(&self) -> Result<()> {
        self.device.disconnect().await?;
        Ok(())
    }

    async fn connection_check(&self) -> Result<()> {
        if !self.device.is_connected().await? {
            anyhow::bail!("Device is not connected");
        }
        Ok(())
    }
}

async fn connect_motor(session: &Session) -> Result<Device> {
    let adapter = session.default_adapter().await?;
    adapter.set_powered(true).await?;

    let mut discover = adapter.discover_devices().await?;
    while let Some(evt) = discover.next().await {
        match evt {
            bluer::AdapterEvent::DeviceAdded(address) => {
                let device = adapter.device(address)?;
                if device.name().await?.as_deref() == Some(REMOTE_AIR_NAME) {
                    device.connect().await?;
                    return Ok(device);
                }
            }
            _ => {}
        }
    }
    Err(anyhow::anyhow!("Device not found"))
}
