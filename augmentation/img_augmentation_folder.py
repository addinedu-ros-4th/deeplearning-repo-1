import tensorflow as tf
from PIL import Image
import matplotlib.pyplot as plt
import cv2
import numpy as np
import random
import os
import sys

#folder_path : 폴더 안에 있는 모든 이미지 파일을 증강 시키는 경우 

folder_path = "/home/dyjung/amr_ws/ml/project/data/augmentedIMG"
dist_folder_name = "augmentedIMG"


#folder 안이 비어있는지 확인
def isFolderEmpty():
    folder_contents = os.listdir(folder_path)
    if len(folder_contents) == 0:
        return True
    else:
        return False
    
def img_augmentation():

    file_list = os.listdir(folder_path)
    
    for file in file_list:
        #이미지 이름에 붙을 index
        img_index =0

        #저장할 경로 가져오기, 만들기 
        directory_path = folder_path +"/" + dist_folder_name
        os.makedirs(directory_path, exist_ok=True)

        #이미지 경로 
        img_path = folder_path + "/" + file

        #이미지 이름가져오기 파일 형태 제거하고
        img_name = file.split('.')[0]

        #이미지 읽기
        cv2_image = cv2.imread(img_path, cv2.IMREAD_COLOR)
        cv2_image = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)

        # 이미지 height, width, center x, center y
        (h, w) = cv2_image.shape[:2]
        (cX, cY) = (w // 2, h // 2)
        
        rot_angle = [0,90,180,270]

        #이미지 회전 랜덤한 숫자를 뽑아서 그만큼 회전 시킨 이미지 생성
        for val in rot_angle:
            random_numbers = random.sample(range(val,val+90), 10)
            
            for rn in random_numbers:
                matrix_rotate = cv2.getRotationMatrix2D((cX, cY), rn, 1.0)
                rotated_img = cv2.warpAffine(cv2_image, matrix_rotate, (w,h))
                rotated_img = cv2.cvtColor(rotated_img, cv2.COLOR_BGR2RGB)
                save_path = directory_path + "/" +img_name + "_augImg" + str(img_index) +".jpg"
                cv2.imwrite(save_path, rotated_img)
                img_index += 1

        #랜덤하게 숫자 뽑아서 Shear 변환 
        for val in range(0,20):
            random_number_for_xy = random.sample(range(-5,5), 2)
            random_number_for_angle_0 = random.uniform(-0.5,0.5)
            random_number_for_angle_1 = random.uniform(-1,1)
            aff = np.array([[1, random_number_for_angle_0, random_number_for_xy[0]],
                            [random_number_for_angle_1, 1, random_number_for_xy[1]]])
            shear_img = cv2.warpAffine(cv2_image, aff,(w+ int(h*0.5),h +int(w*0.5)))
            shear_img = cv2.cvtColor(shear_img, cv2.COLOR_BGR2RGB)
            save_path = directory_path + "/" +img_name + "_augImg" + str(img_index) +".jpg"
            cv2.imwrite(save_path, shear_img)
            img_index += 1

        #밝기 조절
        for val in range(0,10):
            random_numbers = random.sample(range(0,100),1)[0]
            bright_img = cv2.add(cv2_image, (random_numbers, random_numbers, random_numbers, 0))
            bright_img = cv2.cvtColor(bright_img, cv2.COLOR_BGR2RGB)
            save_path = directory_path + "/" +img_name + "_augImg" + str(img_index) +".jpg"
            cv2.imwrite(save_path, bright_img)
            img_index += 1
        
        #saturation 조절
        for val in range(0,10):
            random_alpha = random.uniform(0,5.0)
            saturated_img = np.clip((1+random_alpha)*cv2_image - 128*random_alpha, 0, 255).astype(np.uint8)
            saturated_img = cv2.cvtColor(saturated_img, cv2.COLOR_BGR2RGB)
            save_path = directory_path + "/" +img_name + "_augImg" + str(img_index) +".jpg"
            cv2.imwrite(save_path, saturated_img)
            img_index += 1

        #blurred 처리
        for val in range(0,10):
            random_k = random.sample(range(3,7),1)[0]
            blurred_img = cv2.blur(cv2_image, ksize=(random_k, random_k))
            blurred_img = cv2.cvtColor(blurred_img, cv2.COLOR_BGR2RGB)
            save_path = directory_path + "/" +img_name + "_augImg" + str(img_index) +".jpg"
            cv2.imwrite(save_path, blurred_img)
            img_index += 1        
        
        #noise 처리
        for val in range(0,10):
            random_std = random.uniform(0.1,0.9)
            noise = np.random.normal(0, random_std, cv2_image.shape).astype(np.uint8)
            noisy_img = cv2.add(cv2_image, noise)
            noisy_img = cv2.cvtColor(noisy_img, cv2.COLOR_BGR2RGB)
            save_path = directory_path + "/" +img_name + "_augImg" + str(img_index) +".jpg"
            cv2.imwrite(save_path, noisy_img)
            img_index += 1     

def main():
    if isFolderEmpty() == True:
        print("folder is empty")
        sys.exit()
    else:
        img_augmentation()

if __name__ == "__main__":
    main()