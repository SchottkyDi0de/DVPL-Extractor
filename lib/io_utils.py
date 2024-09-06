from struct import unpack
from io import BufferedIOBase, BufferedReader, BytesIO
from typing import Literal


class IO:
    '''
    ### Class for reading binary data.
    '''
    @staticmethod
    def get_buffer(file_like: BufferedReader) -> BytesIO:
        with file_like as buffer:
            return BytesIO(buffer.read())
    
    @staticmethod
    def buffer_from_bytes(data: bytes) -> BytesIO:
        return BytesIO(data)

    @staticmethod
    def int8(buffer: BufferedIOBase, byte_order: Literal['little', 'big'] = 'little', signed: bool = True) -> int:
        '''
        ### Read 1 byte from the buffer and return it as an integer.
        '''
        return int.from_bytes(buffer.read(1), byte_order, signed=signed)
    
    @staticmethod
    def int16(buffer: BufferedIOBase, byte_order: Literal['little', 'big'] = 'little', signed: bool = True) -> int:
        '''
        ### Read 2 bytes from the buffer and return it as an integer.
        '''
        return int.from_bytes(buffer.read(2), byte_order, signed=signed)
    
    @staticmethod
    def int32(buffer: BufferedIOBase, byte_order: Literal['little', 'big'] = 'little', signed: bool = True) -> int:
        '''
        ### Read 4 bytes from the buffer and return it as an integer.
        '''
        return int.from_bytes(buffer.read(4), byte_order, signed=signed)
    
    @staticmethod
    def int64(buffer: BufferedIOBase, byte_order: Literal['little', 'big'] = 'little', signed: bool = True) -> int:
        '''
        ### Read 8 bytes from the buffer and return it as an integer.
        '''
        return int.from_bytes(buffer.read(8), byte_order, signed=signed)
    
    @staticmethod
    def float32(buffer: BufferedIOBase, byte_order: Literal['little', 'big'] = 'little') -> float:
        '''
        ### Read 4 bytes from the buffer and return it as a float.
        '''
        return unpack('f', buffer.read(8))[0]
    
    @staticmethod
    def float64(buffer: BufferedIOBase, byte_order: Literal['little', 'big'] = 'little') -> float:
        '''
        ### Read 8 bytes from the buffer and return it as a float.
        '''
        return unpack('f', buffer.read(8))[0]
    
    @staticmethod
    def double64(buffer: BufferedIOBase, byte_order: Literal['little', 'big'] = 'little') -> float:
        '''
        ### Read 8 bytes from the buffer and return it as a float (double).
        '''
        return unpack('d', buffer.read(8))[0]

    @staticmethod
    def string(buffer: BufferedIOBase, bytes_length: int, encoding: str = 'utf-8') -> str:
        '''
        ### Read `bytes_length` bytes from the buffer and return it as a string.
        '''
        return buffer.read(bytes_length).decode(encoding)

    @staticmethod
    def bytes(buffer: BufferedIOBase, bytes_length: int) -> bytes:
        '''
        ### Read `bytes_length` bytes from the buffer and return it as bytes.
        '''
        return buffer.read(bytes_length)

    @staticmethod
    def skip_bytes(buffer: BufferedIOBase, bytes_length: int) -> None:
        '''
        ### Skip `bytes_length` bytes from the buffer.
        '''
        buffer.read(bytes_length)
