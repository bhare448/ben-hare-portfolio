import serial
import subprocess
import os
import signal
from adafruit_pn532.uart import PN532_UART

# Set up serial and PN532
uart = serial.Serial("/dev/serial0", baudrate=115200, timeout=1)
pn532 = PN532_UART(uart, debug=False)

ic, ver, rev, support = pn532.firmware_version
print(f'Found PN532 with firmware version: {ver}.{rev}')

pn532.SAM_configuration()
print('Waiting for an NFC tag...')


nfc_to_song = {
    '0443aa01280403': '/home/bhare/Music/song1.mp3',
    '04008d01ee4b03': '/home/bhare/Music/song2.mp3',
    '04431501070403': '/home/bhare/Music/song3.mp3',
    '041b5dfa2d5981': '/home/bhare/Music/song4.mp3'
}

# Track current playing process
current_process = None
current_uid = None

while True:
    uid = pn532.read_passive_target(timeout=0.5)
    if uid is None:
        continue

    uid_str = ''.join('{:02x}'.format(x) for x in uid)
    if uid_str == current_uid:
        continue  # Don't restart the song if the same tag is still present

    print('Found card with UID:', uid_str)

    if uid_str in nfc_to_song:
        song_path = nfc_to_song[uid_str]
        print(f'Playing: {song_path}')

        # Stop current song if one is playing
        if current_process is not None:
            try:
                os.killpg(os.getpgid(current_process.pid), signal.SIGTERM)
            except Exception as e:
                print(f"Error stopping previous song: {e}")

        # Start new song
        current_process = subprocess.Popen(
            ['cvlc', '--intf', 'dummy', '--quiet', '--play-and-exit', song_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            preexec_fn=os.setsid
        )

        current_uid = uid_str

    else:
        print('Unknown tag.')

