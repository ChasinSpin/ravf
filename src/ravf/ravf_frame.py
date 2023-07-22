import struct
from enum import Enum
from datetime import datetime, timedelta, timezone

class RavfFrameType(Enum):
    LIGHT = 0
    BIAS  = 1
    DARK  = 2
    FLAT  = 3

class RavfFrame:
    RAVF_MAGIC   = 0xAF8ABD3C2A98CA3F
    RAVF_HEADER_NO_PADDING_LENGTH = 41

    def __init__(self, frame_type: RavfFrameType, data: bytes, start_timestamp: int, exposure_duration: int, satellites: int, almanac_status: int, almanac_offset: int, satellite_fix_status: int, sequence: int):
        self.frame_type = frame_type
        self.data = data
        self.start_timestamp = start_timestamp
        self.exposure_duration = exposure_duration
        self.satellites = satellites
        self.almanac_status = almanac_status
        self.almanac_offset = almanac_offset
        self.satellite_fix_status = satellite_fix_status
        self.sequence = sequence
        self.__frame_header_length_nopadding = self.RAVF_HEADER_NO_PADDING_LENGTH
        self.__frame_header_length = self.__frame_header_length_nopadding + 60
        
    @classmethod
    def deserialize(cls, file_handle) -> object:
        offset = file_handle.tell()

        (magic, frame_header_length, image_data_length, frame_type, start_timestamp, exposure_duration, satellites, almanac_status, almanac_offset, satellite_fix_status, sequence) = struct.unpack('<QIIBQQBBbBI', file_handle.read(cls.RAVF_HEADER_NO_PADDING_LENGTH))
        assert magic == cls.RAVF_MAGIC, 'Magic number mismatch'

        frame = cls(frame_type = frame_type, data = None, start_timestamp = start_timestamp, exposure_duration = exposure_duration, satellites = satellites, almanac_status = almanac_status, almanac_offset = almanac_offset, satellite_fix_status = satellite_fix_status, sequence = sequence)

        # Skip to image data
        file_handle.seek(offset + frame.__frame_header_length, 0)

        frame.data = file_handle.read(image_data_length)

        return frame

    def write(self, file_handle):
        ser = struct.pack('<QIIBQQBBbBI',
                          self.RAVF_MAGIC,
                          self.__frame_header_length,
                          len(self.data),
                          self.frame_type.value,
                          self.start_timestamp,
                          self.exposure_duration,
                          self.satellites,
                          self.almanac_status,
                          self.almanac_offset,
                          self.satellite_fix_status,
                          self.sequence,
                         )
                          
        ser += bytearray(60)
        file_handle.write(ser)
        file_handle.write(self.data)


    # Returns the start timestamp as a tuple (date,time)
    def start_timestamp_as_str(self) -> (str, str):
        epoch = datetime(2010, 1, 1, hour=0, minute=0, second=0, microsecond=0, tzinfo = timezone.utc) # 00:00:00 1st Jan 2010
        frame_seconds_since_epoch = timedelta(seconds = self.start_timestamp / 1000000000)
        timestamp = epoch + frame_seconds_since_epoch

        return (timestamp.strftime('%Y-%m-%d'), timestamp.strftime('%H:%M:%S.%f'))

    def __repr__(self):
        return f'RavfFrame(frame_type = {self.frame_type}, data_size: {len(self.data)}, start_timestamp = {self.start_timestamp}, exposure_duration = {self.exposure_duration}, satellites = {self.satellites}, almanac_status = {self.almanac_status}, almanac_offset = {self.almanac_offset}, satellite_fix_status = {self.satellite_fix_status}, sequence = {self.sequence})'
