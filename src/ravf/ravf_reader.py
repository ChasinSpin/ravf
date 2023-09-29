from .metadata_entry import UTF8String, RavfColorType, RavfImageFormat
from .ravf_header import RavfHeader
from .ravf_index import RavfIndex
from .ravf_frame import RavfFrame
from .ravf_image_utils import RavfImageUtils

class RavfReader:

    """ Returns required_metadata_entries user_metadata_entries and index_table """
    def __init__(self, file_handle):
        self.header = RavfHeader.deserialize(file_handle)
        #print(self.header)

        offset_index = self.header.metadata_value('OFFSET-INDEX')
        file_handle.seek(offset_index, 0)
        self.index = RavfIndex.deserialize(file_handle)
        #print(self.index)

    def metadata(self) -> list((UTF8String, object)):
        return self.header.metadata()

    def metadata_value(self, name: str) -> object:
        return self.header.metadata_value(name)

    def frame_count(self) -> int:
        return self.index.count()

    def version(self) -> int:
        return self.header.version()

    def frame_by_index(self, file_handle, index) -> (RavfFrame): 
        ind = self.index.item(index)
        file_handle.seek(ind[0], 0)
        frame = RavfFrame.deserialize(file_handle)
        return frame
 
    def timestamps(self) -> list:
        return self.index.timestamps()

    """ Returns err, image, frameInfo, status for pymovie in mono format"""
    def getPymovieMainImageAndStatusData(self, file_handle, frame_to_show):
        stride = self.metadata_value('IMAGE-ROW-STRIDE')
        height = self.metadata_value('IMAGE-HEIGHT')
        width = self.metadata_value('IMAGE-WIDTH')
        format = self.metadata_value('IMAGE-FORMAT')

        frame = self.frame_by_index(file_handle, frame_to_show)

        if self.metadata_value('IMAGE-FORMAT') == RavfImageFormat.FORMAT_PACKED_10BIT.value:
            #print('Found 10bit packed')
            image = RavfImageUtils.bytes_to_np_array(frame.data, stride, height)
            image = RavfImageUtils.unstride_10bit(image, width, height)
            image = RavfImageUtils.unpack_10bit_pigsc(image, width, height, stride)
            image = RavfImageUtils.scale_10_to_16bit(image)
            if self.metadata_value('COLOR-TYPE') != RavfColorType.MONO.value:
               image = RavfImageUtils.debayer_BGGR_to_GRAY(image)
        elif self.metadata_value('IMAGE-FORMAT') == RavfImageFormat.FORMAT_PACKED_12BIT.value:
            #print('Found 12bit packed')
            image = RavfImageUtils.bytes_to_np_array(frame.data, stride, height)
            image = RavfImageUtils.unstride_12bit(image, width, height)
            image = RavfImageUtils.unpack_12bit_pihq(image, width, height, stride)
            image = RavfImageUtils.scale_12_to_16bit(image)
            image = RavfImageUtils.debayer_BGGR_to_GRAY(image)
        elif self.metadata_value('IMAGE-FORMAT') == RavfImageFormat.FORMAT_UNPACKED_12BIT.value:
            #print('Found 12bit unpacked')
            image = RavfImageUtils.bytes_to_np_array_16bit(frame.data, stride, height)
            image = RavfImageUtils.unstride_16bit(image, width, height)
            image = RavfImageUtils.scale_12_to_16bit(image)
            image = RavfImageUtils.debayer_BGGR_to_GRAY(image)
        elif self.metadata_value('IMAGE-FORMAT') == RavfImageFormat.FORMAT_UNPACKED_10BIT.value:
            #print('Found 10bit unpacked')
            image = RavfImageUtils.bytes_to_np_array_16bit(frame.data, stride, height)
            image = RavfImageUtils.unstride_16bit(image, width, height)
            image = RavfImageUtils.scale_10_to_16bit(image)
            image = RavfImageUtils.debayer_GBRG_to_GRAY(image)
        elif self.metadata_value('IMAGE-FORMAT') == RavfImageFormat.FORMAT_16BIT.value:
            image = RavfImageUtils.bytes_to_np_array_16bit(frame.data, stride, height)
        else:
            raise ValueError('Unrecognized image type')

        frameInfo = {}
        ts = frame.start_timestamp_as_str()
        frameInfo['start_timestamp_date'] = ts[0]
        frameInfo['start_timestamp_time'] = ts[1]

        status = {
            'frame_type': frame.frame_type,
            'start_timestamp': frame.start_timestamp,
            'exposure_duration': frame.exposure_duration,
            'satellites': frame.satellites,
            'almanac_status': frame.almanac_status,
            'almanac_offset': frame.almanac_offset,
            'satellite_fix_status': frame.satellite_fix_status,
            'sequence': frame.sequence,
        }

        err = 0 

        return (err, image, frameInfo, status)
