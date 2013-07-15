import Image
import re
import math
import graphics

class ImageDeskewer:
    def __init__(self, bg_color = 255,
                 contrast_tolerance = 120):
        self.angle_step = 2
        self.bg_color = bg_color
        self.contrast_tolerance = contrast_tolerance

    def deskew(self, image_path, deskewed_image_path):
        try:
            image = Image.open(image_path)
        except:
            return False
        deskew_angle = self.get_deskew_angle(image)
        if not deskew_angle:
            return False
        deskewed_image = image.convert('RGBA').rotate(-deskew_angle,
                                                       Image.BICUBIC)
        collage = Image.new('L', image.size, color = self.bg_color)
        collage.paste(deskewed_image, None, deskewed_image)
        collage = collage.convert('RGB')
        collage.save(deskewed_image_path, format=image.format)
        return True

    def get_deskew_angle(self, image_orig):
        width, height = image_orig.size
        resize_ratio = 600 / float(width)
        # Convert image to grayscale and resize it for better
        # performance
        image = image_orig.convert('L')
        image = image.resize((int(round(width * resize_ratio)),
                              int(round(height * resize_ratio))))
        width, height = image.size
        max_r = int(round(math.sqrt(width ** 2 + height ** 2)))
        hough_accumulator = {}

        for x in range(0, width):
            for y in range(0, height - 1):
                if y + 1 > height:
                    break
                color = image.getpixel((x, y))
                color_below = image.getpixel((x, y + 1))
                if graphics.colorsContrast(color, self.bg_color,
                                           self.contrast_tolerance) and \
                   graphics.colorsContrast(color, color_below,
                                           self.contrast_tolerance):
                   for r, angle in self.__getDistanceAndAngle(x, y):
                       if 0 < r < max_r:
                           vote_value = hough_accumulator.get((r, angle), 0)
                           hough_accumulator[(r, angle)] = vote_value + 1

        if not hough_accumulator:
            return 0
        max_voted = hough_accumulator.keys()[0]
        for r_angle in hough_accumulator:
            max_voted_value = hough_accumulator.get(max_voted)
            if hough_accumulator[r_angle] > max_voted_value:
                max_voted = r_angle

        return 90 - max_voted[1]

    def __getDistanceAndAngle(self, x, y):
        for angle in range(1, 180, 1):
            angle_radians = angle * math.pi / 180
            r = math.cos(angle_radians) * x + math.sin(angle_radians) * y
            r = int(round(r))
            yield r, angle



	
