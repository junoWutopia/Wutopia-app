import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import json
from PIL import Image
from mayavi import mlab
import cv2
import imageio

import sys
sys.path.append("..")
from core.Util import *
from core.Framelets import *
from core.JitterCorrection import *
from core.Vis3D import *
from core.ColorCorrection import *

def process_images():
    FRAMELET_RES_X = 2048
    FRAMELET_RES_Y = 1024

    img1_dict = np.load('example10_qs_img_mask1.npy', allow_pickle=True).item()
    base_img, base_mask = img1_dict['img1'], img1_dict['m1']
    img0_dict = np.load('example10_qs_img_mask0.npy', allow_pickle=True).item()
    extra_image, extra_mask = img0_dict['img0'], img0_dict['m0']


    base_mask = cv2.erode(base_mask.astype(np.float32), np.ones((121,121)))
    base_mask = cv2.GaussianBlur(base_mask, (121,121), sigmaX=50, sigmaY=50)
    extra_mask = np.maximum(extra_mask-base_mask, 0)

    base_img = base_img * base_mask[..., None] + extra_image * extra_mask[..., None]


    vel_dict = np.load('example10_quicksave3.npy', allow_pickle=True).item() # prominent velocity it 12 and secondary is 01
    mask2, mask1 = vel_dict['mask01'], vel_dict['mask12']

    mask1 = cv2.erode(mask1.astype(np.float32), np.ones((201,201)))
    mask1 = cv2.GaussianBlur(mask1, (201,201), sigmaX=90, sigmaY=90)
    mask2 = np.maximum(mask2-mask1, 0)

    mask_sum = mask1 + mask2
    mask_sum = np.where(mask_sum != 0, mask_sum, 1)


    vel = (vel_dict['vel12'] * mask1[..., None] + vel_dict['vel01'] * mask2[..., None]) / mask_sum[..., None]
    vx, vy = vel[..., 0], vel[..., 1]

    x_ind, y_ind = np.indices((FRAMELET_RES_Y, FRAMELET_RES_X))
    plt.figure(figsize=(36,16))
    plt.imshow(base_img / np.max(base_img))
    plt.xlim((0,FRAMELET_RES_X))
    plt.ylim((FRAMELET_RES_Y,0))
    plt.streamplot(y_ind, x_ind, vy, vx, linewidth=1.5, color=np.sqrt(vx ** 2 + vy ** 2), cmap='plasma', density=6)
    clb = plt.colorbar()
    clb.ax.set_title('m/s')
    plt.savefig('Optical_flow_red_spot.png')


    factor = 150 * 1024 / (20 * 10**6)
    vx, vy = vx * factor, vy * factor


    new_img = (base_img * 255 / np.max(base_img)).astype(np.uint8)
    fade_frames = 20
    new_vx = -vx.copy().astype(np.float32)
    new_vy = -vy.copy().astype(np.float32)
    images = [new_img]

    for i in range(fade_frames + 40):
        tmp = cv2.remap(new_img,
                        (y_ind - new_vy).astype(np.float32),
                        (x_ind - new_vx).astype(np.float32),
                        cv2.INTER_LINEAR)
        images.append(tmp)
        new_vx += cv2.remap(-vx,
                        (y_ind + new_vy).astype(np.float32),
                        (x_ind + new_vx).astype(np.float32),
                        cv2.INTER_LINEAR)
        new_vy += cv2.remap(-vy,
                        (y_ind + new_vy).astype(np.float32),
                        (x_ind + new_vx).astype(np.float32),
                        cv2.INTER_LINEAR) 

    images = images[::-1]
    new_vx = vx.copy().astype(np.float32)
    new_vy = vy.copy().astype(np.float32)

    for i in range(41):
        tmp = cv2.remap(new_img,
                        (y_ind - new_vy).astype(np.float32),
                        (x_ind - new_vx).astype(np.float32),
                        cv2.INTER_LINEAR)
        images.append(tmp)
        new_vx += cv2.remap(vx,
                        (y_ind + new_vy).astype(np.float32),
                        (x_ind + new_vx).astype(np.float32),
                        cv2.INTER_LINEAR)
        new_vy += cv2.remap(vy,
                        (y_ind + new_vy).astype(np.float32),
                        (x_ind + new_vx).astype(np.float32),
                        cv2.INTER_LINEAR)

    for i in range(1, fade_frames):
        ind = len(images) - fade_frames + i
        images[ind] = (i / fade_frames * images[i] + (1 - i / fade_frames) * images[ind]).astype(np.uint8)
    images = images[fade_frames:]

    for i in range(len(images)):
        images[i] = images[i][64:-64, 64:-64, :]
    #plt.imshow(images[i])
    #plt.show()

    with imageio.get_writer('red_dot_movie.gif', mode='I') as writer:
        for image in images:
            writer.append_data(image)


def prepro(image0, image1, image2, im_info0, im_info1, im_info2):

    pos = np.array([0.5,0.7,-0.3])
    pos *= JUPITER_EQUATORIAL_RADIUS / np.linalg.norm(pos)
    pos[2] *= JUPITER_POLAR_RADIUS / JUPITER_EQUATORIAL_RADIUS
    FRAMELET_RES_X = 2048
    FRAMELET_RES_Y = 1024
    raster = project_tangential_plane(pos, 40000, 20000, FRAMELET_RES_X, FRAMELET_RES_Y, 0)

    def get_image_gradients_and_data(image_path, im_info_path):
        img = Image.open(image_path)
        im_ar = np.array(img)
        im_ar = remove_bad_pixels(im_ar)

        with open(im_info_path, 'rb') as json_file:
            im_info_dict = json.load(json_file)

        start_time = im_info_dict["START_TIME"]
        frame_delay = float(im_info_dict["INTERFRAME_DELAY"].split()[0]) + 0.001

        start_correction, frame_delay = correct_image_start_time_and_frame_delay(im_ar, start_time, frame_delay)

        framelets = generate_framelets(revert_square_root_encoding(im_ar), start_time, start_correction, frame_delay)

        gradient_fields = [[], [], []]
        colors = np.zeros((FRAMELET_RES_Y, FRAMELET_RES_X, 3))
        color_counts = np.zeros((FRAMELET_RES_Y, FRAMELET_RES_X, 3))
        for k, framelet in enumerate(framelets):
            print_progress_bar(k+1, len(framelets),
                            'Processing framelet {} of {}:'.format(k + 1, len(framelets)),
                            length=18)

            brightnesses, y_coords, valid = framelet.get_pixel_val_at_surf_point(raster, sun_brightness_correction=True,
                                                                                return_y_indices=True)
            x_gradientx = (np.gradient(y_coords, axis=0) * valid)[..., None]
            x_gradienty = (np.gradient(y_coords, axis=1) * valid)[..., None]
            x_tangential_field = np.concatenate((x_gradientx, x_gradienty), axis=-1)
            x_tangential_field_norm_sq = np.sum(x_tangential_field ** 2, axis=-1)
            x_tangential_field_norm_sq = np.where(x_tangential_field_norm_sq != 0, x_tangential_field_norm_sq, 1)

            gradient_fields[2 - framelet.color].append(x_tangential_field / x_tangential_field_norm_sq[..., None])
            colors[..., 2 - framelet.color] += brightnesses
            color_counts[..., 2 - framelet.color] += valid
        colors = colors / np.maximum(color_counts, 1)
        mask = np.all(color_counts > 0, axis=-1)

        return colors, gradient_fields, mask



    img0, gradient_fields0, mask0 = get_image_gradients_and_data(image0, im_info0)
    np.save('example10_qs_img_mask0', {'img0':img0, 'm0':mask0})
    np.save('example10_qs_grad_fields0', {'g0':gradient_fields0})
    del img0, gradient_fields0, mask0

    img1, gradient_fields1, mask1 = get_image_gradients_and_data(image1, im_info1)
    np.save('example10_qs_img_mask1', {'img1':img1, 'm1':mask1})
    np.save('example10_qs_grad_fields1', {'g1':gradient_fields1})
    del img1, gradient_fields1, mask1

    img2, gradient_fields2, mask2 = get_image_gradients_and_data(image2, im_info2)
    np.save('example10_qs_img_mask2', {'img2':img2, 'm2':mask2})
    np.save('example10_qs_grad_fields2', {'g2':gradient_fields2})
    del img2, gradient_fields2, mask2


    with open(im_info0, 'rb') as json_file:
        im_info_dict = json.load(json_file)
        second_count0 = int(im_info_dict["SPACECRAFT_CLOCK_START_COUNT"].split(':')[0])
    with open(im_info1, 'rb') as json_file:
        im_info_dict = json.load(json_file)
        second_count1 = int(im_info_dict["SPACECRAFT_CLOCK_START_COUNT"].split(':')[0])
    with open(im_info2, 'rb') as json_file:
        im_info_dict = json.load(json_file)
        second_count2 = int(im_info_dict["SPACECRAFT_CLOCK_START_COUNT"].split(':')[0])

    time_delay01 = second_count1 - second_count0
    time_delay12 = second_count2 - second_count1
    pixel_in_meter = 20000000 / FRAMELET_RES_Y



    img_mask_dict0 = np.load('example10_qs_img_mask0.npy', allow_pickle=True).item()
    #grad_field_dict0 = np.load('example10_qs_grad_fields0.npy', allow_pickle=True).item()
    img_mask_dict1 = np.load('example10_qs_img_mask1.npy', allow_pickle=True).item()
    #grad_field_dict1 = np.load('example10_qs_grad_fields1.npy', allow_pickle=True).item()
    #all_gradient_fields01 = [x+y for x,y in zip(grad_field_dict0['g0'], grad_field_dict1['g1'])]
    mask01 = np.logical_and(img_mask_dict0['m0'], img_mask_dict1['m1'])
    img0, img1 = img_mask_dict0['img0'], img_mask_dict1['img1']
    #del grad_field_dict0

    vel01 = compute_optical_flow(img0, img1, mask=mask01)#, error_fields=all_gradient_fields01)
    vel01 = vel01 * pixel_in_meter / time_delay01
    #del all_gradient_fields01


    img_mask_dict2 = np.load('example10_qs_img_mask2.npy', allow_pickle=True).item()
    #grad_field_dict2 = np.load('example10_qs_grad_fields2.npy', allow_pickle=True).item()
    img_mask_dict1 = np.load('example10_qs_img_mask1.npy', allow_pickle=True).item()
    #grad_field_dict1 = np.load('example10_qs_grad_fields1.npy', allow_pickle=True).item()
    #all_gradient_fields12 = [x+y for x,y in zip(grad_field_dict1['g1'], grad_field_dict2['g2'])]
    mask12 = np.logical_and(img_mask_dict1['m1'], img_mask_dict2['m2'])
    img1, img2 = img_mask_dict1['img1'], img_mask_dict2['img2']
    #del grad_field_dict1, grad_field_dict2

    vel12 = compute_optical_flow(img1, img2, mask=mask12)#, error_fields=all_gradient_fields12)
    vel12 = vel12 * pixel_in_meter / time_delay12
    #del all_gradient_fields12


    vel = vel01 + vel12 / np.maximum(mask01 + mask12, 1)[..., None]

    np.save('example10_quicksave3', {'vel01':vel01,
                                    'vel12':vel12,
                                    'mask01':mask01,
                                    'mask12':mask12,
                                    'vel':vel})

    vx, vy = vel[..., 0], vel[..., 1]