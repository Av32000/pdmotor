import sys
import re


def parse_btmon():
    # Matches the exact data payload line from btmon output
    pattern = re.compile(r"Data\[\d+\]:\s+([0-9a-fA-F]+)")
    buffer = ""

    print("Listening for HCI packets... (Press Ctrl+C to stop)")

    try:
        for line in sys.stdin:
            match = pattern.search(line)
            if match:
                hex_data = match.group(1)
                try:
                    # Decode hex to ASCII, ignoring invalid bytes
                    ascii_str = bytes.fromhex(hex_data).decode("ascii", errors="ignore")
                    buffer += ascii_str

                    # Reassemble fragmented packets using the newline delimiter
                    if "\n" in buffer:
                        commands = buffer.split("\n")

                        # Print all complete commands in the buffer
                        for cmd in commands[:-1]:
                            if cmd:
                                print(f"Command: {cmd}")

                        # Retain any incomplete fragment in the buffer
                        buffer = commands[-1]
                except ValueError:
                    pass
    except KeyboardInterrupt:
        print("\nExiting parser.")


if __name__ == "__main__":
    parse_btmon()
