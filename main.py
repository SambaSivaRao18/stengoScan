import os
import threading
import sys

# Attempt to import Kivy, handle missing module gracefully
try:
    from kivy.app import App
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.label import Label
    from kivy.uix.button import Button
    from kivy.uix.scrollview import ScrollView
    from kivy.uix.popup import Popup
    from kivy.clock import Clock
    from kivy.utils import platform
except ImportError:
    print("WARNING: Kivy not found. UI will not be available.")
    print("Please install Kivy using: pip install kivy")
    # Simulation/CLI mode fallback
    platform = 'pc'
    class App:
        def run(self): pass

# Import custom modules
try:
    from engine.steganalysis import check_stego
    from utils.observer import start_listening, trigger_notification
except ImportError as e:
    print(f"Import Error: {e}")
    def check_stego(path): return False
    def start_listening(cb): return None
    def trigger_notification(t, m): print(f"NOTIF: {t} - {m}")

class StegoApp(App):
    def build(self):
        self.title = "SteganoScan Sentinel"
        self.root = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        self.root.add_widget(Label(
            text="[b]SteganoScan Sentinel[/b]",
            markup=True, font_size='24sp', size_hint_y=None, height=50
        ))
        
        self.status_label = Label(
            text="Service Status: Not Started",
            color=(0.8, 0.8, 0.2, 1)
        )
        self.root.add_widget(self.status_label)
        
        self.scroll = ScrollView()
        self.log_text = Label(
            text="App Ready.\n",
            size_hint_y=None, valign='top', halign='left', markup=True
        )
        self.log_text.bind(texture_size=self.log_text.setter('size'))
        self.scroll.add_widget(self.log_text)
        self.root.add_widget(self.scroll)
        
        btn_layout = BoxLayout(size_hint_y=None, height=100, spacing=10)
        self.service_btn = Button(
            text="Start Sentinel Service",
            background_color=(0.2, 0.6, 0.2, 1)
        )
        self.service_btn.bind(on_release=self.check_and_start)
        btn_layout.add_widget(self.service_btn)
        self.root.add_widget(btn_layout)

        if platform != 'android':
            self.observer = start_listening(self.on_media_changed)
            if self.observer:
                self.add_log("[color=00ff00]PC Observer Active.[/color]")
        
        return self.root

    def check_and_start(self, *args):
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            perms = [Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE]
            try:
                # API 33+ permissions
                perms.extend([Permission.READ_MEDIA_IMAGES, Permission.POST_NOTIFICATIONS])
            except: pass
            request_permissions(perms, self.start_sentinel_service)
        else:
            self.start_sentinel_service()

    def start_sentinel_service(self, permissions=None, grants=None):
        self.add_log("Starting service...")
        if platform == 'android':
            try:
                from jnius import autoclass
                # buildozer.spec: services = SentinelService:service.py
                service_name = 'org.cyberwarlab.steganoscan.ServiceSentinelservice'
                service = autoclass(service_name)
                mActivity = autoclass('org.kivy.android.PythonActivity').mActivity
                service.start(mActivity, "")
                self.add_log("[color=00ff00]Service launch triggered.[/color]")
                self.status_label.text = "Service Status: Running"
                self.status_label.color = (0.2, 0.8, 0.2, 1)
            except Exception as e:
                self.add_log(f"[color=ff0000]Launch Error: {e}[/color]")
        else:
            self.add_log("Service only works on Android.")

    def on_media_changed(self, path):
        self.add_log(f"New image: {os.path.basename(path)}")
        self.run_scan(path)

    def run_scan(self, path):
        def scan_thread():
            is_stego = check_stego(path)
            Clock.schedule_once(lambda dt: self.handle_scan_result(path, is_stego))
        threading.Thread(target=scan_thread).start()

    def handle_scan_result(self, path, is_stego):
        basename = os.path.basename(path)
        if is_stego:
            self.add_log(f"[color=ff0000]ALERT: Stego in {basename}[/color]")
            self.show_alert_popup(basename)
        else:
            self.add_log(f"Clean: {basename}")

    def add_log(self, message):
        def update_log(dt):
            self.log_text.text += f"{message}\n"
        Clock.schedule_once(update_log)

    def show_alert_popup(self, filename):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(
            text=f"[b][color=ff3333]THREAT DETECTED[/color][/b]\n\n"
                 f"Hidden data found in:\n{filename}",
            markup=True, halign='center'
        ))
        close_btn = Button(text="Dismiss", size_hint_y=None, height=40)
        content.add_widget(close_btn)
        popup = Popup(title="Security Warning", content=content, size_hint=(0.8, 0.4))
        close_btn.bind(on_release=popup.dismiss)
        popup.open()

if __name__ == '__main__':
    StegoApp().run()
