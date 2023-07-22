import struct
from .metadata_entry import RavfMetadataEntry, RavfMetadataType

class RavfHeader:
    RAVF_VERSION = 1
    RAVF_MAGIC   = 0x46564152	# 'RAVF'

    def __update_metadata_entry(self, name: str, value: object):
        for entry in self.__metadata_entries:
            if entry.name.txt == name:
                entry.update(value)
                return

    """metadata_entries is a list of RavfMetadataEntry"""
    def __init__(self, metadata_entries: list):
        self.__version = self.RAVF_VERSION
        self.__metadata_entries = metadata_entries
        self.__frame_count = 0

        # Set OFFSET-FRAMES by serializing now to determine length
        self.__length = len(self.__serialize())
        self.__update_metadata_entry('OFFSET-FRAMES', self.__length)
        
    @classmethod
    def deserialize(cls, file_handle) -> object:
        (magic, version, count_metadata_entries) = struct.unpack('<IHI', file_handle.read(4+2+4))
        assert magic == cls.RAVF_MAGIC, 'Magic number mismatch'

        metadata_entries = []
        for i in range(count_metadata_entries):
            metadata_entries.append(RavfMetadataEntry.deserialize(file_handle))
       
        header = cls(metadata_entries = metadata_entries)
        header.__version = version
        return header

    def __serialize(self) -> bytes:
        ser = struct.pack('<IHI', self.RAVF_MAGIC, self.RAVF_VERSION, len(self.__metadata_entries))
        for entry in self.__metadata_entries:
            ser += entry.serialize()
        return ser

    def version(self) -> int:
        return self.__version

    def metadata_value(self, name: str) -> object:
        for entry in self.__metadata_entries:
            if entry.name.txt == name:
                return entry.value
        return None

    def metadata(self) -> list((str, object)):
        metadata = []
        for entry in self.__metadata_entries:
            if entry.entry_type == RavfMetadataType.UTF8STRING:
                value = entry.value.txt            
            else:
                value = entry.value

            metadata.append((entry.name.txt, value))

        return metadata

    def write(self, file_handle):
        self.__update_metadata_entry('FRAMES-COUNT', self.__frame_count)
        file_handle.seek(0, 0)                   # Move to begining of file
        file_handle.write(self.__serialize())    # Write the header
        file_handle.seek(0, 2)                   # Move to end of file

    def update_offset_index(self, offset):
        self.__update_metadata_entry('OFFSET-INDEX', offset)

    def increment_frame_count(self):
        self.__frame_count += 1

    def __repr__(self):
        return f'RavfHeader(version = {self.__version}, metadata_entries = {self.__metadata_entries})'
