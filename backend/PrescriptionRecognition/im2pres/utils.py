from __future__ import print_function

import time, re
from PIL import Image

import cv2
from enum import Enum

def crop_image(img, box, paddings=(1., 1., 5., 5.)):
    # paddings is in float
    
    l, t = box[0]
    r, bt = box[1]

    t_min = min(box[0][1], box[1][1], box[2][1], box[3][1])
    t_max = max(box[0][1], box[1][1], box[2][1], box[3][1])
    # them padding vao day (pixel)
    (pl, pr, pt, pb) = paddings

    return img.crop((l-pl, t_min-pt, r+pr, t_max+pb))    
    
def simplify_bboxes(boxes):
    #return boxes[:, [0,2]]
    return boxes

def craft_time(craft, img_path):
    start_time = time.time()
    content = craft.detect_text(img_path)
    running_time = time.time()-start_time
    return running_time, content['boxes'] # content['text_crop_paths']

def vietocr_time(vietocr, craft, img_path, use_open_cv=False):

    img = None 

    if use_open_cv:
        img = ImagePreprocessingBuilder(img_path).to_pillow().build()
    else:
        img = Image.open(img_path)

    det_time, img_boxes = craft_time(craft, img_path)

    start_time = time.time()

    contents = []
    for box in simplify_bboxes(img_boxes):
        new_img = crop_image(img, box)
        w, h = new_img.size
        if w != 0 and h != 0:
            contents.append({'line': vietocr.predict(new_img), 'box': box})
            
    reg_time = time.time()-start_time

    return [det_time, reg_time], contents

def cleanName(name):
    #cần kiểm tra xem hàm này đã xoá các kí tự tiếng việt chưa ví dụ ê, ư, ó, ò, é nếu chưa cần gọi thêm hàm depunc
    dePunc(name) #thay thế các kí tự tiếng việt thành kí tự tiếng a tương ứng
    # print(name)
    string = re.sub(r'[^a-z0-9]', ' ', name.lower()) 

    string = [x.strip() for x in string.split() if len(x) > 2]
   
    return  ' '.join(string)

def dePunc(string):
        tmp = ''
        for text in string:
            if text in 'aáàảãạăắằẳẵặâấầẩẫậ':
                tmp += 'a'
            elif text in 'eéèẻẽẹêếềểễệ':
                tmp += 'e'
            elif text in 'iíìỉĩị':
                tmp += 'i'
            elif text in 'IÍÌỈĨỊ':
                tmp += 'I'
            elif text in 'yýỳỷỹỵ':
                tmp += 'y'
            elif text in 'AÁÀẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬ':
                tmp += 'A'
            elif text in 'EÉÈẺẼẸÊẾỀỂỄỆ':
                tmp += 'E'
            elif text in 'OÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢ':
                tmp += 'O'
            elif text in 'oóòỏõọôốồổỗộơớờởỡợ':
                tmp += 'o'
            elif text in 'UÚÙỦŨỤƯỨỪỬỮỰ':
                tmp += 'U'
            elif text in 'uúùủũụưứừửữự':
                tmp += 'u'
            elif text in 'YÝỲỶỸỴ':
                tmp += 'Y'
            elif text in 'dđ':
                tmp += 'd'
            elif text in 'DĐ':
                tmp += 'D'
            elif text in '(':
                tmp += ' ('
            elif text in ')':
                tmp +=  ') '
            elif text in '/':
                tmp += ' / '
            else:
                tmp += text
        # if tmp[-1] == ' ':
        #     tmp = tmp[:-1]
        return tmp

class BinThreshold(Enum):
    # https://docs.opencv.org/4.x/d7/d4d/tutorial_py_thresholding.html
    ADAPTIVE_THRESH_MEAN_C = "ADAPTIVE_THRESH_MEAN_C"
    ADAPTIVE_THRESH_GAUSSIAN_C = "ADAPTIVE_THRESH_GAUSSIAN_C"
    THRESH_OTSU = "THRESH_OTSU"
    GAUSSIAN_BLUR_THRESH_OTSU = "GAUSSIAN_BLUR_THRESH_OTSU"
    pass

class ImagePreprocessingBuilder():
    def __init__(self, image_path="imgs/don11.jpg"):
        self.image_path : str = image_path
        self.grayscale : bool = False
        self.binarization_metric : BinThreshold = None
        self.bin_kwargs = None
        self.resize_kwargs = None
        self.denoise_kwargs = None
        self.pil_format = False

    def to_grayscale(self):
        self.grayscale = True
        return self
    
    def set_binarization_metric(self, metric: BinThreshold, **kwargs):
        self.binarization_metric = metric
        self.bin_kwargs = kwargs
        return self

    def resize_to(self, **kwargs):
        assert ('width' in kwargs) ^ ('height' in kwargs), "Please supply only width or height to resize"
        if 'width' in kwargs:
            assert kwargs['width'] > 0, "Make sure width greater than zero" 
        if 'height' in kwargs:
            assert kwargs['height'] > 0, "Make sure width greater than zero" 

        self.resize_kwargs = kwargs

        return self
    
    def to_pillow(self):
        self.pil_format = True
        return self

    def _to_pillow_format(self, img):
        im_pil : Image 
        if self.grayscale:
            im_pil = Image.fromarray(img)
        else:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            im_pil = Image.fromarray(img)

        return im_pil

    def _resize(self, img):
        scale_percent = 1

        if 'width' in self.resize_kwargs:
            scale_percent = self.resize_kwargs['width'] / img.shape[1]
        
        if 'height' in self.resize_kwargs:
            scale_percent = self.resize_kwargs['height'] / img.shape[0] 

        width = int(img.shape[1] * scale_percent)
        height = int(img.shape[0] * scale_percent)
        dim = (width, height)
        
        # resize image
        resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)

        return resized

    def denoise(self, **kwargs):
        self.denoise_kwargs = kwargs
        return self

    def build(self):
        img = cv2.imread(self.image_path)

        if self.resize_kwargs:
            img = self._resize(img)

        if self.grayscale:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        if self.binarization_metric:
            if self.binarization_metric == BinThreshold.THRESH_OTSU:
                _, img = cv2.threshold(img,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
            
            if self.binarization_metric == BinThreshold.GAUSSIAN_BLUR_THRESH_OTSU:
                blur = cv2.GaussianBlur(img,(5,5),0)
                _, img = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

            if self.binarization_metric == BinThreshold.ADAPTIVE_THRESH_MEAN_C:
                img = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY, **self.bin_kwargs)
            
            if self.binarization_metric == BinThreshold.ADAPTIVE_THRESH_GAUSSIAN_C:
                img = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY, **self.bin_kwargs)
        
        if self.denoise_kwargs:
            if self.grayscale:
                # h=50,templateWindowSize = 13,searchWindowSize = 31
                img = cv2.fastNlMeansDenoising(img,None,**self.denoise_kwargs)
            else:
                # h=10,hColor=10,templateWindowSize=7,searchWindowSize=21
                img = cv2.fastNlMeansDenoisingColored(img, None, **self.denoise_kwargs)

        if self.pil_format:
            img = self._to_pillow_format(img)
                    
        return img