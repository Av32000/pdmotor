# Spoof the motor MAC addr

sudo systemctl restart bluetooth
sleep 3
sudo hcitool cmd 0x3f 0x001 0xE1 0xFA 0x3B 0xBE 0x03 0x91
sleep 1
sudo hciconfig hdi0 reset
sudo hciconfig hdi0
