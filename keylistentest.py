from pynput import keyboard

def on_press(key):
    if key == keyboard.Key.esc:
        return False
    try: k = key.char
    except: k = key.name
    if k in ['1', '2', 'left', 'right']:
        print('Key pressed: ' + k)

listener = keyboard.Listener(on_press=on_press)
listener.start()
listener.join()