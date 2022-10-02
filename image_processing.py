from pathlib import Path
from selectors import SelectorKey

import cv2
import numpy as np
import matplotlib.pyplot as plt
from mayavi import mlab
from mpl_toolkits.mplot3d import Axes3D
from PIL import Image
from PIL import ImageEnhance
from scipy.interpolate import splprep, splev
import skimage.exposure

# from core.Util import *
# from core.Framelets import *
# from core.JitterCorrection import *
# from core.Vis3D import *
# from core.ColorCorrection import *
from JupiterMagneticField.jrm09 import jrm09run
from JupiterMagneticField.jrm33 import jrm33run

from utils import *


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
        self.R: float = 0.85
        self.MaxDeg: int = 10

    #def Magnetic_field(self, extshell_rad: float, layer: int):
    #    #domian: extshell:0-2 float
    #    #        layer: 1-10 int
    #    jrm09run.map2d(self.R, self.MaxDeg)
    #    jrm09run.vecfld(extshell_rad, layer, self.MaxDeg)
    #    jrm33run.map2d(self.R, self.MaxDeg)
    #    jrm33run.vecfld(extshell_rad, layer, self.MaxDeg)
    #   theory3d1976.vecfld1976(extshell_rad, layer, MaxDeg)

    #def ball_present(self):
    #    with open(self.METADATA, 'rb') as json_file:
    #        im_info_dir = json.load(json_file)
    #    image = self.RAW
    #    img = Image.open(image)
    #    im_ar = np.array(img)
    #    im_ar = remove_bad_pixels(im_ar)
#
#    s1, s2 = im_ar.shape
#
#    mask1 = get_raw_image_mask(im_ar)
#
#    start_time = im_info_dir["START_TIME"]
#    frame_delay = float(im_info_dir["INTERFRAME_DELAY"].split()[0])+0.001
#
#    start_correction, frame_delay = correct_image_start_time_and_frame_delay(im_ar, start_time, frame_delay)
#
#    framelets = generate_framelets(revert_square_root_encoding(im_ar), start_time, start_correction, frame_delay)
#
#    visualize_framelets_with_mayavi(framelets, 1024, 2048)


class Colormapper:

    colormap_types = {
        'AUTUMN': 0,
        'BONE': 1,
        'JET': 2,
        'WINTER': 3,
        'RAINBOW': 4,
        'OCEAN': 5,
        'SUMMER': 6,
        'SPRING': 7,
        'COOL': 8,
        'HSV': 9,
        'PINK': 10,
        'HOT': 11,
        'PARULA': 12,
        'MAGMA': 13,
        'INFERNO': 14,
        'PLASMA': 15,
        'VIRIDIS': 16,
        'CIVIDIS': 17,
        'TWILIGHT': 18,
        'TWILIGHT SHIFTED': 19,
        'TURBO': 20,
        'DEEPGREEN': 21
    }

    def __init__(self, img: Image.Image, save_dir: Path):
        self.img = np.array(img)
        self.save_dir = get_path(save_dir)

    def generate(self):
        for name, value in self.colormap_types.items():
            mapped = cv2.applyColorMap(self.img, value)
            cv2.imwrite(str(self.save_dir / f'{name}.png'), mapped)


def adjust_hsl(img: Image.Image, hue: float, saturation: float,
               lightness: float) -> Image.Image:
    f_img = np.array(img).astype(np.float32)  # RGB
    f_img /= 255

    hls_img = cv2.cvtColor(f_img, cv2.COLOR_RGB2HLS)

    # Hue
    hls_img[:, :, 0] += hue
    hls_img[:, :, 0] = hls_img[:, :, 0] % 360
    # Lightness
    hls_img[:, :, 1] *= (1 + lightness / 100.0)
    hls_img[:, :, 1][hls_img[:, :, 1] > 1] = 1
    # Saturation
    hls_img[:, :, 2] *= (1 + saturation / 100.0)
    hls_img[:, :, 2][hls_img[:, :, 2] > 1] = 1

    result_img = cv2.cvtColor(hls_img, cv2.COLOR_HLS2RGB)
    result_img = ((result_img * 255).astype(np.uint8))
    return Image.fromarray(result_img)


def adjust_brightness(img: Image.Image, factor: float) -> Image.Image:
    enhancer = ImageEnhance.Brightness(img)
    return enhancer.enhance(factor)


def adjust_contrast(img: Image.Image, factor: float) -> Image.Image:
    enhancer = ImageEnhance.Contrast(img)
    return enhancer.enhance(factor)
