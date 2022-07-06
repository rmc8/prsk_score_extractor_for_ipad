import re
from typing import Optional, Any

import pyocr
import pyocr.builders
import pytesseract
from PIL import Image, ImageEnhance, ImageOps, ImageFilter

from .util import add_path

add_path(r"C:\Program Files (x86)\Tesseract-OCR")
add_path(r"C:\Program Files\Tesseract-OCR")

position_dict: dict = {
    "ipad_pro_2021_11": {
        "title": (222, 192, 2130, 308),
        "personal_score": {
            "position": (202, 361, 585, 1223),
            "offset": 393,
            "name_position": (12, 2, 370, 47),
            "difficulty_position": (113, 281, 270, 326),
            "score_position": (88, 339, 326, 394),
            "fcap_position": (20, 335, 308, 373),  # (20, 335, 308, 373)
            "combo_position": (145, 370, 310, 430),
            "accuracy_position": (210, 456, 320, 510),
            "accuracy_offset": 55,
        }
    }
}


class SCORE:
    def __init__(self, img_path: str, model: str = "ipad_pro_2021_11", builder=pyocr.builders.TextBuilder()):
        tools: list = pyocr.get_available_tools()
        self.tool = tools[0]
        img_obj = Image.open(img_path).filter(ImageFilter.MedianFilter())
        si = ImageEnhance.Sharpness(img_obj)
        self.img_obj = si.enhance(3.0)
        self.position_dict: dict = position_dict[model]
        self.img_box: Optional[Any] = None
        self.builder = builder
        self.fist: Optional[str] = None
        self.second: Optional[str] = None
        self. third: Optional[str] = None
        self.forth: Optional[str] = None
        self.fifth: Optional[str] = None

    def _crop(self, position: tuple):
        self.img_box = self.img_obj.crop(position)

    def _review(self, name: str, position: tuple):
        if type(name) is not str or name == "":
            name: str = "review"
        self._crop(position=position)
        self.img_box.save(f"./img/{name}.png")

    def _exec_ocr(self, box: bool = True, lang: str = "eng+jpn"):
        img = self.img_box if box else self.img_obj
        return self.tool.image_to_string(img, lang=lang, builder=self.builder)

    def _exec_ocr_img(self, img, lang: str = "eng+jpn"):
        return self.tool.image_to_string(img,
                                         lang=lang,
                                         builder=self.builder,
                                         )

    @staticmethod
    def _exec_ocr_dig(img):
        return pytesseract.image_to_string(
            img, config="nobatch digits"
        )

    def get_title(self) -> dict:
        self._crop(self.position_dict["title"])
        img = self.img_box
        img = self._remove_bight(img, c_min=230)
        self.img_box = ImageOps.invert(img.convert(mode="L"))
        res: str = self._exec_ocr(lang="jpn")
        try:
            title_match: str = re.search(r"(?<=「)[^」]+(?=」.+)", res)\
                .group()\
                .strip()
            title: str = re.sub(
                r"(?<=[ぁ-んァ-ヶｱ-ﾝﾞﾟ一-龠])\s+(?=[ぁ-んァ-ヶｱ-ﾝﾞﾟ一-龠])",
                "",
                title_match
            )
            return {"title": title}
        except AttributeError:
            return {"title": ""}

    def _crop_img_box(self, position):
        return self.img_box.crop(position)

    def _remove_bight(self, img, c_min : int = 140):
        pixels = img.load()
        for j in range(img.size[1]):
            for i in range(img.size[0]):
                if (pixels[i, j][0] < c_min or pixels[i, j][1] < c_min or
                        pixels[i, j][0] < c_min):
                    pixels[i, j] = (0, 0, 0)
        return img

    def _remove_color(self, img, c_min : int = 140):
        pixels = img.load()
        for j in range(img.size[1]):
            for i in range(img.size[0]):
                if (pixels[i, j][0] < c_min or pixels[i, j][1] < c_min or
                        pixels[i, j][0] < c_min):
                    pixels[i, j] = (255, 255, 255)
        return img

    def _get_gray_img(self, img, c_min: int = 140):
        img = self._remove_bight(img, c_min)
        return ImageOps.invert(img.convert(mode="L"))

    # TODO: 適切な名前に変更する
    def _get_name_img(self, position: tuple,
                      bi_num: float = 0.7, ci_num: float = 5.0,
                      c_min: int = 140):
        bi = ImageEnhance.Brightness(self._crop_img_box(position))
        bi_img = bi.enhance(bi_num)
        ci = ImageEnhance.Contrast(bi_img)
        ci_img = ci.enhance(ci_num)
        img = self._remove_bight(ci_img)
        return self._get_gray_img(img, c_min=c_min)

    def get_accuracy(self, position, offset, accuracy_num, location_number=None):
        accuracy_position = tuple([
            pos + offset * accuracy_num if n % 2 else pos
            for n, pos in enumerate(position)
        ])
        accuracy_img = self._crop_img_box(accuracy_position)
        ret = self._exec_ocr_dig(accuracy_img).strip()
        return ret

    def _personal_score(self, location_number: int):
        res_dict: dict = {
            "location_number": location_number,
        }
        person_dict: dict = self.position_dict["personal_score"]
        offset = person_dict["offset"] * (location_number - 1)
        base_position: tuple = person_dict["position"]
        position = tuple([
            num + offset if n % 2 == 1 else num
            for n, num in enumerate(base_position, 1)
        ])
        self._crop(position)

        # Name
        name_position : tuple = person_dict["name_position"]
        name_img = self._get_name_img(name_position)
        name: str = self._exec_ocr_img(name_img, lang="jpn")
        res_dict["name"] = name

        # difficulty
        difficulty_position : tuple = person_dict["difficulty_position"]
        dif_img = self._get_name_img(difficulty_position)
        difficulty: str = self._exec_ocr_img(dif_img, lang="eng")
        res_dict["difficulty"] = difficulty

        # combo
        combo_position : tuple = person_dict["combo_position"]
        cmb_img = self._crop_img_box(combo_position)
        cmb_img = self._remove_color(cmb_img, c_min=240)
        cmb_img = self._remove_bight(cmb_img, c_min=254)
        combo: str = self._exec_ocr_dig(cmb_img)
        res_dict["combo"] = combo
        # accuracy
        accuracy_position : tuple = person_dict["accuracy_position"]
        accuracy_offset: int = person_dict["accuracy_offset"]
        for n, accuracy in enumerate(["perfect", "great", "good", "bad", "miss"]):
            accuracy_num = self.get_accuracy(accuracy_position, accuracy_offset, n, location_number)
            res_dict[accuracy] = accuracy_num
        return res_dict

    def get_score(self, location_number: int):
        res_dict: dict = {}
        person_dict: dict = self.position_dict["personal_score"]
        offset = person_dict["offset"] * (location_number - 1)
        base_position: tuple = person_dict["position"]
        position = tuple([
            num + offset if n % 2 == 1 else num
            for n, num in enumerate(base_position, 1)
        ])
        self._crop(position)

        # difficulty
        difficulty_position : tuple = person_dict["difficulty_position"]
        dif_img = self._get_name_img(difficulty_position)
        difficulty: str = self._exec_ocr_img(dif_img, lang="eng")
        res_dict[f"difficulty_{location_number}"] = difficulty

        # score
        self._crop(position)
        score_position : tuple = person_dict["score_position"]
        score_img = self._crop_img_box(score_position).convert(mode="L")
        ci = ImageEnhance.Contrast(score_img)
        score_img = ci.enhance(5.0)
        score: str = self._exec_ocr_img(score_img)
        res_dict[f"score_{location_number}"] = score
        return res_dict
