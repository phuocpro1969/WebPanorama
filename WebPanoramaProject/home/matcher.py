import cv2
import numpy as np
import os

class SIFT:
    def __init__(self, directory_output):
        self.sift = cv2.xfeatures2d.SIFT_create()
        FLANN_INDEX_KDTREE = 1
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        search_params = dict(checks=50)
        self.PLANN = cv2.FlannBasedMatcher(index_params, search_params)
        self.MIN_MATCH_COUNT = 10
        self.directory_output = directory_output

    def convert_link_file_to_true_directory(self, name):
        return os.path.join(self.directory_output, name)

    def keyPoints(self, img):
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        kp, des = self.sift.detectAndCompute(img_gray, None)
        return kp, des

    def match(self, src_img, test_img, idImage):
        # set name
        name_matches = 'matcher\match_image_' + str(idImage) + '.jpg'
        name_matches = self.convert_link_file_to_true_directory(name_matches)
        name_RANSAC = 'ransac\match_RANSAC_image_' + str(idImage) + '.jpg'
        name_RANSAC = self.convert_link_file_to_true_directory(name_RANSAC)
        name_kp_1 = 'keypoints_image_after_compare\keypoints_image_src_compare_image_' + str(idImage) + '.jpg'
        name_kp_1 = self.convert_link_file_to_true_directory(name_kp_1)
        name_kp_2 = 'keypoints\keypoints_image_' + str(idImage) + '.jpg'
        name_kp_2 = self.convert_link_file_to_true_directory(name_kp_2)

        kp_1, des_1 = self.keyPoints(src_img)
        kp_2, des_2 = self.keyPoints(test_img)
        cv2.imwrite(name_kp_1, cv2.drawKeypoints(src_img, kp_1, None))
        cv2.imwrite(name_kp_2, cv2.drawKeypoints(test_img, kp_2, None))

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
        cv2.imwrite(name_matches, img_draw_matches)

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
            cv2.imwrite(name_RANSAC, img_match_RANSAC)
            return M
        else:
            matches_mask = None
        return None