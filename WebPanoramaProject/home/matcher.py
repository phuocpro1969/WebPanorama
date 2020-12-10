import cv2
import numpy as np
import os
import base64
from io import BytesIO
from PIL import Image

def encodeBase64(img):
    _, buffer = cv2.imencode('.jpg', img)
    new_image_string = "data:image/jpg;base64," + base64.b64encode(buffer).decode("utf-8")
    return new_image_string

class SIFT:
    def __init__(self, directory_output):
        self.sift = cv2.xfeatures2d.SIFT_create()
        FLANN_INDEX_KDTREE = 1
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        search_params = dict(checks=50)
        self.PLANN = cv2.FlannBasedMatcher(index_params, search_params)
        self.MIN_MATCH_COUNT = 10
        self.directory_output = directory_output

    def keyPoints(self, img):
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        kp, des = self.sift.detectAndCompute(img_gray, None)
        return kp, des

    def match(self, src_img, test_img, idImage, arrKeyPoints, arrKeyPointsAfterCompare, arrMatcher, arrRansac):
        # Get keypoints in image
        kp_1, des_1 = self.keyPoints(src_img)
        kp_2, des_2 = self.keyPoints(test_img)
        dKP1 = cv2.drawKeypoints(src_img, kp_1, None)
        dKP2 = cv2.drawKeypoints(test_img, kp_2, None)

        arrKeyPointsAfterCompare.append(encodeBase64(dKP1))
        arrKeyPoints.append(encodeBase64(dKP2))

        # Matching keypoints
        matches = self.PLANN.knnMatch(des_1, des_2, k=2)
        matches_mask = [[0, 0] for i in range(len(matches))]

        #find good
        good = []
        for i, (m, n) in enumerate(matches):
            if m.distance < 0.7*n.distance:
                good.append(m)
                matches_mask[i] = [1, 0]

        draw_params = dict(
            matchColor=(0, 255, 0),
            singlePointColor=(255, 0, 0),
            matchesMask=matches_mask,
            flags=0
        )
        img_draw_matches = cv2.drawMatchesKnn(src_img, kp_1, test_img, kp_2, matches, None, **draw_params)
        arrMatcher.append(encodeBase64(img_draw_matches))

        if len(good) > self.MIN_MATCH_COUNT:
            src_pts = np.float32([kp_1[m.queryIdx].pt for m in good])
            dst_pts = np.float32([kp_2[m.trainIdx].pt for m in good])

            M, mask = cv2.findHomography(dst_pts, src_pts, cv2.RANSAC, 5.0)
            matches_mask = mask.ravel().tolist()
            draw_params = dict(
                matchColor=(0, 255, 0),
                singlePointColor=(255, 0, 0),
                matchesMask=matches_mask,
                flags=2,
            )
            img_match_RANSAC = cv2.drawMatches(src_img, kp_1, test_img, kp_2, good, None, **draw_params)
            arrRansac.append(encodeBase64(img_match_RANSAC))
            return M, arrKeyPoints, arrKeyPointsAfterCompare, arrMatcher, arrRansac
        else:
            matches_mask = None
        return None, arrKeyPoints, arrKeyPointsAfterCompare, arrMatcher, arrRansac