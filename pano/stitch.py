import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
import imutils
from matcher import *

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

class Stitch:
    def __init__(self, directory_input, directory_output):
        self.directory_input = directory_input
        self.directory_output = directory_output
        self.images = self.load_image()
        self.matcher = SIFT(directory_output)
        self.result = None
        self.idImage = 1

    def load_image(self):
        imgs = []
        for (dirname, dirnames, filenames) in os.walk(self.directory_input):
            imgs.extend([filename for filename in filenames if (filename.endswith('.jpg') or filename.endswith('.JPG') or filename.endswith('.png') or filename.endswith('.PNG'))])
            break
        print(imgs)
        images = [
            cv2.resize(cv2.imread(os.path.join(self.directory_input, img)), (500, 500)) for img in imgs
        ]
        return images

    def shift(self):
        tmp = None
        image = self.images[0]
        for image_next in self.images[1:]:
            homography = self.matcher.match(image, image_next, self.idImage)
            # invert homography
            try:
                ih = np.linalg.inv(homography)
            except:
                continue
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
            image = crop(tmp)
            self.idImage += 1
        self.result = image

    def finish(self):
        result = self.matcher.convert_link_file_to_true_directory('result.jpg')
        cv2.imwrite(result, self.result)
        cv2.waitKey(0)

    def run_stitch(self):
        self.shift()
        self.finish()
