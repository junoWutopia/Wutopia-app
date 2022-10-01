from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from PIL import ImageEnhance
from scipy.interpolate import splprep, splev
import skimage.exposure


class RGBCombiner:

    def __init__(self, image_dir: Path):
        self.image_dir = image_dir

        for f in image_dir.iterdir():
            if f.name.endswith('red.png'):
                self.R = np.array(cv2.imread(str(f), 0))
            elif f.name.endswith('green.png'):
                self.G = np.array(cv2.imread(str(f), 0))
            elif f.name.endswith('blue.png'):
                self.B = np.array(cv2.imread(str(f), 0))
            elif f.name.endswith('raw.png'):
                self.RAW = np.array(cv2.imread(str(f), 0))

        self.RGB_combined = None
        self.RGB_combine()
        self.RGB_smooth_contour_pic = None
        self.smooth_contours()

    def RGB_combine(self):
        self.RGB_combined = np.dstack([self.B, self.G, self.R]).astype(np.uint8)
        cv2.imwrite(str(self.image_dir / 'RGB_combined.png'), self.RGB_combined)

    def smooth_contours(self):
        # Reference: https://stackoverflow.com/questions/62078016/smooth-the-edges-of-binary-images-face-using-python-and-open-cv
        blur = cv2.GaussianBlur(self.RGB_combined, (0, 0),
                                sigmaX=3,
                                sigmaY=3,
                                borderType=cv2.BORDER_DEFAULT)
        self.RGB_smooth_contour_pic = skimage.exposure.rescale_intensity(
            blur, in_range=(127.5, 255), out_range=(0, 255))
        cv2.imwrite(str(self.image_dir / 'RGB_combined.png'),
                    self.RGB_smooth_contour_pic)


def adjust_brightness(img: Image, factor: float) -> Image:
    enhancer = ImageEnhance.Brightness(img)
    return enhancer.enhance(factor)


def adjust_contrast(img: Image, factor: float) -> Image:
    enhancer = ImageEnhance.Contrast(img)
    return enhancer.enhance(factor)
