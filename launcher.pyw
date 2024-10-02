
import os, sys, json, glfw, ctypes, time, psutil
from PIL import Image
from pynput.keyboard import Key, Listener, Controller
from OpenGL.GL import *
from steamworks import STEAMWORKS

user32 = ctypes.windll.user32

os.add_dll_directory(os.getcwd())

class SteamOverlayLauncher():
    def __init__(self):
        self.APP_NAME = 'External Steam Overlay'

        self.initialized = False
        self.window = None
        self.last_focused_window = None
        self.focused = False
        self.__steam_overlay_visible = False

        #Keyboard Listener
        self.hotkey_pressed = False
        self.HOTKEY = {Key.ctrl_l, Key.tab}
        self.COMBO = set()
        self.key_listener = Listener(on_press=self.on_key_pressed, on_release=self.on_key_released)
        self.key_controller = Controller()

        #Create Folder and Template File
        if not os.path.exists('./Configs'):
            os.mkdir('Configs')

            with open('Configs\\new_config.json', 'w') as new_json:
                data = {
                    "launch_id"    : "",
                    "appid"        : "",
                    "process_name" : "",
                    "executable"   : ""
                }
                json.dump(data, new_json)

        #Get Configuration Json Path from Args
        config_path = None
        if len(sys.argv) >= 2:
            config_path = sys.argv[1]

        #Load the Config File
        self.config_data :dict = None
        if config_path: 
            self.config_data = self.get_configuration_data(config_path)
            print(f'Loading Config: {config_path}')
        if self.config_data:
            #Data
            self.appid        : str = self.config_data['appid']        #Main Game AppID
            self.launch_id    : str = self.config_data['launch_id']    #AppID for initial launcher (if needed)
            self.process_name : str = self.config_data['process_name'] #final executable file name (ex.: "ffxiv_dx11.exe", "Terraria.exe", "witcher3.exe")
            self.executable   : str = self.config_data['executable']   #Full Filepath to final executable or launcher

            #Start Executable
            if self.executable: os.startfile(self.executable) #DEBUG

            #Init SteamWorks
            self.steamworks = STEAMWORKS()
            try:
                self.set_appid(self.appid)
                self.initialized = self.steamworks.initialize()
            except Exception as e:
                print(e)
                input('PRESS')

    ## KEY
    def on_key_pressed(self, key):
        if not key in self.COMBO:
            self.COMBO.add(key)
        else:
            return

        if not self.hotkey_pressed and self.COMBO == self.HOTKEY:
            self.hotkey_pressed = True
            if self.focused == False:
                self.focused = True

                self.hide_taskbar()

                to_set = self.get_focused_window_hwnd()
                if not self.get_window_title_debug(to_set) == self.APP_NAME and to_set:
                    self.last_focused_window = to_set
                    

                glfw.restore_window(self.window)
                glfw.focus_window(self.window)
                self.set_topmost(self.window)

                ## Open Overlay (Once)
                if not self.__steam_overlay_visible:
                    time.sleep(1)

                    self.key_controller.press(Key.shift_l)
                    self.key_controller.press(Key.tab)
                    time.sleep(0.05)
                    self.key_controller.release(Key.shift_l)
                    self.key_controller.release(Key.tab)
                    
                    self.__steam_overlay_visible = True

                print(f'Showing Overlay')
                return

            elif self.focused == True:
                self.focused = False

                self.show_taskbar()
                glfw.iconify_window(self.window)

                if self.last_focused_window:
                    self.set_focus_on_window(self.last_focused_window)
                    print(f'Hiding Overlay, Focusing on: {self.get_window_title_debug(self.last_focused_window)}')

    def on_key_released(self, key):
        if key in self.COMBO:
            self.COMBO.remove(key)

        if not self.COMBO == self.HOTKEY:
            self.hotkey_pressed = False

    ## 
    def run(self):
        """Main Function / BLOCKING"""
        if not self.initialized: 
            return
        
        self.key_listener.start()
        
        self.init_window()
        self.update_window() #BLOCKING


    ## TOOLS
    def set_icon(self, path:str):
        icon_image = Image.open(path).convert('RGBA')
        icon_width, icon_height = icon_image.size
        icon_data = icon_image.tobytes()

        # Create a GLFWimage and set it as the window icon
        icon = glfw.Image(icon_width, icon_height, icon_data)
        glfw.set_window_icon(self.window, 1, [icon])

    def show_taskbar(self):
        h = user32.FindWindowA(b'Shell_TrayWnd', None)
        user32.ShowWindow(h, 9)

    def hide_taskbar(self):
        h = user32.FindWindowA(b'Shell_TrayWnd', None)
        user32.ShowWindow(h, 0)

    def set_window_transparency(self, transparent):
        hwnd = glfw.get_win32_window(self.window)
        
        """if ctypes.sizeof(ctypes.c_void_p) == 8:  # 64-bit
            GetWindowLongPtr = user32.GetWindowLongPtrW
        else:  # 32-bit
            GetWindowLongPtr = user32.GetWindowLongW"""

        ex_style = user32.GetWindowLongPtrW(hwnd, -20)  # Use GetWindowLongPtr
        if transparent:
            user32.GetWindowLongPtrW(hwnd, -20, ex_style | 0x80000 | 0x2000000)  # WS_EX_LAYERED
            user32.SetLayeredWindowAttributes(hwnd, 0, 0, 0x00000002)  # LWA_ALPHA, semi-transparent
        else:
            user32.GetWindowLongPtrW(hwnd, -20, ex_style & ~0x80000 & ~0x2000000)  # Remove WS_EX_LAYERED
            user32.SetLayeredWindowAttributes(hwnd, 0, 255, 0x00000001)  # LWA_ALPHA, fully opaque

    def set_focus_on_window(self, hwnd):
        # Set the specified window as the foreground window
        user32.SetForegroundWindow(hwnd)

    def set_window_no_activate(self, window):
        hwnd = glfw.get_win32_window(window)  # Get the HWND for the GLFW window
        ex_style = user32.GetWindowLongPtrW(hwnd, -20)  # Get the current extended window style
        user32.SetWindowLongPtrW(hwnd, -20, ex_style | 0x08000000)  # Add WS_EX_NOACTIVATE

    def loose_focus(self, window):
        hwnd = glfw.get_win32_window(window)  # Get the HWND for the GLFW window
        # Set the window to the bottom of the Z-order (background)
        user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0, 0x0001)  # SWP_NOMOVE | SWP_NOSIZE

    def get_focused_window_hwnd(self):
        # Get the handle of the currently focused window
        hwnd = user32.GetForegroundWindow()
        return hwnd

    def get_window_title_debug(self, hwnd):
        # Allocate a buffer for the window title
        buffer_size = 256
        buffer = ctypes.create_unicode_buffer(buffer_size)
        
        # Get the window title
        length = user32.GetWindowTextW(hwnd, buffer, buffer_size)
        
        if length > 0:
            return buffer.value
        else:
            return None  # Return None if there was an error or the title is empty

    def set_topmost(self, window):
        hwnd = glfw.get_win32_window(window)
        user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0002 | 0x0001 | 0x0040)

    ## WINDOW
    def init_window(self):
        if not glfw.init():
            raise Exception("glfw can not be initialized!")

        # Configure window to be transparent
        glfw.window_hint(glfw.TRANSPARENT_FRAMEBUFFER, glfw.TRUE)
       
        # Get the primary monitor
        monitor : glfw._GLFWmonitor = glfw.get_primary_monitor()
        MVM : glfw._GLFWvidmode = glfw.get_video_mode(monitor)

        # Create a windowed mode window and its OpenGL context
        self.window = glfw.create_window(MVM.size.width, MVM.size.height + (42 * 2), self.APP_NAME, None, None)

        glfw.set_window_pos(self.window, 0, 0)

        self.set_window_transparency(False)

        #No Decorations
        glfw.set_window_attrib(self.window, glfw.DECORATED, False)

        # Make the window's context current
        glfw.make_context_current(self.window)

        self.set_icon('steam.png')

        glfw.iconify_window(self.window)

    def update_window(self):
        """Main Loop"""
        while not glfw.window_should_close(self.window):

            ## WINDOW RENDER
            
            # Render here, e.g. using pyOpenGL
            glClearColor(0.0, 0.0, 0.0, 0.0)  # Set the background transparent
            glClear(GL_COLOR_BUFFER_BIT)

            # Swap front and back buffers
            glfw.swap_buffers(self.window)

            # Poll for and process events
            glfw.poll_events()
        
        self.stop_process()

    def stop_process(self):
        self.show_taskbar()

        self.key_listener.stop()

        if self.launch_id: 
            self.set_appid(self.launch_id)
        else:
            self.set_appid('')

        try:
            glfw.terminate()
        except: pass
    
    ## FILES
    def set_appid(self, appid:str):
        with open('steam_appid.txt', 'w') as id_file:
            id_file.write(appid)

    def get_configuration_data(self, file) -> dict | None:
        if file: file = os.path.basename(file)
        if os.path.exists(f'Configs\\{file}'):
            with open(f'Configs\\{file}', 'r') as file:
                return json.load(file)
        else: return None

## RUNNING APP

if __name__ == "__main__":
    
    app = SteamOverlayLauncher()
    app.run() #BLOCKING
    app.show_taskbar()