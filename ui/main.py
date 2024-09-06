from pathlib import Path
from functools import partial

import customtkinter as ctk

from lib.data_classes import CommonFile
from ui.log_frame import CustomLogFrame
from ui.metadata_frame import TaskMetadataFrame
from ui.side_bar import SideBar

from lib.extract import Extract, ExtractFolder
from lib.dvp_struct import DVPLFooterStruct


def target_folder_unpack(frame: 'MasterFrame', extract_data: Extract) -> None:
    folder = ctk.filedialog.askdirectory()

    if folder == '':
        return

    extract_data.set_target_path(folder)
    
    frame.side_bar.target_unpack_label.configure(
        text=f"Unpack to...\n{extract_data.extract_path}"
    )
    
def target_folder_unpack_dvpd(frame: 'MasterFrame', extract_data: Extract) -> None:
    folder = ctk.filedialog.askdirectory()

    if folder == '':
        return

    extract_data.set_target_path(folder)
    
    frame.side_bar.target_unpack_label.configure(
        text=f"Unpack to...\n{extract_data.extract_path.joinpath(extract_data.dvpd_path)}"
    )

def alt_target_unpack_folder(frame: 'MasterFrame', extract_data_folder: ExtractFolder) -> None:
    folder = ctk.filedialog.askdirectory()

    if folder == '':
        return

    extract_data_folder.extract_path = Path(folder)
    frame.side_bar.target_unpack_label.configure(text=f"Unpack / Pack to...\n{folder}")
    
    extract_data_folder.extract_path

def extract_file(frame: 'MasterFrame') -> None:
    file_select = ctk.filedialog.askopenfilename()

    if file_select == '':
        frame.side_bar.set_state_default()
        frame.log_frame.set_state_default()
        frame.metadata_frame.set_metadata('')
        frame.log_frame.add_log("No file selected")
        return

    extract_data = Extract(file_select)
    
    extract_data.keep_originals = frame.side_bar.keep_orig_state
    extract_data.skip_if_exists = frame.side_bar.skip_if_exist_state
    extract_data.compression_type = frame.side_bar.compression_state
    extract_data.fast_mode = frame.side_bar.fast_mode_state
    
    frame.log_frame.add_log(f'Reading file: {Path(file_select)}')
    target_folder_unpack_callback = partial(target_folder_unpack, frame, extract_data)

    if isinstance(extract_data.data, DVPLFooterStruct):
        extract_DVPL = partial(extract_data.extract_DVPL, frame)
        frame.side_bar.set_state_unpack_DVPL(
            target_path=file_select,
            target_unpack_path=str(extract_data.extract_path),
            target_path_unpack_command=target_folder_unpack_callback,
            unpack_command=extract_DVPL
        )
        frame.log_frame.set_state_unpack_DVPL()
        frame.metadata_frame.set_metadata(extract_data.read_file_metadata())
    elif isinstance(extract_data.data, CommonFile):
        frame.side_bar.set_state_pack_DVPL(
            target_path=file_select,
            target_unpack_path=str(extract_data.extract_path),
            target_path_unpack_command=target_folder_unpack_callback,
            unpack_command=partial(extract_data.pack_DVPL, frame)
        )
        frame.log_frame.set_state_pack_DVPL()
        frame.metadata_frame.set_metadata(extract_data.read_file_metadata())

def extract_folder(frame: 'MasterFrame') -> None:
    file_select = ctk.filedialog.askdirectory()
    
    if file_select == '':
        frame.side_bar.set_state_default()
        frame.log_frame.set_state_default()
        frame.metadata_frame.set_metadata('')
        frame.log_frame.add_log("No file selected")
        return
    
    frame.log_frame.add_log(f'Reading folder: {Path(file_select)}')
    
    extract_data_folder = ExtractFolder(file_select)
    extract_data_folder.get_folder_data(master_frame=frame)
    extract_data_folder.keep_originals = frame.side_bar.keep_orig_state
    extract_data_folder.skip_if_exists = frame.side_bar.skip_if_exist_state
    extract_data_folder.fast_mode = frame.side_bar.fast_mode_state
    extract_data_folder.compression_type = frame.side_bar.compression_state
    
    frame.side_bar.target_unpack_label.configure(text=f"Unpack to...\n{extract_data_folder.extract_path}")
    
    frame.side_bar.set_state_folder_selected(
        target_path=file_select,
        pack_command=partial(extract_data_folder.pack_folder, frame),
        unpack_command=partial(extract_data_folder.extract_folder, frame),
        select_unpack_folder_command=partial(alt_target_unpack_folder, frame, extract_data_folder)
    )
    frame.side_bar.lock_controls(False)


class MasterFrame(ctk.CTkFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.columnconfigure(0, weight=20)
        self.columnconfigure(1, weight=100)
        self.columnconfigure(2, weight=100)
        
        self.rowconfigure(0, weight=10)
        
        self.log_frame = CustomLogFrame(self)
        self.metadata_frame = TaskMetadataFrame(self)
        self.side_bar = SideBar(self)
        
        self.side_bar.grid(row=0, column=0, sticky="nsew", padx=5)
        self.side_bar.button_file.configure(command=partial(extract_file, self))
        self.side_bar.button_folder.configure(command=partial(extract_folder, self))
        self.log_frame.grid(row=0, column=1, sticky="nsew")
        self.metadata_frame.grid(row=0, column=2, sticky="nsew", padx=10)
        
    def set_state_default(self):
        self.side_bar.set_state_default()
        self.log_frame.set_state_default()
        self.log_frame.add_log("Ready to start", prefix="[app]: ")
        self.log_frame.set_pb_value(1, 1)
        self.log_frame.set_task('')
        self.log_frame.progress_bar.configure(progress_color="green")
        
    def set_state_on_error(self, exception: Exception):
        self.side_bar.set_state_default()
        self.log_frame.set_state_default()
        self.log_frame.add_log(f"Error occurred: \n{exception}", prefix="[app]: ")
        self.log_frame.set_pb_value(1, 1)
        self.log_frame.set_task('')
        self.log_frame.progress_bar_label.configure(text_color="red", text="Error!")
        self.log_frame.progress_bar.configure(progress_color="red")
        
    def set_state_canceled(self):
        self.log_frame.add_log("Task canceled", prefix="[app]: ")
        self.log_frame.set_pb_value(1, 1)
        self.log_frame.set_task('')
        self.log_frame.progress_bar_label.configure(text_color="orange", text="Canceled!")
        self.log_frame.progress_bar.configure(progress_color="orange")
        self.side_bar.set_state_default()
        
    def set_state_paused(self):
        self.log_frame.progress_bar.configure(progress_color="gray")
        self.log_frame.progress_bar_label.configure(text_color="gray", text="Paused!")
        self.log_frame.set_task('Wait for resume')


class CTkApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # configure window
        self.title("DVPL Extractor | _Zener ver 0.0.5")
        self.geometry(f"{1250}x{650}")
        self.minsize(1200, 600)

        self.main_frame = MasterFrame(self)
        self.main_frame.pack(fill="both", expand=True)
        self.main_frame.side_bar.run_monitoring()
        self.main_frame.log_frame.add_log("Start monitoring", prefix="[app]: ")
        self.main_frame.log_frame.add_log("App started", prefix="[app]: ")


def run_app():
    app = CTkApp()
    app.mainloop()
