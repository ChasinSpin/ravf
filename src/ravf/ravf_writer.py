from .metadata_entry import UTF8String, RavfMetadataEntry, RavfMetadataType, RavfColorType, RavfImageEndianess, RavfImageFormat, RavfEquinox
from .ravf_header import RavfHeader
from .ravf_frame import RavfFrame, RavfFrameType
from .ravf_index import RavfIndex

class RavfWriter:

    """entries is a list of type: RavfMetadataEntry"""
    def __has_entry(self, name: str, entries: list):
        for entry in entries:
             if entry.name.txt == name:
                 return True
        return False

    def __init__(self, file_handle, required_metadata_entries: list((UTF8String, object)), user_metadata_entries: list((UTF8String, RavfMetadataType, object))):

        private_required_entries = [
            RavfMetadataEntry('OFFSET-FRAMES',               RavfMetadataType.UINT64, int(0)),
            RavfMetadataEntry('OFFSET-INDEX',                RavfMetadataType.UINT64, int(0)),
            RavfMetadataEntry('FRAMES-COUNT',                RavfMetadataType.UINT32, int(0)),
        ]

        public_required_entries = [
            RavfMetadataEntry('COLOR-TYPE',                  RavfMetadataType.UINT8,      int(RavfColorType.MONO.value),               True), 
            RavfMetadataEntry('IMAGE-ENDIANESS',             RavfMetadataType.UINT8,      int(RavfImageEndianess.LITTLE_ENDIAN.value), True),
            RavfMetadataEntry('IMAGE-WIDTH',                 RavfMetadataType.UINT32,     int(0),                                      True),
            RavfMetadataEntry('IMAGE-HEIGHT',                RavfMetadataType.UINT32,     int(0),                                      True),
            RavfMetadataEntry('IMAGE-ROW-STRIDE',            RavfMetadataType.UINT32,     int(0),                                      True),
            RavfMetadataEntry('IMAGE-FORMAT',                RavfMetadataType.UINT8,      int(RavfImageFormat.FORMAT_8BIT.value),      True),
            RavfMetadataEntry('IMAGE-BINNING-X',             RavfMetadataType.UINT8,      int(1)),
            RavfMetadataEntry('IMAGE-BINNING-Y',             RavfMetadataType.UINT8,      int(1)),
            RavfMetadataEntry('RECORDER-SOFTWARE',           RavfMetadataType.UTF8STRING, ''),
            RavfMetadataEntry('RECORDER-SOFTWARE-VERSION',   RavfMetadataType.UTF8STRING, ''),
            RavfMetadataEntry('RECORDER-HARDWARE',           RavfMetadataType.UTF8STRING, ''),
            RavfMetadataEntry('RECORDER-HARDWARE-VERSION',   RavfMetadataType.UTF8STRING, ''),
            RavfMetadataEntry('INSTRUMENT',                  RavfMetadataType.UTF8STRING, ''),
            RavfMetadataEntry('INSTRUMENT-VENDOR',           RavfMetadataType.UTF8STRING, ''),
            RavfMetadataEntry('INSTRUMENT-VERSION',          RavfMetadataType.UTF8STRING, ''),
            RavfMetadataEntry('INSTRUMENT-SERIAL',           RavfMetadataType.UTF8STRING, ''),
            RavfMetadataEntry('INSTRUMENT-FIRMWARE-VERSION', RavfMetadataType.UTF8STRING, ''),
            RavfMetadataEntry('INSTRUMENT-SENSOR',           RavfMetadataType.UTF8STRING, ''),
            RavfMetadataEntry('INSTRUMENT-GAIN',             RavfMetadataType.FLOAT32,    float(1.0)),
            RavfMetadataEntry('INSTRUMENT-GAMMA',            RavfMetadataType.FLOAT32,    float(1.0)),
            RavfMetadataEntry('INSTRUMENT-SHUTTER',          RavfMetadataType.UINT64,     int(0)),
            RavfMetadataEntry('INSTRUMENT-OFFSET',           RavfMetadataType.UINT32,     int(0)),
            RavfMetadataEntry('TELESCOPE',                   RavfMetadataType.UTF8STRING, ''),
            RavfMetadataEntry('OBSERVER',                    RavfMetadataType.UTF8STRING, ''),
            RavfMetadataEntry('OBSERVER-ID',                 RavfMetadataType.UTF8STRING, ''),
            RavfMetadataEntry('LATITUDE',                    RavfMetadataType.FLOAT32,    float(0.0)),
            RavfMetadataEntry('LONGITUDE',                   RavfMetadataType.FLOAT32,    float(0.0)),
            RavfMetadataEntry('ALTITUDE',                    RavfMetadataType.FLOAT32,    float(0.0)),
            RavfMetadataEntry('OBJNAME',                     RavfMetadataType.UTF8STRING, ''),
            RavfMetadataEntry('RA',                          RavfMetadataType.FLOAT32,    float(0.0)),
            RavfMetadataEntry('DEC',                         RavfMetadataType.FLOAT32,    float(0.0)),
            RavfMetadataEntry('EQUINOX',                     RavfMetadataType.UINT8,      int(RavfEquinox.JNOW.value)),
            RavfMetadataEntry('RECORDING-START-UTC',         RavfMetadataType.TIMESTAMP,  int(0)),
            RavfMetadataEntry('COMMENT',                     RavfMetadataType.UTF8STRING, ''),
            RavfMetadataEntry('FRAME-TIMING-ACCURACY',       RavfMetadataType.UINT64,     int(0),                                      True),
        ]

        # Update the required entries
        for entry in required_metadata_entries:
            # Sanity check on what we're changi9ng
            if self.__has_entry(entry[0], private_required_entries):
                raise ValueError(f'{entry[0]} exists in private_required_entries, unable to update this value')
            if not self.__has_entry(entry[0], public_required_entries):
                raise ValueError(f'{entry[0]} does not exist in public_required_entries, unable to update this value')

            for public_entry in public_required_entries:
                if public_entry.name.txt == entry[0]:
                    public_entry.update(entry[1])

        # Verify that all entries that need updating have been
        for public_entry in public_required_entries:
            if public_entry.requires_update:
                raise ValueError(f'{public_entry.name.txt} is required to be set')

        metadata_entries = private_required_entries + public_required_entries

        # Create the user metadata entries
        user_entries = []
        for entry in user_metadata_entries:
            if self.__has_entry(entry[0], metadata_entries):
                raise ValueError(f'{entry[0]} exists, unable to update this value')
            user_entries.append(RavfMetadataEntry(entry[0], entry[1], entry[2]))

        metadata_entries += user_entries

        print(*metadata_entries, sep='\n')

        self.header = RavfHeader(metadata_entries)
        self.header.write(file_handle)
        self.index = RavfIndex()

    def write_frame(self, file_handle, frame_type: RavfFrameType, data: bytes, start_timestamp: int, exposure_duration: int, satellites: int, almanac_status: int, almanac_offset: int, satellite_fix_status: int, sequence: int):
        offset_frame = file_handle.tell()

        frame = RavfFrame(frame_type, data, start_timestamp, exposure_duration, satellites, almanac_status, almanac_offset, satellite_fix_status, sequence)
        frame.write(file_handle)

        self.index.add_frame(offset_frame, start_timestamp)
        self.header.increment_frame_count()

    def version(self):
        return self.header.version

    def finish(self, file_handle):
        self.header.update_offset_index(file_handle.tell())
        self.header.write(file_handle)
        self.index.write(file_handle)

        print(self.header)
        #print(self.index)
