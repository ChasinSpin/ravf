import struct

class RavfIndex:

    def __init__(self):
        self.__frames = []

    def add_frame(self, offset, start_timestamp):
        self.__frames.append((offset, start_timestamp))

    @classmethod
    def deserialize(cls, file_handle) -> object:
        index = cls()

        count_frames = struct.unpack('<I', file_handle.read(4))[0]

        for i in range(count_frames):
            frame = struct.unpack('<QQ', file_handle.read(16)) 
            index.__frames.append(frame)
       
        return index

    def __serialize(self) -> bytes:
        ser = struct.pack('<I', len(self.__frames))
        for i in range(len(self.__frames)):
            ser += struct.pack('<QQ', self.__frames[i][0], self.__frames[i][1])
        return ser

    def write(self, file_handle):
        file_handle.write(self.__serialize())    # Write the header

    def count(self):
        return len(self.__frames)

    def item(self, index: int) -> (int, int):
        return (self.__frames[index][0], self.__frames[index][1])

    def timestamps(self) -> list:
        timestamps = []
        for i in range(len(self.__frames)):
            timestamps.append(self.__frames[i][1])
        return timestamps

    def __repr__(self):
        return f'RavfIndex(frames(offset, timestamp) = {self.__frames})'
