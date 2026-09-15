use crate::PDMotorPacket;

pub fn encode_packet(packet: PDMotorPacket) -> Vec<u8> {
    let le_bytes = packet.payload.to_le_bytes();
    let payload_hex = format!("{:02X}{:02X}", le_bytes[0], le_bytes[1]);

    let body = format!("@{}{}{}", packet.motor_id, packet.command_id, payload_hex);

    let xor_sum = body.bytes().reduce(|acc, b| acc ^ b).unwrap_or(0);

    let full_packet = format!("{}{:02X}\n", body, xor_sum);
    full_packet.into_bytes()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_encode_packet_examples() {
        // Input: motor_id = '1', command_id = "00", payload = 0
        let res1 = encode_packet(PDMotorPacket {
            motor_id: '1',
            command_id: "00".into(),
            payload: 0,
        });
        assert_eq!(String::from_utf8(res1).unwrap(), "@100000071\n");

        // Input: motor_id = '1', command_id = "00", payload = 7200 (0x1C20 -> little-endian hex "201C")
        let res2 = encode_packet(PDMotorPacket {
            motor_id: '1',
            command_id: "00".into(),
            payload: 7200,
        });
        assert_eq!(String::from_utf8(res2).unwrap(), "@100201C01\n");
    }
}
