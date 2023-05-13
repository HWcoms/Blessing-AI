import keyboard
import subprocess
import time

def on_press(event):
    # Run the first executable when 'f' key is pressed and held down
    subprocess.Popen(r'C:\Users\HWcoms\Documents\오디오컨트롤\케이블 마이크.bat')
    
def on_release(event):
    # Wait for a short time before running the second executable
    time.sleep(0.5)
    # Run the second executable when 'f' key is released
    subprocess.Popen(r'C:\Users\HWcoms\Documents\오디오컨트롤\마이크.bat')
    
# Register the key events
keyboard.on_press_key('f', on_press)
keyboard.on_release_key('f', on_release)

# Keep the program running to listen to key events
keyboard.wait()