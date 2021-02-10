from pathlib import Path
import os
import subprocess

pngs = "output"
gcodes = "gcodes"

import base64

def getGcodeThumbnail(input_file, size):
    output_file = '/tmp/i.png'

    command = f"convert {input_file} -fuzz 7% -trim -filter Triangle -define filter:support=2 -thumbnail {size} -unsharp 0.25x0.08+8.3+0.045 -dither None -posterize 136 -quality 82 -define jpeg:fancy-upsampling=off -define png:compression-filter=5 -define png:compression-level=9 -define png:compression-strategy=1 -define png:exclude-chunk=all -interlace none -colorspace sRGB {output_file}"

    os.system(command)

    output = subprocess.check_output("file " + output_file, shell=True)
    image_size = str(output[28:37]).replace(" ", "")

    filesize = os.path.getsize(output_file)

    result = ""
    with open(output_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())

        n = 78
        split_strings = [encoded_string[index : index + n] for index in range(0, len(encoded_string), n)]

        result += ';\n'
        result += f"; thumbnail begin {image_size[2:-1]} {filesize}\n"
        result += '; ' + '\n; '.join([str(s)[2:-1] for s in split_strings]) + '\n'
        result += "; thumbnail end\n"
        result += ';\n'

    return result


for path in Path(pngs).rglob("*.png"):
    str_path = str(path)

    gcodeThumbnail = getGcodeThumbnail(str_path, "220x124")
    gcode_filename = str_path.replace(pngs, gcodes).replace(".png", ".gcode")

    with open(gcode_filename, "r") as gcode_file:
        gcode_text = gcode_file.read()

    with open(gcode_filename, "w") as gcode_file:
        gcode_file.write(gcodeThumbnail)
        gcode_file.write(gcode_text)
