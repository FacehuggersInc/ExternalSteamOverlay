from steam import steamworks

import os, json
import glfw
from OpenGL.GL import *


LAUNCH_ID = None

class SteamOverlayLauncher():
    def __init__(self):
        self.APP_NAME = 'External Steam Overlay'
        
        self.config_data : dict = self.get_configuration_data()

        #Data
        self.appid        : str = self.config_data['appid']        #Main Game AppID
        self.launch_id    : str = self.config_data['launch_id']    #AppID for initial launcher (if needed)
        self.process_name : str = self.config_data['process_name'] #final executable file name (ex.: "ffxiv_dx11.exe", "Terraria.exe", "witcher3.exe")
        self.executable   : str = self.config_data['executable']   #Full Filepath to final executable or launcher

        self.window = None

        #Init SteamWorks
        self.initialized = False
        try:
            self.set_appid(self.appid)
            self.initialized = steamworks.initialize()
        except Exception as e:
            print(e)
            input('\n\n press [ENTER]')

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
        glfw.terminate()
    
    ## FILES
    def set_appid(appid:str):
        with open('steam_appid.txt', 'w') as id_file:
            id_file.write(appid)

    def get_configuration_data(self) -> dict | None:
        if os.path.exists('launcher_config.json'):
            with open('launcher_config.json', 'r') as file:
                return json.load(file)
        else: return None

    


if __name__ == "__main__":
    
    app = SteamOverlayLauncher()
    app.run()