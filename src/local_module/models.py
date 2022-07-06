from keras.applications.vgg16 import VGG16
from keras.optimizers import Adam
from keras.layers import Activation, Dense, Dropout, Flatten, Input
from keras.models import Model


def model_vgg(class_num, height, width):
    out_num = class_num
    input_tensor = Input(shape=(height, width, 3))
    vgg = VGG16(include_top=False, input_tensor=input_tensor, weights=None)
    x = vgg.output
    x = Flatten()(x)
    x = Dense(2048, activation="relu")(x)
    x = Dropout(0.5)(x)
    x = Dense(2048, activation="relu")(x)
    x = Dropout(0.5)(x)
    x = Dense(out_num)(x)
    x = Activation("softmax")(x)
    model = Model(inputs=vgg.inputs, outputs=x)
    model.compile(optimizer=Adam(lr=1e-4), loss='categorical_crossentropy', metrics=['accuracy'])
    return model
