import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
from .matcher import *
import base64

def blend_linear(image_1, image_2):
    img_1_mask = ((image_1[:, :, 0] | image_1[:, :, 1] | image_1[:, :, 2]) > 0)
    img_2_mask = ((image_2[:, :, 0] | image_2[:, :, 1] | image_2[:, :, 2]) > 0)

    r, c = np.nonzero(img_1_mask)
    out_1_center = [np.mean(r), np.mean(c)]
    r, c = np.nonzero(img_2_mask)
    out_2_center = [np.mean(r), np.mean(c)]

    vec = np.array(out_2_center) - np.array(out_1_center)
    intsct_mask = img_1_mask & img_2_mask

    r, c = np.nonzero(intsct_mask)
    out_mask = np.zeros(img_2_mask.shape[:2])
    proj_val = (r - out_1_center[0]) * vec[0] + (c - out_1_center[1]) * vec[1]
    out_mask[r, c] = (proj_val - (min(proj_val) + 1e-3)) / \
                      ((max(proj_val) - 1e-3) - (min(proj_val) + 1e-3))
    # blending
    mask_1 = img_1_mask & (out_mask == 0)
    mask_2 = out_mask
    mask_3 = img_2_mask & (out_mask == 0)

    out = np.zeros(image_1.shape)
    for c in range(3):
        out[:, :, c] = image_1[:, :, c] * (mask_1 + (1 - mask_2) * (mask_2 != 0)) + \
                       image_2[:, :, c] * (mask_2 + mask_3)

    return np.uint8(out)

def decodeBase64(data):
    new_data = data.split(",")[1]
    im_bytes = base64.b64decode(new_data)
    im_arr = np.frombuffer(im_bytes, dtype=np.uint8)  # im_arr is one-dim Numpy array
    img = cv2.imdecode(im_arr, flags=cv2.IMREAD_COLOR)
    img = cv2.resize(img, (500, 500))
    return img

def trim(frame):
    #crop top
    if not np.sum(frame[0]):
        return trim(frame[1:])
    #crop bottom
    if not np.sum(frame[-1]):
        return trim(frame[:-2])
    #crop left
    if not np.sum(frame[:, 0]):
        return trim(frame[:, 1:])
    #crop right
    if not np.sum(frame[:, -1]):
        return trim(frame[:, :-2])
    return frame

class Stitch:
    def __init__(self, data, directory_output):
        self.data = data
        self.directory_output = directory_output
        self.images = self.load_image()
        self.left_list = []
        self.right_list = []
        self.left_image = None
        self.right_image = None
        self.prepare_list()
        self.idImage = 1
        self.matcher = SIFT(directory_output)

    def load_image(self):
        imgs = []
        for i in range(len(self.data)):
            img = decodeBase64(self.data[i])
            imgs.append(img)
        return imgs

    def prepare_list(self):
        count_img = len(self.images)
        id_center = count_img / 2
        for i in range(count_img):
            if i <= id_center:
                self.left_list.append(self.images[i])
            else:
                self.right_list.append(self.images[i])

    def left_shift(self):
        image = self.left_list[0]
        for image_next in self.left_list[1:]:
            homography = self.matcher.match(image, image_next, self.idImage)
            # invert homography
            ih = np.linalg.inv(homography)

            br = np.dot(
                ih,
                np.array([image.shape[1], image.shape[0], 1])
            )
            br = br / br[-1]
            tl = np.dot(ih, np.array([0, 0, 1]))
            tl = tl / tl[-1]
            bl = np.dot(ih, np.array([0, image.shape[0], 1]))
            bl = bl / bl[-1]
            tr = np.dot(ih, np.array([image.shape[1], 0, 1]))
            tr = tr / tr[-1]

            cx = int(max(
                [0, image.shape[1], tl[0], bl[0], tr[0], br[0]]
            ))
            cy = int(max(
                [0, image.shape[0], tl[1], bl[1], tr[1], br[1]]
            ))
            offset = [
                abs(int(min(
                    [0, image.shape[1], tl[0], bl[0], tr[0], br[0]]
                ))),
                abs(int(min(
                    [0, image.shape[0], tl[1], bl[1], tr[1], br[1]]
                )))
            ]

            dSize = (cx + offset[0], cy + offset[1])
            print('image dSize =', dSize, 'offset =', offset)
            tl[0: 2] += offset
            bl[0: 2] += offset
            tr[0: 2] += offset
            br[0: 2] += offset

            dstPoints = np.array([tl, bl, tr, br])
            srcPoints = np.array(
                [
                    [0, 0],
                    [0, image.shape[0]],
                    [image.shape[1], 0],
                    [image.shape[1], image.shape[0]]
                ]
            )
            m_off = cv2.findHomography(srcPoints, dstPoints)[0]

            warp_img_1 = np.zeros(
                [dSize[1], dSize[0], 3],
                np.uint8
            )
            warp_img_1[
                offset[1]:image_next.shape[0] + offset[1],
                offset[0]:image_next.shape[1] + offset[0]
            ] = image_next
            warp_img_2 = cv2.warpPerspective(image, m_off, dSize)
            tmp = blend_linear(warp_img_1, warp_img_2)
            image = trim(tmp)
            name_image = self.matcher.convert_link_file_to_true_directory("results\ result_" + str(self.idImage) + '.jpg')
            cv2.imwrite(name_image, image)
            self.idImage += 1
        self.left_image = image

    def right_shift(self):
        tmp = None
        for image_next in self.right_list:
            homography = self.matcher.match(self.left_image, image_next, self.idImage)

            br = np.dot(
                homography,
                np.array([image_next.shape[1], image_next.shape[0], 1])
            )
            br = br / br[-1]
            tl = np.dot(homography, np.array([0, 0, 1]))
            tl = tl / tl[-1]
            bl = np.dot(homography, np.array([0, image_next.shape[0], 1]))
            bl = bl / bl[-1]
            tr = np.dot(homography, np.array([image_next.shape[1], 0, 1]))
            tr = tr / tr[-1]

            cx = int(max(
                [0, self.left_image.shape[1], tl[0], bl[0], tr[0], br[0]]
            ))
            cy = int(max(
                [0, self.left_image.shape[0], tl[1], bl[1], tr[1], br[1]]
            ))
            offset = [
                abs(int(min(
                    [0, self.left_image.shape[1], tl[0], bl[0], tr[0], br[0]]
                ))),
                abs(int(min(
                    [0, self.left_image.shape[0], tl[1], bl[1], tr[1], br[1]]
                )))
            ]

            dSize = (cx + offset[0], cy + offset[1])
            print('image dSize =', dSize, 'offset =', offset)
            tl[0: 2] += offset
            bl[0: 2] += offset
            tr[0: 2] += offset
            br[0: 2] += offset

            dstPoints = np.array([tl, bl, tr, br])
            srcPoints = np.array(
                [
                    [0, 0],
                    [0, image_next.shape[0]],
                    [image_next.shape[1], 0],
                    [image_next.shape[1], image_next.shape[0]]
                ]
            )
            m_off = cv2.findHomography(dstPoints, srcPoints)[0]

            warp_img_1 = np.zeros(
                [dSize[1], dSize[0], 3],
                np.uint8
            )
            warp_img_1[
                offset[1]:self.left_image.shape[0] + offset[1],
                offset[0]:self.left_image.shape[1] + offset[0]
            ] = self.left_image
            warp_img_2 = cv2.warpPerspective(image_next, m_off, dSize, flags=cv2.WARP_INVERSE_MAP)
            tmp = blend_linear(warp_img_1, warp_img_2)
            self.left_image = trim(tmp)
            name_image = self.matcher.convert_link_file_to_true_directory("results\ result_" + str(self.idImage) + '.jpg')
            cv2.imwrite(name_image, self.left_image)
            self.idImage += 1
        self.right_image = trim(tmp)

    def finish(self):
        result = self.matcher.convert_link_file_to_true_directory('results\ result_' + str(self.idImage) + '.jpg')
        cv2.imwrite(result, self.left_image)

    def run_stitch(self):
        self.left_shift()
        self.right_shift()
        self.finish()
