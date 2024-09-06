import time
import psutil
from collections.abc import Callable
from threading import Thread

import customtkinter as ctk

from lib.dvp_struct import CompressionTypes

class SideBar(ctk.CTkFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_bg_color = ('gray78', 'gray23')
        self.label = ctk.CTkLabel(self, height=20, text="Control panel")
        self.label.pack(side="top", fill="both")
        self.target_label = ctk.CTkLabel(self, height=30, text="Target:\nNone", wraplength=220, bg_color=self.label_bg_color)
        self.target_unpack_label = ctk.CTkLabel(self, height=30, text="Unpack to...\nNone", wraplength=220, bg_color=self.label_bg_color)
        self.compression_types_label = ctk.CTkLabel(self, height=30, text="Compression types", bg_color=self.label_bg_color)
        self.compression_state = ctk.StringVar(self, value=CompressionTypes.LZ4.name)
        
        self.segmented_button = ctk.CTkSegmentedButton(
            self, 
            values=[x.name for x in CompressionTypes if x != CompressionTypes.RFC1951], 
            state='disabled',
            variable=self.compression_state
        )
        self.control_btn_frame = ctk.CTkFrame(self)
        
        self.control_check_frame = ctk.CTkFrame(self)
        
        self.keep_orig_state = ctk.BooleanVar(value=True)
        self.skip_if_exist_state = ctk.BooleanVar(value=False)
        self.fast_mode_state = ctk.BooleanVar(value=False)
        
        self.keep_orig_check = ctk.CTkCheckBox(self.control_check_frame, text="Keep original files", onvalue=True, offvalue=False, variable=self.keep_orig_state)
        self.skip_if_exist_check = ctk.CTkCheckBox(self.control_check_frame, text="Skip if file exists", onvalue=1, offvalue=0, variable=self.skip_if_exist_state)
        self.fast_mode_check = ctk.CTkCheckBox(self.control_check_frame, text="Fast mode", onvalue=1, offvalue=0, variable=self.fast_mode_state)
        
        self.keep_orig_check.pack(side="left", expand=True, pady=5)
        self.skip_if_exist_check.pack(side="left", expand=True, pady=5)
        self.fast_mode_check.pack(side="left", expand=True, pady=5)

        self.pack_btn = ctk.CTkButton(self.control_btn_frame, text="PACK", state='disabled')
        self.unpack_btn = ctk.CTkButton(self.control_btn_frame, text="UNPACK", state='disabled', fg_color='green', hover_color='#007300')
        
        self.process_control_frame = ctk.CTkFrame(self)
        self.pause_btn = ctk.CTkButton(self.process_control_frame, text="PAUSE", state='disabled')
        self.resume_btn = ctk.CTkButton(self.process_control_frame, text="RESUME", state='disabled', fg_color='green', hover_color='#007300')
        self.cancel_btn = ctk.CTkButton(self.process_control_frame, text="CANCEL", state='disabled', fg_color='#C21717', hover_color='#FF2E1F')
        
        self.performance_frame = ctk.CTkFrame(self)
        self.cpu_load_label = ctk.CTkLabel(self.performance_frame, text="CPU load", font=("Cascadia Code", 14))
        self.cpu_load_bar = ctk.CTkProgressBar(self.performance_frame, orientation="horizontal", width=20)
        self.ram_load_label = ctk.CTkLabel(self.performance_frame, text="RAM used", font=("Cascadia Code", 14))
        self.ram_load_bar = ctk.CTkProgressBar(self.performance_frame, orientation="horizontal", width=20)
        self.read_write_speed_label = ctk.CTkLabel(self.performance_frame, text="Read/Write Speed", font=("Cascadia Code", 14))
        
        self.cpu_load_label.pack(side="top", fill="both")
        self.cpu_load_bar.pack(side="top", fill="both", expand=True, padx=5, pady=5)
        self.ram_load_label.pack(side="top", fill="both")
        self.ram_load_bar.pack(side="top", fill="both", expand=True, padx=5, pady=5)
        self.read_write_speed_label.pack(side="top", fill="both", expand=True, padx=5, pady=5)
        
        self.control_check_frame.pack(side="top", fill="both")
        self.pause_btn.pack(side="left", padx=5, pady=5, expand=True, fill='both')
        self.resume_btn.pack(side="left", padx=5, pady=5, expand=True, fill='both')
        self.cancel_btn.pack(side="left", padx=5, pady=5, expand=True, fill='both')
        
        self.folder_buttons_frame = ctk.CTkFrame(self)
        self.unpack_btn.pack(side="left", padx=5, pady=5, expand=True, fill='both')
        self.pack_btn.pack(side="right", padx=5, pady=5, expand=True, fill='both')
        
        self.process_control_frame.pack(side="bottom", fill="both")
        self.control_btn_frame.pack(side="bottom", fill="both")
        
        self.button_file = ctk.CTkButton(
            self, 
            text="Choose file", 
            width=80, 
            height=45
        )
        self.button_file.pack(side="top", fill="both")
        
        self.button_folder = ctk.CTkButton(
            self, 
            text="Choose folder", 
            width=80, 
            height=45,
        )
        self.button_folder.pack(side="top", fill="both", pady=10)
        
        self.target_label.pack(side="top", fill="both", pady=5)
        self.target_folder_unpack = ctk.CTkButton(
            self, 
            text="Wait for command ...", 
            width=80, 
            height=45,
            state='disabled'
        )
        
        self.target_folder_unpack.pack(side="top", fill="both")
        self.target_unpack_label.pack(side="top", fill="both", pady=5)
        self.compression_types_label.pack(side="top", fill="both", pady=5)
        self.segmented_button.pack(side="top", fill="both", pady=5)
        self.performance_frame.pack(side="bottom", fill="both")
        self.control_check_frame.pack(after=self.control_btn_frame, fill="both", side="bottom")
        
    def disable_process_controls(self):
        self.pause_btn.configure(state='disabled')
        self.resume_btn.configure(state='disabled')
        self.cancel_btn.configure(state='disabled')

    def enable_process_controls(self, command_pause: Callable[..., None], command_resume: Callable[..., None], command_cancel: Callable[..., None]):
        self.pause_btn.configure(state='normal', command=command_pause)
        self.resume_btn.configure(state='disabled', command=command_resume)
        self.cancel_btn.configure(state='normal', command=command_cancel)
        
    def process_state_paused(self):
        self.pause_btn.configure(state='disabled')
        self.resume_btn.configure(state='normal')
        self.cancel_btn.configure(state='disabled')
        
    def process_state_resumed(self):
        self.pause_btn.configure(state='normal')
        self.resume_btn.configure(state='disabled')
        self.cancel_btn.configure(state='normal')
        
    def set_state_default(self):
        self.segmented_button.configure(state='disabled')
        self.target_folder_unpack.configure(state='disabled', command=None)
        self.button_file.configure(state='normal')
        self.button_folder.configure(state='normal')
        self.pack_btn.configure(state='disabled', command=None)
        self.unpack_btn.configure(state='disabled', command=None)
        self.target_label.configure(text="Target:\nNone")
        self.target_unpack_label.configure(text="Pack / Unpack to...\nNone")
        self.segmented_button.set(CompressionTypes.LZ4.name)
        self.disable_process_controls()

    def set_state_unpack_DVPL(
            self, 
            target_path: str,
            target_unpack_path: str,
            target_path_unpack_command: Callable[..., None],
            unpack_command: Callable[..., None]
        ) -> None:
        self.target_label.configure(text=f"Target:\n{target_path}")
        self.target_unpack_label.configure(text=f"Pack / Unpack to...\n{target_unpack_path}")
        self.target_folder_unpack.configure(state='normal')
        self.target_folder_unpack.configure(command=target_path_unpack_command, text='Select pack / unpack folder')
        self.pack_btn.configure(state='disabled')
        self.unpack_btn.configure(command=unpack_command, state='normal')
        self.disable_process_controls()

    def set_state_unpack_DVPD(
            self,
            target_path: str,
            target_unpack_path: str,
            target_path_unpack_command: Callable[..., None],
            unpack_command: Callable[..., None],
        ) -> None:
        self.target_label.configure(text=f"Target:\n{target_path}")
        self.target_unpack_label.configure(text=f"Unpack to...\n{target_unpack_path}")
        self.target_folder_unpack.configure(state='normal', text='Select unpack folder')
        self.target_folder_unpack.configure(command=target_path_unpack_command)
        self.pack_btn.configure(state='disabled')
        self.unpack_btn.configure(state='normal', command=unpack_command)
        
    def set_state_pack_DVPL(
            self,
            target_path: str,
            target_unpack_path: str,
            target_path_unpack_command: Callable[..., None],
            unpack_command: Callable[..., None],
        ) -> None:
        self.target_label.configure(text=f"Target:\n{target_path}")
        self.target_unpack_label.configure(text=f"Unpack to...\n{target_unpack_path}")
        self.target_folder_unpack.configure(state='normal', text='Select pack folder')
        self.target_folder_unpack.configure(command=target_path_unpack_command)
        self.segmented_button.configure(state='normal')
        self.unpack_btn.configure(state='disabled')
        self.pack_btn.configure(command=unpack_command, state='normal')
        
    def set_state_folder_selected(
            self, 
            target_path: str, 
            pack_command: Callable[..., None],
            select_unpack_folder_command: Callable[..., None],
            unpack_command: Callable[..., None],
        ) -> None:
        self.target_folder_unpack.configure(state='normal', text='Select pack / unpack folder', command=select_unpack_folder_command)
        self.target_label.configure(text=f"Target:\n{target_path}")
        self.target_unpack_label.configure(text=f"Pack / Unpack to...\n{target_path}")
        self.segmented_button.configure(state='normal')
        self.pack_btn.configure(state='normal', command=pack_command)
        self.unpack_btn.configure(state='normal', command=unpack_command)

    def set_state_none_DVPD(self):
        self.target_folder_unpack.configure(state='disabled')
        self.pack_btn.configure(state='disabled')
        
    def lock_controls(self, lock_target_folder_unpack: bool = True):
        if lock_target_folder_unpack:
            self.target_folder_unpack.configure(state='disabled')
        self.button_file.configure(state='disabled')
        self.button_folder.configure(state='disabled')
        self.pack_btn.configure(state='disabled')
        self.unpack_btn.configure(state='disabled')
        self.segmented_button.configure(state='disabled')

    def unlock_controls(self, unlock_target_folder_unpack: bool = True):
        if unlock_target_folder_unpack:
            self.target_folder_unpack.configure(state='normal')
            
        self.button_file.configure(state='normal')
        self.button_folder.configure(state='normal')
        self.pack_btn.configure(state='normal')
        self.unpack_btn.configure(state='normal')
        self.segmented_button.configure(state='normal')

    def run_monitoring(self):
        Thread(target=self._monitoring, daemon=True, name="MonitoringThread").start()
        
    def _monitoring(self):
        process = psutil.Process()
        while True:
            proc_cpu_usage = process.cpu_percent()
            ram_usage, ram_free = psutil.virtual_memory().used, psutil.virtual_memory().free
            io_counters = process.io_counters()
            
            self.ram_load_bar.set(ram_usage / (ram_usage + ram_free))
            self.cpu_load_bar.set(proc_cpu_usage / 100)
            
            self.cpu_load_label.configure(text=f'CPU Load (process): {proc_cpu_usage}%')
            self.ram_load_label.configure(
                text=f'RAM Load: used {round(ram_usage / 1024 / 1024)} MB / free {round(ram_free / 1024 / 1024)} MB ({round(process.memory_info().rss / 1024 / 1024)} MB)'
            )
            
            time.sleep(1)
            io_counters_next = process.io_counters()
            
            current_write_speed = io_counters_next.write_bytes - io_counters.write_bytes
            current_read_speed = io_counters_next.read_bytes - io_counters.read_bytes
            
            self.read_write_speed_label.configure(
                text=f'IO Speed | Read: {round(current_read_speed / 1024 / 1024)} MB / Write: {round(current_write_speed / 1024 / 1024)} MB'
            )
