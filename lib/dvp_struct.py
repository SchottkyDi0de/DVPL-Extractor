from dataclasses import dataclass
from io import BufferedIOBase
from enum import Enum
from pathlib import Path
from struct import pack

from lib.data_classes import FolderMeta


class CompressionTypes(Enum):
    NONE = 0
    LZ4 = 1
    LZ4_HC = 2
    RFC1951 = 3


@dataclass
class DVPLFooter:
    input_file_size: int
    '''
    ### input file size (in bytes)
    '''
    compressed_block_size: int
    '''
    ### compressed block size (in bytes)
    '''
    compressed_block_crc32: int
    '''
    ### CRC32 of compressed block
    '''
    compression_type: CompressionTypes
    '''
    ### Compression type, see CompressionTypes
    '''
    footer_label: str
    '''
    ### magic string encoded in UTF-8
    '''


class Folder:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.glob_files = self.path.glob("**/*")
        
        dvpl_paths: list[Path] = []
        file_paths: list[Path] = []
        folder_paths: list[Path] = []
        
        for i in self.glob_files:
            file_path = Path(i)
            
            if not file_path.is_file():
                folder_paths.append(file_path)
                continue
            
            if file_path.suffix == ".dvpl":
                dvpl_paths.append(file_path)
            else:
                file_paths.append(file_path)
        
        self.dvpl_file_list = dvpl_paths
        self.file_list = file_paths
        self.folder_paths = folder_paths
        
        self.files_count = len(self.file_list)
        self.dvpl_count = len(self.dvpl_file_list)
        self.folders_count = len(self.folder_paths)
        
        self.folder_meta = FolderMeta(self.path, self.files_count, self.dvpl_count, self.folders_count)

    
class DVPLFooterStruct:
    def __init__(self, file: BufferedIOBase) -> None:
        self.data = file.read()
        footer = self.data[-20:]
        
        if len(footer) != 20:
            raise ValueError('Invalid last bytes length')
        
        self.last_bytes = footer
        self.footer_data = self._get_footer_metadata()
        file.close()
        '''
        ### 20 last bytes of DVPL file
        '''

    def __str__(self) -> str:
        data = \
            f'DVPL Footer metadata:\n'\
            f'-|  Input file size: {self.footer_data.input_file_size} bytes\n'\
            f'-|  Compressed block size: {self.footer_data.compressed_block_size} bytes\n'\
            f'-|  Compressed block crc32: {hex(self.footer_data.compressed_block_crc32).replace("0x", "")}\n'\
            f'-|  Compression type: {self.footer_data.compression_type.name}\n'\
            f'-|  Footer label: {self.footer_data.footer_label}\n'\
            f'-|  Compression: {round(abs((self.footer_data.compressed_block_size / self.footer_data.input_file_size * 100) - 100), 2)}%\n'
        
        return data

    def _get_footer_metadata(self) -> DVPLFooter:
        input_file_size = int.from_bytes(self.last_bytes[0:4], 'little')
        compressed_block_size = int.from_bytes(self.last_bytes[4:8], 'little')
        compressed_block_crc32 = int.from_bytes(self.last_bytes[8:12], 'little')
        compression_type = CompressionTypes(int.from_bytes(self.last_bytes[12:16], 'little'))
        file_descriptor = self.last_bytes[16:20].decode('utf-8')

        return DVPLFooter(
            input_file_size=input_file_size,
            compressed_block_size=compressed_block_size,
            compressed_block_crc32=compressed_block_crc32,
            compression_type=compression_type,
            footer_label=file_descriptor
        )
    
    @staticmethod
    def generate_footer(input_file_size: int, compressed_block_size: int, compressed_block_crc32: int, compression_type: int, footer_label: str = 'DVPL') -> bytes:
        """
        Generate the footer for a DVPL file.

        Args:
            input_file_size (int): The size of the input file in bytes.
            compressed_block_size (int): The size of the compressed block in bytes.
            compressed_block_crc32 (int): The CRC32 checksum of the compressed block.
            compression_type (CompressionTypes): The type of compression used.
            footer_label (str, optional): The label for the footer. Defaults to 'DVPL'.

        Returns:
            bytes: The generated footer as a byte array. 20 bytes long.
        """
        bytes = bytearray()
        bytes += pack('<I', input_file_size)
        bytes += pack('<I', compressed_block_size)
        bytes += pack('<I', compressed_block_crc32)
        bytes += pack('<I', compression_type)
        bytes += footer_label.encode('utf-8')
        
        return bytes
        
    def get_footer_data(self) -> DVPLFooter:
        return self.footer_data
