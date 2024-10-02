from ctypes import windll
h = windll.user32.FindWindowA(b'Shell_TrayWnd', None)
windll.user32.ShowWindow(h, 9)