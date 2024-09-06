import time
from threading import Thread
from pathlib import Path
from typing import Literal, Optional, TYPE_CHECKING
from zlib import crc32
import traceback

import lz4.block

from lib.data_classes import CommonFile, FileInfo, FolderMeta
from lib.dvp_struct import DVPLFooterStruct, CompressionTypes, Folder
from lib.exceptions import wrap_exceptions

if TYPE_CHECKING:
    from customtkinter import BooleanVar, StringVar
    
    from ui.log_frame import CustomLogFrame
    from ui.main import MasterFrame

class ExtractFolder:
    def __init__(self, path: str) -> None:
        self.path = Path(path)
        
        if not self.path.exists():
            raise ValueError(f"Folder not found: {self.path}")
        
        if not self.path.is_dir():
            raise ValueError(f"Path is not a folder: {self.path}")
        
        self.extract_path = Path(path)

        self.keep_originals: Optional['BooleanVar'] = None
        self.skip_if_exists: Optional['BooleanVar'] = None
        self.fast_mode: Optional['BooleanVar'] = None
        self.compression_type: Optional['StringVar'] = None
        
        self.folder_data: Optional[Folder] = None
        self.folder_meta: Optional[FolderMeta] = None
        
        self.PAUSE_FLAG = False
        self.CANCEL_FLAG = False
        
    def set_pause(self) -> None:
        self.PAUSE_FLAG = True
        
    def set_cancel(self) -> None:
        self.CANCEL_FLAG = True
        
    def reset_pause(self) -> None:
        self.PAUSE_FLAG = False
    
    def get_folder_data(self, master_frame: 'MasterFrame') -> None:
        log_frame = master_frame.log_frame
        
        log_frame.add_log('Start thread to get folder metadata', prefix="[threading]: ")
        thread = Thread(target=self._get_folder_metadata, args=(master_frame, ), daemon=True)
        log_frame.add_log('Get folder metadata', prefix="[extract]: ")
        thread.start()
    
    def _get_folder_metadata(self, master_frame: 'MasterFrame') -> None:
        meta_frame = master_frame.metadata_frame
        self.folder_data = Folder(self.path)
        self.folder_meta = self.folder_data.folder_meta
        meta_frame.set_metadata(str(self.folder_meta))
        master_frame.side_bar.unlock_controls(False)

    def extract_folder(self, master_frame: 'MasterFrame') -> None:
        log_frame = master_frame.log_frame
        log_frame.add_log('Start thread to extract folder', prefix="[threading]: ")
        log_frame.set_task('Start threads to extract folder')
        master_frame.side_bar.enable_process_controls(
            command_pause=self.set_pause,
            command_cancel=self.set_cancel,
            command_resume=self.reset_pause
        )
        Thread(target=self._extract_folder, args=(master_frame, ), daemon=True, name="MainExtractorThread").start()
    
    @wrap_exceptions(
        frame_pos=1, 
        ignore_exceptions=(
            PermissionError,
            FileNotFoundError
        )
    )
    def _extract_folder(self, master_frame: 'MasterFrame') -> None:
        log_frame = master_frame.log_frame
        master_frame.side_bar.enable_process_controls(
            command_pause=self.set_pause,
            command_cancel=self.set_cancel,
            command_resume=self.reset_pause
        )
        
        if self.folder_data is None:
            log_frame.add_log('Folder data not found', prefix="[extract]: ")
            return
        
        master_frame.side_bar.lock_controls()
        log_frame.add_log('Extract folder...', prefix="[extract]: ")
        log_frame.set_task('Extracting files...')
        log_frame.set_pb_value(0, len(self.folder_data.dvpl_file_list))
        files = len(self.folder_data.dvpl_file_list)
        
        if self.skip_if_exists is None:
            raise ValueError("skip_if_exists is None")
        
        if self.fast_mode is None:
            raise ValueError("fast_mode is None")
        
        for counter, file in enumerate(self.folder_data.dvpl_file_list):
            if self.CANCEL_FLAG:
                master_frame.set_state_canceled()
                return
            
            if self.PAUSE_FLAG:
                master_frame.set_state_paused()
                master_frame.side_bar.process_state_paused()
                while self.PAUSE_FLAG:
                    time.sleep(0.1)
                else:
                    master_frame.side_bar.process_state_resumed()
            
            orig_file_name = file.name.removesuffix(file.suffix)
            
            if file.parent.joinpath(orig_file_name).exists() and self.skip_if_exists.get():
                if self.fast_mode.get():
                    continue
                
                log_frame.add_log(f'File already exists: {file.parent.joinpath(orig_file_name)}', prefix="[extract]: ")
                log_frame.set_pb_value(counter, files - 1)
                continue
            
            target_path = self.extract_path.joinpath(file.parent.relative_to(self.path))
            
            if not target_path.exists():
                target_path.mkdir(parents=True, exist_ok=True)
            
            if not self.fast_mode.get():
                log_frame.set_task(f'Extracting file... {counter}')

            if file.stat().st_size < 20:
                if self.fast_mode.get():
                    continue
                
                log_frame.add_log('File too small, skipping', prefix="[extract]: ")
                continue

            with open(file, "rb") as dvpl_file:
                data = DVPLFooterStruct(dvpl_file)
            
            with open(target_path.joinpath(orig_file_name), "wb") as new_file:
                if data.footer_data.compression_type is CompressionTypes.NONE:
                    new_file.write(data.data[:-20])
                
                else:
                    new_file.write(lz4.block.decompress(data.data[:-20], data.footer_data.input_file_size))
            
            if not self.fast_mode.get():
                log_frame.add_log('File uncompressed!', prefix="[extract]: ")

                log_frame.add_log(f'file {file} uncompressed, new file - {file.parent.joinpath(orig_file_name)}', prefix="[extract]: ")
                log_frame.set_pb_value(counter, files - 1)

            elif counter % 100 == 0:
                log_frame.add_log(f'Extracted {counter} files', prefix="[extract]: ")
                log_frame.set_task(f'Extracting files... {counter}')
                log_frame.set_pb_value(counter, files - 1)

        log_frame.set_task('')
        log_frame.set_pb_value(1, 1)
        log_frame.progress_bar.configure(progress_color="yellow")
        log_frame.progress_bar_label.configure(text_color="yellow", text="cleaning up...")
        self.clean_up(log_frame)
        master_frame.set_state_default()
    
    def clean_up(self, log_frame: 'CustomLogFrame', mode: Literal['dvpl', 'files'] = 'dvpl') -> None:
        if self.folder_data is None:
            log_frame.add_log('Folder data not found', prefix="[extract]: ")
            return
        
        if self.keep_originals is None:
            raise ValueError("keep_originals is None")
        
        log_frame.add_log('Clean up...', prefix="[extract]: ")
        for file in self.folder_data.dvpl_file_list if mode == 'dvpl' else self.folder_data.file_list:
            if not self.keep_originals.get():
                try:
                    file.unlink()
                except Exception:
                    log_frame.add_log(traceback.format_exc(), prefix="[stderr]: ")
            
        log_frame.add_log('Clean up completed', prefix="[extract]: ")
        log_frame.set_pb_value(1, 1)
        log_frame.add_log('Folder extracted / packed, all done!', prefix="[extract]: ")
    
    def pack_folder(self, master_frame: 'MasterFrame') -> None:
        log_frame = master_frame.log_frame
        log_frame.add_log('Start thread to pack folder', prefix="[threading]: ")
        log_frame.set_task('Start threads to pack folder')
        master_frame.side_bar.enable_process_controls(
            command_pause=self.set_pause,
            command_cancel=self.set_cancel,
            command_resume=self.reset_pause
        )
        Thread(target=self._pack_folder, args=(master_frame, ), daemon=True, name="MainExtractorThread").start()
    
    @wrap_exceptions(
        frame_pos=1, 
        ignore_exceptions=(
            PermissionError,
            FileNotFoundError
        )
    )
    def _pack_folder(self, master_frame: 'MasterFrame') -> None:
        log_frame = master_frame.log_frame
        
        if self.folder_data is None:
            log_frame.add_log('Folder data not found', prefix="[extract]: ")
            return
        
        if self.keep_originals is None:
            raise ValueError("keep_originals is None")
        
        if self.skip_if_exists is None:
            raise ValueError("skip_if_exists is None")
        
        if self.fast_mode is None:
            raise ValueError("fast_mode is None")
        
        if self.compression_type is None:
            raise ValueError("compression_type is None")
        
        for counter, file in enumerate(self.folder_data.file_list):
            if self.CANCEL_FLAG:
                master_frame.set_state_canceled()
                return
            
            if self.PAUSE_FLAG:
                master_frame.set_state_paused()
                master_frame.side_bar.process_state_paused()
                while self.PAUSE_FLAG:
                    time.sleep(0.1)
                else:
                    master_frame.side_bar.process_state_resumed()
            
            if file.is_dir():
                continue
            
            target_path = self.extract_path.joinpath(file.parent.relative_to(self.path))
            if not target_path.exists():
                target_path.mkdir(parents=True)
            
            with open(file, "rb") as pack_file:
                if CompressionTypes[self.compression_type.get()] is CompressionTypes.NONE:
                    compressed_data = pack_file.read()
                else:
                    compressed_data: bytes = lz4.block.compress(
                        pack_file.read(), 
                        store_size=False, 
                        mode='high_compression' if self.compression_type.get() == 'LZ4_HC' else 'default'
                    )
                input_file_size = file.stat().st_size
                compressed_data_size = len(compressed_data)
                compressed_data_crc32 = crc32(compressed_data)
                compression_type = CompressionTypes[self.compression_type.get()].value
                
                footer = DVPLFooterStruct.generate_footer(
                    input_file_size, compressed_data_size, compressed_data_crc32, compression_type
                )
                dvpl_data = compressed_data + footer

            with open(target_path.joinpath(file.name+'.dvpl'), "wb") as new_file:
                new_file.write(dvpl_data)

            if not self.fast_mode.get():
                log_frame.add_log('File compressed!', prefix="[compress]: ")

                log_frame.add_log(f'file {file} compressed, new file - {file.parent.joinpath(file.name+".dvpl")}', prefix="[compress]: ")
                log_frame.set_pb_value(counter, len(self.folder_data.file_list) - 1)

            elif counter % 100 == 0:
                log_frame.add_log(f'Packed {counter} files', prefix="[compress]: ")
                log_frame.set_task(f'Packing files... {counter}')
                log_frame.set_pb_value(counter, len(self.folder_data.file_list) - 1)
                
        log_frame.set_task('')
        log_frame.set_pb_value(1, 1)
        log_frame.progress_bar.configure(progress_color="yellow")
        log_frame.progress_bar_label.configure(text_color="yellow", text="cleaning up...")
        self.clean_up(log_frame, mode='files')
        master_frame.set_state_default()


class Extract:
    def __init__(self, path: str) -> None:
        self.path = Path(path)
        self.data_type = self.path.suffix
        self.dvpd_path = self.path.name.removesuffix('.dvpm')

        if not self.path.exists():
            raise FileNotFoundError(f"File not found: {self.path}")

        with open(self.path, "rb") as file:

            if self.path.suffix.lower() == ".dvpl":
                self.data = DVPLFooterStruct(file)

            else:
                self.data = CommonFile(self.path)
                
        self.extract_path = self.path.parent
        self.orig_file_name = self.path.name.removesuffix(self.path.suffix)
        self.compression_type: Optional['StringVar'] = None
        self.skip_if_exists: Optional['BooleanVar'] = None
        self.keep_originals: Optional['BooleanVar'] = None
        self.fast_mode: Optional['BooleanVar'] = None
        
        self.PAUSE_FLAG = False
        self.CANCEL_FLAG = False
        
    def set_target_path(self, path: str) -> None:
        self.extract_path = Path(path)
        self.dvpd_path = self.path.name.removesuffix('.dvpm')
        
    def set_pause(self) -> None:
        self.PAUSE_FLAG = True
        
    def set_cancel(self) -> None:
        self.CANCEL_FLAG = True
        
    def reset_pause(self) -> None:
        self.PAUSE_FLAG = False

    def read_file_metadata(self) -> str:
        data = ''

        file_info = FileInfo(
            full_path=str(self.path.absolute()),
            name=self.path.name,
            extension=self.path.suffix,
            size=self.path.stat().st_size
        )
        
        data += str(file_info) + '\n'
        
        if isinstance(self.data, DVPLFooterStruct):
            data += str(self.data)

        return data
    
    def extract_DVPL(self, frame: 'MasterFrame') -> None:
        log_frame = frame.log_frame
        log_frame.add_log('Create thread to unpack file', prefix="[threading]: ")
        log_frame.set_task('Create thread to unpack file')
        Thread(target=self._extract_file, args=(frame, ), daemon=True).start()
    
    @wrap_exceptions(
    frame_pos=1, 
    ignore_exceptions=(
        PermissionError,
        FileNotFoundError
        )
    )
    def _extract_file(self, master_frame: 'MasterFrame') -> None:
        log_frame = master_frame.log_frame
        log_frame.set_pb_value(0, 1)
        prefix = "[unpacker]: "
        
        if self.keep_originals is None:
            raise ValueError("keep_originals is None")
        
        if self.skip_if_exists is None:
            raise ValueError("skip_if_exists is None")
        
        if self.compression_type is None:
            raise ValueError("compression_type is None")
        
        if not isinstance(self.data, DVPLFooterStruct): 
            raise ValueError("Not a DVPL file")
        
        if self.skip_if_exists.get() and self.check_dvpd_exists():
            log_frame.add_log(f'File already exists: {self.path.with_name(self.orig_file_name)}', prefix=prefix)
            log_frame.set_pb_value(1, 1)
            return
        
        if not isinstance(self.data, DVPLFooterStruct):
            log_frame.add_log('Not a DVPL file', prefix=prefix)
            raise ValueError("Not a DVPL file")
        
        log_frame.set_task('Unpacking file...')
        log_frame.add_log(f'Unpacking file in target path: {self.extract_path}', prefix=prefix)
        
        if self.extract_path.joinpath(self.orig_file_name).exists():
            mode = 'r+b'
        else:
            mode = 'wb'
        
        with open(self.extract_path.joinpath(self.orig_file_name), mode) as new_file:
            log_frame.add_log(f'Open file descriptor: {self.extract_path}\\{self.orig_file_name}', prefix=prefix)
            log_frame.add_log('Checking file compression type...', prefix=prefix)
            
            if self.data.footer_data.compression_type is CompressionTypes.NONE:
                new_file.write(self.data.data[:-20])
                
            else:
                new_file.write(lz4.block.decompress(self.data.data[:-20], self.data.footer_data.input_file_size))
                log_frame.add_log('File uncompressed!', prefix=prefix)
        
        log_frame.add_log('Clean up...', prefix=prefix)
        log_frame.set_task('Clean up...')
        log_frame.set_pb_value(1, 1)
        log_frame.progress_bar.configure(progress_color="yellow")
        self.clean_up(log_frame)
        log_frame.add_log(f'Unpacked_file: {self.extract_path}\\{self.orig_file_name}', prefix=prefix)
        master_frame.set_state_default()
    
    def pack_DVPL(self, frame: 'MasterFrame') -> None:
        log_frame = frame.log_frame
        log_frame.add_log('Create thread to pack file', prefix="[threading]: ")
        log_frame.set_task('Create thread to pack file')
        Thread(target=self._pack_file, args=(frame, ), daemon=True).start()
    
    @wrap_exceptions(
        frame_pos=1, 
        ignore_exceptions=(
            PermissionError,
            FileNotFoundError
        )
    )
    def _pack_file(self, master_frame: 'MasterFrame') -> None:
        log_frame = master_frame.log_frame
        log_frame.set_pb_value(0, 1)
        prefix = "[packer]: "

        if not isinstance(self.data, CommonFile):
            log_frame.add_log('Not a DVPL file', prefix=prefix)
            raise ValueError("Not a valid file")

        if self.skip_if_exists is None:
            raise ValueError("skip_if_exists is None")

        if self.keep_originals is None:
            raise ValueError("keep_originals is None")

        if self.skip_if_exists.get() and self.path.parent.joinpath(self.path.name + ".dvpl").exists():
            log_frame.add_log(f'File already exists: {self.path.parent.joinpath(self.path.name + ".dvpl")}', prefix=prefix)
            log_frame.set_task('')
            log_frame.set_pb_value(1, 1)
            return

        log_frame.set_task('Packing file...')
        log_frame.add_log(f'Packing file in target path: {self.extract_path}', prefix=prefix)

        with open(self.path, "rb") as pack_file:
            log_frame.add_log(f'Open file descriptor: {self.extract_path}', prefix=prefix)
            if self.compression_type is None:
                raise ValueError("compression_type is None")

            if CompressionTypes[self.compression_type.get()] is CompressionTypes.NONE:
                compressed_data = pack_file.read()
            else:
                compressed_data = lz4.block.compress(
                    pack_file.read(),
                    store_size=False, 
                    mode='high_compression' if CompressionTypes[self.compression_type.get()].name == 'LZ4_HC' else 'default'
                )

            input_file_size = self.path.stat().st_size
            compressed_data_size = len(compressed_data)
            compressed_data_crc32 = crc32(compressed_data)
            compression_type = CompressionTypes[self.compression_type.get()].value
            
            dvpl_footer = DVPLFooterStruct.generate_footer(
                input_file_size=input_file_size,
                compressed_block_size=compressed_data_size,
                compressed_block_crc32=compressed_data_crc32,
                compression_type=compression_type
            )

        dvpl_data = compressed_data + dvpl_footer

        open_mode = 'wb' if not self.path.parent.joinpath(self.path.name + ".dvpl").exists() else 'r+b'

        with open(self.path.parent.joinpath(self.path.name + ".dvpl"), open_mode) as new_file:
            new_file.write(dvpl_data)

        log_frame.add_log('Clean up...', prefix=prefix)
        log_frame.set_task('Clean up...')
        log_frame.set_pb_value(1, 1)
        log_frame.progress_bar.configure(progress_color="yellow")
        self.clean_up(log_frame)
        log_frame.add_log(f'Packed file: {self.path.parent.joinpath(self.path.name + ".dvpl")}', prefix=prefix)
        master_frame.set_state_default()

    def clean_up(self, log_frame: 'CustomLogFrame') -> None:
        time.sleep(1)
        if self.keep_originals is None:
            raise ValueError("keep_originals is None")

        if self.keep_originals.get() is False:
            self.path.unlink()

        log_frame.set_task('')
        log_frame.set_pb_value(1, 1)
