# simple_server.py - Only needs pyautogui
import socket
import json
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
import ctypes
from ctypes import wintypes
import time
import os

# Windows API constants
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_WHEEL = 0x0800

KEYEVENTF_KEYUP = 0x0002

# Key codes for common keys
KEY_CODES = {
    'backspace': 0x08,
    'tab': 0x09,
    'return': 0x0D,
    'enter': 0x0D,
    'shift': 0x10,
    'ctrl': 0x11,
    'alt': 0x12,
    'escape': 0x1B,
    'space': 0x20,
}

class WindowsController:
    def __init__(self):
        self.user32 = ctypes.windll.user32
        self.kernel32 = ctypes.windll.kernel32
    
    def move_mouse(self, dx, dy):
        """Move mouse cursor relatively"""
        try:
            current_pos = wintypes.POINT()
            self.user32.GetCursorPos(ctypes.byref(current_pos))
            new_x = current_pos.x + dx
            new_y = current_pos.y + dy
            self.user32.SetCursorPos(new_x, new_y)
        except Exception as e:
            print(f"Mouse move error: {e}")
    
    def click(self, button='left'):
        """Simulate mouse click"""
        try:
            if button == 'left':
                self.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                time.sleep(0.01)
                self.user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            elif button == 'right':
                self.user32.mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
                time.sleep(0.01)
                self.user32.mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
        except Exception as e:
            print(f"Click error: {e}")
    
    def double_click(self):
        """Simulate double click"""
        self.click('left')
        time.sleep(0.05)
        self.click('left')
    
    def scroll(self, direction):
        """Simulate mouse scroll"""
        try:
            wheel_delta = 120 if direction == 'up' else -120
            self.user32.mouse_event(MOUSEEVENTF_WHEEL, 0, 0, wheel_delta, 0)
        except Exception as e:
            print(f"Scroll error: {e}")
    
    def type_text(self, text):
        """Type text using keyboard events"""
        try:
            for char in text:
                # Convert character to virtual key code
                vk = self.user32.VkKeyScanW(ord(char))
                if vk != -1:
                    # Key down
                    self.user32.keybd_event(vk & 0xFF, 0, 0, 0)
                    time.sleep(0.01)
                    # Key up
                    self.user32.keybd_event(vk & 0xFF, 0, KEYEVENTF_KEYUP, 0)
                    time.sleep(0.01)
        except Exception as e:
            print(f"Type text error: {e}")
    
    def press_key(self, key):
        """Press a special key"""
        try:
            key_lower = key.lower()
            if key_lower in KEY_CODES:
                vk = KEY_CODES[key_lower]
                # Key down
                self.user32.keybd_event(vk, 0, 0, 0)
                time.sleep(0.01)
                # Key up  
                self.user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)
        except Exception as e:
            print(f"Key press error: {e}")
    
    def key_combo(self, keys):
        """Press key combination like Alt+Tab"""
        try:
            # Press all keys down
            vk_keys = []
            for key in keys:
                key_lower = key.lower().replace('_l', '').replace('control', 'ctrl')
                if key_lower in KEY_CODES:
                    vk = KEY_CODES[key_lower]
                    vk_keys.append(vk)
                    self.user32.keybd_event(vk, 0, 0, 0)
                elif len(key) == 1:
                    vk = self.user32.VkKeyScanW(ord(key))
                    if vk != -1:
                        vk_keys.append(vk & 0xFF)
                        self.user32.keybd_event(vk & 0xFF, 0, 0, 0)
            
            time.sleep(0.05)
            
            # Release all keys
            for vk in reversed(vk_keys):
                self.user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)
                
        except Exception as e:
            print(f"Key combo error: {e}")

class CommandHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.controller = WindowsController()
        super().__init__(*args, **kwargs)
    
    def do_POST(self):
        if self.path == '/command':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                command = json.loads(post_data.decode('utf-8'))
                
                self.handle_command(command)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'POST')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                self.end_headers()
                self.wfile.write(b'{"status": "ok"}')
                
            except Exception as e:
                print(f"Command error: {e}")
                self.send_response(500)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(f'{{"error": "{str(e)}"}}'.encode())
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def handle_command(self, command):
        """Process the received command"""
        cmd_type = command.get('type')
        print(f"Executing command: {cmd_type}")
        
        if cmd_type == 'mouse_move':
            self.controller.move_mouse(command.get('x', 0), command.get('y', 0))
        
        elif cmd_type == 'left_click':
            self.controller.click('left')
        
        elif cmd_type == 'right_click':
            self.controller.click('right')
        
        elif cmd_type == 'double_click':
            self.controller.double_click()
        
        elif cmd_type == 'scroll':
            self.controller.scroll(command.get('direction', 'up'))
        
        elif cmd_type == 'type_text':
            self.controller.type_text(command.get('text', ''))
        
        elif cmd_type == 'key':
            self.controller.press_key(command.get('key', ''))
        
        elif cmd_type == 'key_combo':
            self.controller.key_combo(command.get('keys', []))

def get_local_ip():
    """Get the local IP address"""
    try:
        # Connect to a remote server to determine local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return socket.gethostname()

if __name__ == '__main__':
    local_ip = get_local_ip()
    port = 8000
    
    print("=" * 50)
    print("Phone Mouse & Keyboard Server")
    print("=" * 50)
    print(f"Server IP: {local_ip}")
    print(f"Server Port: {port}")
    print(f"\nOpen this URL on your phone:")
    print(f"http://{local_ip}:{port}")
    print("\nMake sure your phone and laptop are on the same WiFi network!")
    print("=" * 50)
    
    try:
        httpd = HTTPServer(('0.0.0.0', port), CommandHandler)
        print(f"Server started successfully!")
        print("Waiting for phone connections...")
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Server error: {e}")
        input("Press Enter to exit...")