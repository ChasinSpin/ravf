# Raw Astro Video Format (RAVF) - Version 1

## Overview

This file format is designed to store raw frames coming from a camera to a file in realtime.  It consists of a reader and a writer

Design goals:

* Lightweight
* Minimal CPU resources
* Timing support for Occultations, Transits and Eclipses (OTE)
* Observation support
* Raw image and calibration data (including packed and CFA) stored in frames
* Per frame indexing
* Per frame additional data
* Mono or Color (CFA and RGB)
* Maximum 16 bit data
* Optional metadata

Due to CPU load possibly impacting frames per second on slower architectures,
it doesn't do the following during writing:

* Compression of the image data
* Unpacking of the image data
* Debayering CFA data

However, support is provided in the reader for unpacking, debayering image data, and conversion to 16-bit and 8-bit space.

## Conventions

Supported metadata types:

| Type | Id | Bytes | Description | 
|------|----|-------|-------------|
| int8       | 0  | 1          | Signed char |
| uint8      | 1  | 1          | Unsigned char |
| int16      | 2  | 2          | Signed short |
| uint16     | 3  | 2          | Unsigned short |
| int32      | 4  | 4          | Signed int |
| uint32     | 5  | 4          | Unsigned int |
| int64      | 6  | 8          | Signed long |
| uint64     | 7  | 8          | Unsigned long |
| timestamp  | 8  | 8          | Nanoseconds since 00:00:00 1st Jan 2010 |
| float32    | 9  | 4          | IEEE single-precision floating point |
| float64    | 10 | 8          | IEEE double-precision floating point |
| UTF8String | 11 | 2 + length | uint16 length + utf8 encoded string (no terminating Null) |

Frame types:

| Type | Id | Description |
|------|----|-------------|
| light | 0 | Light frames (normal image frames) |
| bias | 1 | Bias frames (calibration) - optional |
| dark | 2 | Dark frames (calibration) - optional |
| flat | 3 | Flat frames (calibration) - optional |

* All data is in little-endian format except the image data which can be little or big endian
* Image data is in Left to Right, Top to Bottom order
* Filenames have the extension "ravf"

## Format

| Name | Description |
|------|-------------|
| Header | Stores information about the proceeding data |
| Frames | Frames contain the image data and status information, stored sequentially |
| Index | Provides an index of all frames |

If a recording is interrupted, image data upto the point of interruption can be recovered and index rebuilt.


### Header

The first 4 bytes are 0x52 0x41 0x56 0x46 (RAVF) followed by:

| File Offset | Type | Description |
|--------|-------|-------------|
| 0x00 | uint32 | Magic 0x46564152 (RAVF) file identifier |
| 0x04 | uint16 | Version (1) |
| 0x06 | uint32 | Number of metadata entries (N) |
| 0x0A | bytes | N metadata entries |
Note: These types are regular serialization types (not metadata types)


####Metadata entry:

Note: Metadata tags cannot be changed after creation as it would
change the position of the data frame and cause corruption.

Every meta entry consists of 3 consecutive fields in this order:

| Field | Type |
| ----- | ---- |
| Name | Metadata type UTF8String | 
| Metadata Type | uint8 (the metadata type id) | 
| Value | See metadata type above |

Required metadata entries:

| Name | Metadata Type | Default | Description |
|------|---------------|---------|-------------|
| OFFSET-FRAMES | uint64 | 0 | Offset of the first frame from the start of the file (Read only) |
| OFFSET-INDEX | uint64 | 0 | Offset of the index from the start of the file (Read only) |
| FRAMES-COUNT | uint32 | 0 | Total number of frames (Read only) |
| COLOR-TYPE | uint8 | | MONO, BAYER\_RGGB, BAYER\_GRBG, BAYER\_GBRG, BAYER\_BGGR, BAYER\_CYYM, BAYER\_YCMY, BAYER\_YMCY, BAYER\_MYYC, BAYER\_RGB, BAYER\_BGR |
| IMAGE-ENDIANESS | uint8 | 1 | 1 = Little Endian, 0 = Big Endian for 16 bit image data |
| IMAGE-WIDTH | uint32 | | Width of image in pixels |
| IMAGE-HEIGHT | uint32 | | Height of image in pixels |
| IMAGE-ROW-STRIDE | uint32 | | This is the length of a row in bytes |
| IMAGE-FORMAT | uint8 | | 8bit, 16bit, 10bit\_UNPACKED, 10bit\_PACKED, 12bit\_UNPACKED, 12bit\_PACKED |
| IMAGE-BINNING-X | uint8 | 1 | Camera horizontal binning |
| IMAGE-BINNING-Y | uint8 | 1 | Camera vertical binning |
| RECORDER-SOFTWARE | UTF8String | | Name of the recording software |
| RECORDER-SOFTWARE-VERSION | UTF8String | | Version of the recording software |
| RECORDER-HARDWARE | UTF8String | | Name of the recording hardware |
| RECORDER-HARDWARE-VERSION | UTF8String | | Version of the recording hardware |
| INSTRUMENT | UTF8String | | Camera Model |
| INSTRUMENT-VENDOR | UTF8String | | Camera Vendor |
| INSTRUMENT-VERSION | UTF8String | | Camera Version |
| INSTRUMENT-SERIAL | UTF8String | | Camera Serial |
| INSTRUMENT-FIRMWARE-VERSION | UTF8String | | Camera Firmware Version |
| INSTRUMENT-SENSOR | UTF8String | | Camera Sensor, e.g. Sony - IMX477 |
| INSTRUMENT-GAIN | float32 | | Camera Gain |
| INSTRUMENT-GAMMA | float32 | | Camera Gamma }
| INSTRUMENT-SHUTTER | uint64 | | Camera shutter in duration in nanoseconds |
| INSTRUMENT-OFFSET | uint32 | | Camera image offset level in ADU |
| TELESCOPE | UTF8String | | Telescope model or name |
| OBSERVER | UTF8String | | Name of the observer |
| OBSERVER-ID | UTF8String | | ID of the observer  |
| LATITUDE | float32 | | Latitude of the recording |
| LONGITUDE | float32 | | Longitude of the recording |
| ALTITUDE | float32 | | Altitude of the recording |
| OBJNAME | UTF8STring | | Name of the observer object |
| RA | float32 | | Right ascension of the observed object in hours (0-24) |
| DEC | float32 | | Declination of the observed object in degrees |
| EQUINOX | uint8 | | Equinox of RA/DEC: 0 = J2000, 1 = JNOW | 
| RECORDING-START-UTC | timestamp | | Nanoseconds since 00:00:00 1st Jan 2010 UTC (JD 2455197.5), this is when recording was started and is not meant for timing purposes, system time is good enough |
| COMMENT | UTF8String | | Generic descriptive comment |
| FRAME-TIMING-ACCURACY | uint64 | | Accuracy of frame timestamps in ns |

Additional user tags can be added to this list at header creation time.

### Frames

Offset is the offset from the start of the data frame

| Offset | Name | Type | Description |
|--------|------|------|-------------|
| 0x00 | Magic | uint64 | Magic number: 0xAF8ABD3C2A98CA3F |
| 0x08 | Frame Header Length | uint32 | Offset of the start of the image data |
| 0x0C | Image Data Length | uint32 | Length of the image data |
| 0x10 | Frame Type | uint8 | See Frame type above |
| 0x11 | Timestamp Start | uint64 | Nanoseconds since 00:00:00 1st Jan 2010 UTC |
| 0x19 | Exposure duration | uint64 | Nanoseconds | 
| 0x21 | Gps Satellite | uint8 | Number of GPS Satellite used in the fix |
| 0x22 | Almanac Status | uint8 | A status flag indicating if the leap second correction to UTC us known/certain. 0 = certain, 1 = uncertain
| 0x23 | Almanac Offset | int8_t | Alamanac offset in seconds, this is the difference in leap seconds between the satellite UTC time and receiver known amount o leap seconds |
| 0x24 | Satellite Fix Status | uint8_t | 0 = No Fix, 1 = Internal Time keeping in a condition of a no fix after establishing a previous time or position fix, 2 = time fix, 3 = time and position fix |
| 0x4C | Frame Sequence | 4 bytes | Increments on every frame, missing number means dropped frame |
| 0x50 | Padding | 60 bytes | Padding for future use |
| 0x8C | Image data | Image Data Length(above) | Image data

### Index

| Offset | Type | Description |
|--------|------|-------------|
| 0x00 | uint32 | Total number of frames (N) |
| 0x04 | uint64 | Offset of Frame 1 from the beginning of the file |
| 0x0C | timestamp | Start timestamp of Frame 1 |
| 0x14 | uint64 | Offset of Frame 2 from the beginning of the file |
| 0x1C | timestamp | Start timestamp of Frame 2 |
| ... | ... | ... |
| | uint64 | Offset of Frame N from the beginning of the file |
| | timestamp | Start timestamp of Frame N |kkkk


   
