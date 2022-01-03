# A very fudged program to make a curious title animation,
#
# Copyright:
#    If this program works I wrote it. If it does not, I dunno who made it.
#
# A lot of stuff is hacked and hard coded in, if you cannot understand my hard coding, sorry.

from colour import Color
import re
import math
from PIL import Image, ImageDraw, ImageFont
import os
import subprocess


def purge_folder(directory, pattern=".*.jpg"):
    """
    Create an empty output folder for the image series

    :param directory:
    :param pattern:
    :return:
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
    for f in os.listdir(directory):
        if re.search(pattern, f):
            os.remove(os.path.join(directory, f))


def convert_avi(folder_path, out_path):
    command = [ffmpeg_exe, '-f', 'image2', '-framerate', '8', '-i', f"{folder_path}\image%03d.jpg", '-y', out_path]

    for s in command:
        print(s.replace("\\\\", "\\"), end=' ')
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    process.wait()
    print(process.returncode)


def cos_positive(minimum, maximum):
    """
    generator func, makes a nice wave using ugly math
    :param amplify:
    :param minimum: minimum value
    :param maximum: max value
    :return:
    """
    rads = 0.0
    amplify = (maximum - minimum)/2
    while rads < 6.3:
        yield minimum + int((math.cos(rads) + 1.0)*amplify)
        rads += 0.03


class Rectangle:
    """
    Convenience class because no standard python lib has one
    """
    def __init__(self, x1, y1, x2, y2):
        self.x = self.left = x1
        self.y = self.top = y1
        self.x2 = self.right = x2
        self.y2 = self.bottom = y2

    def __str__(self):
        return('Rectangle(' + str(self.x) + ',' + str(self.y) + ','
               + str(self.x2) + ',' + str(self.y2)+')')

    def dims(self):
        return self.x, self.y, self.x2, self.y2

    def width(self):
        return int(math.fabs(self.x - self.x2))

    def height(self):
        return int(math.fabs(self.y - self.y2))

    def shrunk(self, amount):
        return Rectangle(self.x+amount, self.y-amount, self.x2-amount, self.y2+amount)


def get_bounding_box(font, point_size, string):
    """
    Calculates the bounding box of the text by drawing it into an empty bitmap.
    Trailing spaces do not count!
    """
    h = point_size * 2  # make sure bitmap is never zero width
    w = h + h*len(string)
    img = Image.new('RGB', (w, h), color=(0, 0, 0))
    d = ImageDraw.Draw(img)

    d.text((1, 1), string, font=font, fill="white")
    dims = img.getbbox()
    if dims is None:  # zero length or a nonprintable
        return Rectangle(0, 0, 0, 0)
    return Rectangle(*dims)


def rgb_to_hex(red, green, blue):
    """Return color as #rrggbb for the given color values."""
    return '#%02x%02x%02x' % (red, green, blue)


def hex_to_rgb(value):
    """Return (red, green, blue) for the color given as #rrggbb."""
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))


def build_boxes(pen, boxes, num_boxes, max, min):
    """
    this might be a generator function
    :param pen:
    :param boxes:
    :param num_boxes:
    :param max:
    :param min:
    :return:
    """

    def tweak_boxes(boxes, total, victims):
        """
        shrinks the victim boxes as needed
        :param boxes: box widths
        :param total: total width
        :param victim: which box index to grow to match the total
        :return: 
        """
        diff = sum(boxes) - total
        while abs(diff) > 1:
            for victim in victims:
                boxes[victim] -= diff/len(victims)
                if boxes[victim] < min:
                    boxes[victim] = min
            diff = sum(boxes) - total
        for i in range(len(boxes)):
            boxes[i] = int(boxes[i])

    width, height = pen.im.size
    index = len(boxes)
    b = [0] * NUM_BOXES
    b[0] = min + curve[index]
    b[1] = min + curve[int(index +curve_length/4*3) % curve_length]
    b[2] = min + curve[int(index +curve_length/4*2) % curve_length]
    b[3] = min + curve[int(index +curve_length/4*1) % curve_length]
    tweak_boxes(b, width, [1, 2, 3])
    boxes.append(b)


def get_font_weight(fnt, text, width):
    # return weight to use and width we expect to get
    # and font
    bounds = get_bounding_box(fnt, 44, text)
    weight = int(width/bounds.width() * 44)
    new_font = ImageFont.truetype(fnt.path, weight, layout_engine=ImageFont.LAYOUT_BASIC)
    bounds = get_bounding_box(new_font, weight, text)
    return weight, bounds.width(), new_font

# =======================================================================
IMAGE_WIDTH = 800
IMAGE_HEIGHT = 480
COLOUR_WHITE = (255, 255, 255)
COLOUR_BLACK = (2, 2, 2)
# loop through box animation sizes
BOX_MAX = int(IMAGE_HEIGHT*0.9)
BOX_MIN = int(BOX_MAX/7)
NUM_BOXES = 4
boxes = []

ffmpeg_exe = r"d:\tools\ffmpeg\bin\ffmpeg.exe"
font_filename = r"C:\Windows\fonts\Aliee13.ttf"
signature_text = "zaphodikus"
# Font for the footer subtitle, and it's location
SIGNATURE_SIZE = 22  # font point size
fnt_signature = ImageFont.truetype(font_filename, SIGNATURE_SIZE, layout_engine=ImageFont.LAYOUT_BASIC)
sig_coords = (IMAGE_WIDTH - get_bounding_box(fnt_signature, SIGNATURE_SIZE, signature_text + "M").width(),
              BOX_MAX + SIGNATURE_SIZE/2)
fnt_box44 = ImageFont.truetype(font_filename, SIGNATURE_SIZE*2, layout_engine=ImageFont.LAYOUT_BASIC)

# clean out old images
folder = os.path.join(os.getcwd(), 'images')
purge_folder(folder, ".*.jpg")
# blank canvas
new_image = Image.new('RGB', (IMAGE_WIDTH, IMAGE_HEIGHT), COLOUR_WHITE)

# build a sweet looking curve
curve = [0, 1, 1, 2, 2, 3, 4, 5, 7, 9, 12, 15, 20, 27, 30, 35, 39, 42, 44, 45, 46, 47, 47, 48, 47, 47, 46, 44, 42]
while curve[len(curve)-1]:
    v = max(curve[len(curve)-1]-2, 0)
    curve.append(v)
curve.reverse()
curve = [elem*((BOX_MAX-BOX_MIN)/max(curve)) for elem in curve]  # change the curve scale to match our canvas

slide_length = len(curve)
# colours to animate according to
slide_colors = list(Color("darkcyan").range_to(Color("ForestGreen"), slide_length))
slide_colors.extend(list(Color("ForestGreen").range_to(Color("royalblue"), slide_length)))
slide_colors.extend(list(Color("royalblue").range_to(Color("fuchsia"), slide_length)))
curve = curve*3
curve_length = len(curve)
print(f"Creating {curve_length} frames...")
index = 0
for cosine_index in curve:
    image_copy = new_image.copy()
    draw = ImageDraw.Draw(image_copy)
    build_boxes(draw, boxes, NUM_BOXES, BOX_MAX, BOX_MIN)

    print(f"\r{100*(index/curve_length):.0f}%", end='')
    x = 0
    for box_num in range(0, NUM_BOXES):
        current_width = boxes[index][box_num]
        c = slide_colors[int(index+ slide_length/4*box_num)%curve_length ].get_hex()
        draw.rectangle(Rectangle(x, BOX_MAX, x + current_width, BOX_MAX - current_width).dims(), fill=c)

        # font fit to box
        message_string = ["THIS", "IS", "VIDEO", "STUDIO"]
        min_weight,text_width, fnt_box = get_font_weight(fnt_box44, message_string[box_num] + 'I', current_width)
        msg_y = BOX_MAX - current_width / 2 - (min_weight / 2)
        msg_x = x + current_width/2 - text_width*0.47
        draw.text((msg_x, msg_y), message_string[box_num], font=fnt_box, fill=COLOUR_BLACK)
        draw.text(sig_coords, signature_text, font=fnt_signature, fill=COLOUR_BLACK)
        image_copy.save(f"{folder}\\image{index:03d}.jpg", "JPEG")

        x += current_width
    index += 1

print("\nCreating movie...")
# convert to avi
outpath = os.path.join(os.getcwd(), 'out.avi')
convert_avi(folder, outpath)
