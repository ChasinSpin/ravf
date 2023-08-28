import cv2
import numpy as np

class RavfImageUtils:
    @classmethod
    def bytes_to_np_array(cls, buffer: bytes, stride: int, height: int) -> np.array:
        """Converts bytes to a numpy array of uint8"""
        assert (stride * height) == len(buffer), 'Stride x height != buffer length'
        image = np.frombuffer(buffer, dtype=np.uint8)
        image = image.reshape(height, stride)
        return image

    @classmethod
    def bytes_to_np_array_16bit(cls, buffer: bytes, stride: int, height: int) -> np.array:
        """Converts bytes to a numpy array of uint16"""
        assert (stride * height) == len(buffer), 'Stride x height != buffer length'
        image = np.frombuffer(buffer, dtype=np.uint16)
        image = image.reshape(height, stride//2)
        return image

    @classmethod
    def unstride_12bit(cls, image: np.array, width: int, height: int) -> np.array:
        """Removes the stride padding from the image, so image size is width x height, image should be in uint8 (before unpacking)"""
        unstride_length = ((width * 3) // 2)
        image = image[:,:unstride_length]
        return image

    @classmethod
    def unstride_10bit(cls, image: np.array, width: int, height: int) -> np.array:
        """Removes the stride padding from the image, so image size is width x height, image should be in uint8 (before unpacking)"""
        unstride_length = ((width * 5) // 4)
        image = image[:,:unstride_length]
        return image

    @classmethod
    def unstride_16bit(cls, image: np.array, width: int, height: int) -> np.array:
        unstride_length = width
        image = image[:,:unstride_length]
        return image

    @classmethod
    def unpack_12bit_pihq(cls, image: np.array, width: int, height: int, stride: int) -> np.array:
        """Unpacks a uint8 12-bit packed image into uint16 pixels"""
        image = image.flatten()
        image = image.astype(np.uint16)
        result = np.zeros(height * width, np.uint16)	# Holds the result

        # There are a few different 12 bit packing formats in the wild where 2x12 bit pixels are encoded into 3 bytes
        # This one for the Pi HQ is  aaaabbbb AAAAAAAA BBBBBBBB
        result[0::2] = (image[1::3] << 4) | ((image[0::3] & 0xF0) >> 4)
        result[1::2] = (image[2::3] << 4) | (image[0::3] & 0x0F)

        result = np.reshape(result, (height, width))

        return result

    @classmethod
    def unpack_10bit_pigsc(cls, image: np.array, width: int, height: int, stride: int) -> np.array:
        """Unpacks a uint8 10-bit packed image into uint16 pixels"""
        image = image.flatten()
        image = image.astype(np.uint16)
        result = np.zeros(height * width, np.uint16)	# Holds the result

        # 4 pixels are encoded into 5 bytes as follows
        # This one for the Pi HQ is  AAAAAAAA BBBBBBBB CCCCCCCC DDDDDDDD AABBCCDD
        # Bytes 1-4 contain the most sigficant bits and Byte 5 contains the least significant
        #result[0::4] = (image[0::5] << 2) | ((image[3::5] >> 6) & 0x03)
        #result[1::4] = (image[1::5] << 2) | ((image[3::5] >> 4) & 0x03)
        #result[2::4] = (image[2::5] << 2) | ((image[3::5] >> 2) & 0x03)
        #result[3::4] = (image[4::5] << 2) | (image[3::5] & 0x03)
        result[0::4] = (image[0::5] << 2) | ((image[4::5] >> 6) & 0x03)
        result[1::4] = (image[1::5] << 2) | ((image[4::5] >> 4) & 0x03)
        result[2::4] = (image[2::5] << 2) | ((image[4::5] >> 2) & 0x03)
        result[3::4] = (image[3::5] << 2) | (image[4::5] & 0x03)

        result = np.reshape(result, (height, width))

        return result

    @classmethod
    def scale_12_to_16bit(cls, image: np.array) -> np.array:
        """Scales and image from 12 to 16 bit"""
        return image << 4 

    @classmethod
    def scale_10_to_16bit(cls, image: np.array) -> np.array:
        """Scales and image from 10 to 16 bit"""
        return image << 6 

    @classmethod
    def debayer_BGGR_to_BGR(cls, image: np.array) -> np.array:
        """Converts a bayered image from BBGR to BGR, note opencv has whacky bayers""" 
        return cv2.cvtColor(image, cv2.COLOR_BayerRG2BGR)

    @classmethod
    def debayer_GBRG_to_BGR(cls, image: np.array) -> np.array:
        """Converts a bayered image from GBRG to BGR, note opencv has whacky bayers""" 
        return cv2.cvtColor(image, cv2.COLOR_BayerGR2BGR)

    @classmethod
    def debayer_BGGR_to_BGR_VNG(cls, image: np.array) -> np.array:
        """Converts a bayered image from BBGR to BGR using VNG, note opencv has whacky bayers""" 
        return cv2.cvtColor(image, cv2.COLOR_BayerRG2BGR_VNG)

    @classmethod
    def debayer_BGGR_to_GRAY(cls, image: np.array) -> np.array:
        """Converts a bayered image from BBGR to GRAY, note opencv has whacky bayers""" 
        return cv2.cvtColor(image, cv2.COLOR_BayerRG2GRAY)

    @classmethod
    def debayer_GBRG_to_GRAY(cls, image: np.array) -> np.array:
        """Converts a bayered image from GBRG to GRAY, note opencv has whacky bayers""" 
        return cv2.cvtColor(image, cv2.COLOR_BayerGR2GRAY)
