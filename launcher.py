
import os, sys, json, glfw
from OpenGL.GL import *
from steamworks import STEAMWORKS

os.add_dll_directory(os.getcwd())

class SteamOverlayLauncher():
    def __init__(self):
        self.APP_NAME = 'External Steam Overlay'
        
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

        self.config_data : dict = self.get_configuration_data(sys.argv[1])
        if not self.config_data:
            #Data
            self.appid        : str = self.config_data['appid']        #Main Game AppID
            self.launch_id    : str = self.config_data['launch_id']    #AppID for initial launcher (if needed)
            self.process_name : str = self.config_data['process_name'] #final executable file name (ex.: "ffxiv_dx11.exe", "Terraria.exe", "witcher3.exe")
            self.executable   : str = self.config_data['executable']   #Full Filepath to final executable or launcher

            self.window = None

            #Init SteamWorks
            self.steamworks = STEAMWORKS()
            self.initialized = False
            try:
                self.set_appid(self.appid)
                self.initialized = self.steamworks.initialize()
            except Exception as e:
                pass #NEED ERROR DISPLAY

    ## CORE
    def run(self):
        """Main Function / BLOCKING"""
        if not self.initialized: 
            return
        
        self.init_window()
        self.update_window() #BLOCKING

    def init_window(self):
        if not glfw.init():
            raise Exception("glfw can not be initialized!")

        # Configure window to be transparent
        glfw.window_hint(glfw.TRANSPARENT_FRAMEBUFFER, glfw.TRUE)

        # Get the primary monitor
        monitor : glfw._GLFWmonitor = glfw.get_primary_monitor()
        MVM : glfw._GLFWvidmode = glfw.get_video_mode(monitor)

        # Create a windowed mode window and its OpenGL context
        self.window = glfw.create_window(MVM.size.width, MVM.size.height, self.APP_NAME, None, None)

        # Make the window's context current
        glfw.make_context_current(self.window)

    def update_window(self):
        """Window Loop"""
        while not glfw.window_should_close(self.window):

            ## LOGIC

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
        self.set_appid(self.launch_id)
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
    app.run()