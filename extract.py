#!/usr/bin/python3

# This script will extract all video segments from all jpg files in the current directory that contain video data.
# Verified to work with pictures taken with the Android camera app on a Pixel 7 Pro (Oct 2024)

# NOTES:

# Motion photos taken by Pixel phones will be named something like: PXL_20241019_021947626.MP.jpg.  Note the "MP" in
# the filename, indicating there's video data in the file.  Besides the filename, there are EXIF tags that indicate
# that there is video data.  The following tags are of interest:

# Motion Photo                    : 1
# MP Image Length                 : 42556
# MP Image Start                  : 3171685

# If there is video data, the "Motion Photo" tag will be present and set to 1.  For photos without video data, this
# tag is not present.  To determine where the video data starts, one must look at the MP tags shown above.  Basically,
# video data starts at "MP Image Start" + "MP Image Length" and runs to the end of the file.  Note that the MP tags are
# present in images without video data, so don't use their existence to assume the presence of video data.

# This has all been verified by using the Android camera app and exporting the video of the file (as raw video, not
# stabilized as that would recompress it) and then using a hex editor to compare  the contents of the exported video to
# examine the original jpg file.

import os
import subprocess

images = []

def main():
    # Obtain a sorted list of all images
    for filename in os.listdir("."):
        if not filename.lower().endswith('.jpg'):
            continue
        images.append(filename)
    images.sort()

    # Extract the video data from each image
    for filename in images:
    
        # Video photos will have the exif property "Motion Photo" and it will be "1"
        motion_photo = get_exif_prop("MotionPhoto", filename)
        is_motion_photo = len(motion_photo) == 1 and motion_photo == "1"
        if not is_motion_photo:
            print(f"Skipped {filename}")
            continue
        
        # Calculate start of video data
        mp_image_start = get_exif_prop("MPImageStart", filename)
        mp_image_len = get_exif_prop("MPImageLength", filename)
        offset = int(mp_image_start) + int(mp_image_len)
        #print(f"{filename} --> {mp_image_start} + {mp_image_len} = {offset}")
   
        # Read in the video data
        data = bytearray()
        with open(filename, 'rb') as file:
            file.seek(offset)
            data = file.read()
        
        # Save the video data to its own file (same name as jpg)
        video_filename, _ = os.path.splitext(filename)
        video_filename = f"{video_filename}.mp4"     
        with open(video_filename, 'wb') as outfile:
            outfile.write(data)
        print(f"Saved {filename} --> {video_filename}")

def get_exif_prop(prop, filename):
    command = ['exiftool', f"-{prop}", '-s', '-s', '-s', filename]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()
    return stdout.strip()

main()