pub mod client;
mod codec;

pub struct PDMotorPacket {
    pub motor_id: char,
    pub command_id: String,
    pub payload: u16,
}
