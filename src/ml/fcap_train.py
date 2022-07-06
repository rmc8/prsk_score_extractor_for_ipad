import os
import warnings
from glob import glob

warnings.simplefilter("ignore")  # nopep8

from PIL import Image
import numpy as np
from keras.utils import np_utils

from local_lib import models


WIDTH: int = 288
HIGHT: int = 38
epochs: int = 15
batch_size: int = 16
class_num: int = 12


def main():
    x_train: list = []
    y_train: list = []
    BASE_DIR: str = "./img/train/fcap_train"
    for cat_num, cat_name in enumerate(os.listdir(BASE_DIR), 1):
        dir_path: str = f"{BASE_DIR}/{cat_name}"
        for img_path in glob(f"{dir_path}/*.png"):
            img = Image.open(img_path)
            img_array = np.array(img)
            x_train.append(img_array)
            y_train.append(cat_num)
    model = models.model_vgg(class_num=class_num, height=HIGHT, width=WIDTH)
    x_arr = np.asarray(x_train) / 255
    y_arr = np_utils.to_categorical(np.array(y_train), class_num)
    history = model.fit(
        x_arr,
        y_arr,
        batch_size=batch_size,
        epochs=epochs,
        verbose=1,
        shuffle=True,
    )
    model.save_weights(f"weights{class_num}_{epochs}.h5")


if __name__ == "__main__":
    main()
