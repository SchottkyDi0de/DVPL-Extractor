from dataclasses import dataclass
from pathlib import Path


@dataclass
class FileInfo:
    full_path: str
    name: str
    extension: str
    size: int
    
    def __str__(self):
        data = \
            f'Common File Info:\n' \
            f"-|  Name: {self.name}\n"\
            f"-|  Extension: {self.extension}\n"\
            f"-|  Size: {self.size} bytes\n"\
            f"-|  Full path: {self.full_path}\n"
            
        return data

class CommonFile:
    def __init__(self, path: Path):
        self.full_path = str(path.absolute())
        self.name = path.name
        self.extension = path.suffix
        self.size = path.stat().st_size
        self.path = path


@dataclass
class FolderMeta:
    path: Path
    files_count: int
    dvpl_count: int
    folders_count: int
    
    def __str__(self):
        data = \
            f'DVPL Folder Info:\n' \
            f"-|  Path: {self.path}\n"\
            f"-|  Files count: {self.files_count}\n"\
            f"-|  DVPL count: {self.dvpl_count}\n"\
            f"-|  Folders count: {self.folders_count}\n"
            
        return data
