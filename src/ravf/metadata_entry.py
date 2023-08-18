import struct
from enum import Enum

class RavfColorType(Enum):

    MONO        = 0
    BAYER_RGGB  = 1
    BAYER_GRBG  = 2
    BAYER_GBRG  = 3
    BAYER_BGGR  = 4
    BAYER_CYYM  = 5
    BAYER_YCMY  = 6
    BAYER_YMCY  = 7
    BAYER_MYYC  = 8
    RGB         = 9
    BGR         = 10

class RavfImageEndianess(Enum):
    BIG_ENDIAN    = 0
    LITTLE_ENDIAN = 1

class RavfImageFormat(Enum):
    FORMAT_8BIT            = 0
    FORMAT_16BIT           = 1
    FORMAT_PACKED_10BIT    = 2
    FORMAT_PACKED_12BIT    = 3
    FORMAT_UNPACKED_10BIT  = 4
    FORMAT_UNPACKED_12BIT  = 5

class RavfEquinox(Enum):
    J2000 = 0
    JNOW  = 1

class RavfMetadataType(Enum):

    INT8       = 0
    UINT8      = 1
    INT16      = 2
    UINT16     = 3
    INT32      = 4
    UINT32     = 5
    INT64      = 6
    UINT64     = 7
    TIMESTAMP  = 8
    FLOAT32    = 9
    FLOAT64    = 10
    UTF8STRING = 11

class UTF8String:

    def __init__(self, txt):
        self.txt = txt
        self.string_as_bytes = bytes(self.txt, 'utf-8')
        self.length = 2 + len(self.string_as_bytes)

    @classmethod
    def deserialize(cls, file_handle) -> object:
        size = struct.unpack('<H', file_handle.read(2))[0]
        string_as_bytes = file_handle.read(size)
        return cls(string_as_bytes.decode('utf-8'))

    def serialize(self) -> bytes:
        ser = struct.pack('<H', len(self.string_as_bytes))
        ser += self.string_as_bytes
        return ser

    def __str__(self):
        return self.txt

class RavfMetadataEntry:

    def __python_type_for_entry_type(self, entry_type: RavfMetadataType) -> str:
        if   entry_type == RavfMetadataType.INT8:
            return 'int'
        elif entry_type == RavfMetadataType.UINT8:
            return 'int'
        elif entry_type == RavfMetadataType.INT16:
            return 'int'
        elif entry_type == RavfMetadataType.UINT16:
            return 'int'
        elif entry_type == RavfMetadataType.INT32:
            return 'int'
        elif entry_type == RavfMetadataType.UINT32:
            return 'int'
        elif entry_type == RavfMetadataType.INT64:
            return 'int'
        elif entry_type == RavfMetadataType.UINT64:
            return 'int'
        elif entry_type == RavfMetadataType.TIMESTAMP:
            return 'int'
        elif entry_type == RavfMetadataType.FLOAT32:
            return 'float'
        elif entry_type == RavfMetadataType.FLOAT64:
            return 'float'
        elif entry_type == RavfMetadataType.UTF8STRING:
            return 'str'
        else:
            raise ValueError('Unrecognized type')

    def __set_value(self, value: object):
        # Check if the class of the value matches the class expected for the entry_type
        if self.__python_type_for_entry_type(self.entry_type) == type(value).__name__:
            if  self.entry_type == RavfMetadataType.UTF8STRING:
                self.value = UTF8String(value)
            else:
                self.value = value
        else:
            raise ValueError('type of value does not match entry_type for: %s %s!=%s' % (self.name, (self.__python_type_for_entry_type(self.entry_type)), str(type(value).__name__)))

    def __init__(self, name: str, entry_type: RavfMetadataType, value: object, requires_update = False):
        self.name = UTF8String(name)
        self.entry_type = entry_type
        self.requires_update = requires_update
        self.__set_value(value)

    @classmethod
    def deserialize(cls, file_handle) -> object:
        name = UTF8String.deserialize(file_handle).txt
        entry_type = RavfMetadataType(int(file_handle.read(1)[0]))

        if   entry_type == RavfMetadataType.INT8:
            value = struct.unpack('b', file_handle.read(1))[0]
        elif entry_type == RavfMetadataType.UINT8:
            value = struct.unpack('B', file_handle.read(1))[0]
        elif entry_type == RavfMetadataType.INT16:
            value = struct.unpack('<h', file_handle.read(2))[0]
        elif entry_type == RavfMetadataType.UINT16:
            value = struct.unpack('<H', file_handle.read(2))[0]
        elif entry_type == RavfMetadataType.INT32:
            value = struct.unpack('<i', file_handle.read(4))[0]
        elif entry_type == RavfMetadataType.UINT32:
            value = struct.unpack('<I', file_handle.read(4))[0]
        elif entry_type == RavfMetadataType.INT64:
            value = struct.unpack('<q', file_handle.read(8))[0]
        elif entry_type == RavfMetadataType.UINT64:
            value = struct.unpack('<Q', file_handle.read(8))[0]
        elif entry_type == RavfMetadataType.TIMESTAMP:
            value = struct.unpack('<Q', file_handle.read(8))[0]
        elif entry_type == RavfMetadataType.FLOAT32:
            value = struct.unpack('<f', file_handle.read(4))[0]
        elif entry_type == RavfMetadataType.FLOAT64:
            value = struct.unpack('<d', file_handle.read(8))[0]
        elif entry_type == RavfMetadataType.UTF8STRING:
            value = UTF8String.deserialize(file_handle).txt
        else:
            raise ValueError('Unrecognized type')

        return cls(name = name, entry_type = entry_type, value = value)

    def update(self, value: object):
        self.requires_update = False
        self.__set_value(value)

    def serialize(self) -> bytes:
        ser = self.name.serialize()
        ser += struct.pack('B', self.entry_type.value)

        if   self.entry_type == RavfMetadataType.INT8:
            pack_str = 'b'
        elif self.entry_type == RavfMetadataType.UINT8:
            pack_str = 'B'
        elif self.entry_type == RavfMetadataType.INT16:
            pack_str = '<h'
        elif self.entry_type == RavfMetadataType.UINT16:
            pack_str = '<H'
        elif self.entry_type == RavfMetadataType.INT32:
            pack_str = '<i'
        elif self.entry_type == RavfMetadataType.UINT32:
            pack_str = '<I'
        elif self.entry_type == RavfMetadataType.INT64:
            pack_str = '<q'
        elif self.entry_type == RavfMetadataType.UINT64:
            pack_str = '<Q'
        elif self.entry_type == RavfMetadataType.TIMESTAMP:
            pack_str = '<Q'
        elif self.entry_type == RavfMetadataType.FLOAT32:
            pack_str = '<f'
        elif self.entry_type == RavfMetadataType.FLOAT64:
            pack_str = '<d'
        elif self.entry_type == RavfMetadataType.UTF8STRING:
            return ser + self.value.serialize()
        else:
            raise ValueError('Unrecognized type')

        ser += struct.pack(pack_str, self.value)

        return ser

    def __repr__(self):
        return f'RavfMetadataEntry(name = {self.name}, entry_type = {self.entry_type}, value = {self.value})'
