import os
import cv2
import torch
import time
import onnx, onnxruntime
import torchvision
import numpy as np
import pandas as pd
from PIL import Image





import pdfplumber

from pdf2image import convert_from_path, convert_from_bytes


#pip install pdf2image
#pip install torch torchvision torchaudio
#pip install onnx
#pip install pdfplumber
#pip install onnxruntime


#ONNEX_MODEL_PATH = 'best2.onnx'



import io
import requests



#POPPLER_DIR = r"C:\Program Files\poppler-21.03.0\Library\bin"
POPPLER_DIR = r".\install\poppler\Library\bin"

def pdf_to_images(pdf_url,dpi=200):
    r = requests.get(pdf_url)
    f = io.BytesIO(r.content)

    # https://github.com/Belval/pdf2image
    # use_pdftocairo = True (peformance improvement - look into if no crash?)
    pdf_images = convert_from_bytes(f.read(), dpi=dpi, poppler_path = POPPLER_DIR, thread_count=2)
    return pdf_images





class onnx_detection_handler:

    def __init__(self, model_path='best2.onnx'):
        onnx_model = onnx.load(model_path)
        try:
            onnx.checker.check_model(onnx_model)
        except (Exception, err):
            print('model error:', err)
        else:
            print('model is good to go!')
            self.model_path = model_path
        finally:
            print('model check is over!')
        return

    def init_session(self):
        self.session_options = onnxruntime.SessionOptions()
        self.session_options.enable_profiling = True
        self.session = onnxruntime.InferenceSession(self.model_path)
        self.batch_size = self.session.get_inputs()[0].shape[0]
        self.img_size_h = self.session.get_inputs()[0].shape[2]
        self.img_size_w = self.session.get_inputs()[0].shape[3]
        print ('batch_size: {}, h:{}, w:{}'.format(self.batch_size, self.img_size_h ,self.img_size_w))
        return

    def letterbox(self, img, new_shape=(640, 640), color=(114, 114, 114), scaleup=True, stride=32):
        shape = img.shape[:2]
        if isinstance(new_shape, int):
            new_shape = (new_shape, new_shape)
        # Scale ratio (new / old)
        r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
        if not scaleup:
            r = min(r, 1.0)
        # Compute padding
        ratio = r, r  # width, height ratios
        new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
        dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]  # wh padding
        # Divide padding into 2 sides
        dw /= 2
        dh /= 2
        # Resize
        if shape[::-1] != new_unpad:
            img = cv2.resize(img, new_unpad, interpolation=cv2.INTER_LINEAR)
        top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
        left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
        img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)  # Add border :p
        return img, ratio, (dw, dh)


    def non_max_suppression(self, prediction, conf_thres=0.25, iou_thres=0.45, classes=None, agnostic=True, multi_label=False, labels=(), max_det=300):
        """
        This is a temporary, it should be setup differently at somepoint
        For an explination on non-max sup and IoU: https://github.com/dylanamiller/non_max_suppression
        :)
        """
        # Cut off for number of classes
        nc = prediction.shape[2] - 5
        # Candidates that fall over the confidence threshold
        xc = prediction[..., 4] > conf_thres
        # Checks
        assert 0 <= conf_thres <= 1, f'Invalid Confidence threshold {conf_thres}, 0 - 1'
        assert 0 <= iou_thres <= 1, f'Invalid IoU {iou_thres}, 0 - 1'
        # Settings
        min_wh, max_wh = 2, 4096# (pixels) min and max box width and height
        max_nms = 30000
        time_limit = 10.0 
        redundant = True
        multi_label &= nc > 1  # Multiple labels per box (adds 0.5ms/img)
        t = time.time()
        output = [torch.zeros((0, 6), device=prediction.device)] * prediction.shape[0]
        for xi, x in enumerate(prediction):
            x = x[xc[xi]]  # confidence
            # Cat apriori labels if autolabelling
            if labels and len(labels[xi]):
                l = labels[xi]
                v = torch.zeros((len(l), nc + 5), device=x.device)
                v[:, :4] = l[:, 1:5]  # bbox
                v[:, 4] = 1.0  # confidence
                v[range(len(l)), l[:, 0].long() + 5] = 1.0  # class
                x = torch.cat((x, v), 0)
            # If none remain process next image
            if not x.shape[0]:
                continue
            # Compute conf
            x[:, 5:] *= x[:, 4:5]  # conf = obj_conf * cls_conf
            # Width & Height ---> tl, br
            box = self.xywh2xyxy(x[:, :4])
            # Detections matrix nx6 (xyxy, conf, cls)
            if multi_label:
                i, j = (x[:, 5:] > conf_thres).nonzero(as_tuple=False).T
                x = torch.cat((box[i], x[i, j + 5, None], j[:, None].float()), 1)
            else:  # best class only
                conf, j = x[:, 5:].max(1, keepdim=True)
                x = torch.cat((box, conf, j.float()), 1)[conf.view(-1) > conf_thres]
            # Filter by class
            if classes is not None:
                x = x[(x[:, 5:6] == torch.tensor(classes, device=x.device)).any(1)]
            # Check shape
            n = x.shape[0]  # Number of boxes
            if not n:  # No boxes
                continue
            elif n > max_nms:  # Excess boxes
                x = x[x[:, 4].argsort(descending=True)[:max_nms]]  # Sort by confidence
            # Batched NMS
            c = x[:, 5:6] * (0 if agnostic else max_wh)
            boxes, scores = x[:, :4] + c, x[:, 4]
            i = torchvision.ops.nms(boxes, scores, iou_thres)
            if i.shape[0] > max_det:
                i = i[:max_det]
            output[xi] = x[i]
            if (time.time() - t) > time_limit:
                break  # Time limit exceeded
        return output

    def xywh2xyxy(self, x):
        # Convert boxes from [x, y, w, h] to [x1, y1, x2, y2] top-left, bottom-right
        y = x.clone() if isinstance(x, torch.Tensor) else np.copy(x)
        y[:, 0] = x[:, 0] - x[:, 2] / 2  # top left x
        y[:, 1] = x[:, 1] - x[:, 3] / 2  # top left y
        y[:, 2] = x[:, 0] + x[:, 2] / 2  # bottom right x
        y[:, 3] = x[:, 1] + x[:, 3] / 2  # bottom right y
        return y


    def clip_coords(self, boxes, img_shape):
        # Clip bounding xyxy bounding boxes to image shape (height, width)
        # xy1
        boxes[:, 0].clamp_(0, img_shape[1])
        boxes[:, 1].clamp_(0, img_shape[0])
        # xy2
        boxes[:, 2].clamp_(0, img_shape[1])
        boxes[:, 3].clamp_(0, img_shape[0])



    def scale_coords(self, img1_shape, coords, img0_shape, ratio_pad=None):
        """
        Needs fixin up so it doesent need to cringe abt potential differences with tensors, lists, ints, floats and other assorted nosense
        (:
        """
        # Rescale coords (xyxy) img1_shape ---> img0_shape
        if ratio_pad is None:  # Calculate from img0_shape
            # gain  = old / new
            gain = min(img1_shape[0] / img0_shape[0], img1_shape[1] / img0_shape[1])
            # wh padding
            pad = (img1_shape[1] - img0_shape[1] * gain) / 2, (img1_shape[0] - img0_shape[0] * gain) / 2
        else:
            gain = ratio_pad[0][0]
            pad = ratio_pad[1]
        coords[:, [0, 2]] -= pad[0]  # x padding
        coords[:, [1, 3]] -= pad[1]  # y padding
        coords[:, :4] /= gain
        self.clip_coords(coords, img0_shape)
        return coords

    def add_box(self, x, im, color=(128, 128, 128), label=None, line_thickness=3):
        c1, c2 = (int(x[0]), int(x[1])), (int(x[2]), int(x[3]))
        cv2.rectangle(im, c1, c2, color, thickness=line_thickness, lineType=cv2.LINE_AA)
        return

    def run_image_detection(self, img, imgsz=640, stride=32):
        cv2_img = img.copy()
        cv2_img = self.letterbox(cv2_img, imgsz, stride)[0] 
        cv2_img = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
        # ascontiguousarray == combine all memory into same memory block for the sake of pointers
        cv2_img = np.ascontiguousarray(cv2_img)
        image_np = Image.fromarray(cv2_img)
        resized =  image_np.resize((self.img_size_w, self.img_size_h))
        img_in = np.transpose(resized, (2, 0, 1)).astype(np.float32)
        img_in = np.expand_dims(img_in, axis=0)
        img_in /= 255.0
        input_name = self.session.get_inputs()[0].name
        outputs = self.session.run(None, {input_name: img_in})
        filterd_predictions = self.non_max_suppression(torch.tensor(outputs[0]), conf_thres = 0.3, iou_thres = 0.45)# conf_thres = 0.25, iou_thres = 0.45
        return filterd_predictions

    def get_detection_boxes(self, img, predictions, image_path=None):
        xyxy = []
        table_areas = []
        new_img = img.copy()
        for i, det in enumerate(predictions):
            det[:, :4] = self.scale_coords([self.img_size_h, self.img_size_w], det[:, :4], new_img.shape).round()
            
            for *xyxy, conf, cls in reversed(det):
                # Integer class
                c = int(cls)
                # Classes list
                names = ['table']
                label = '{} {}'.format(names[c], conf)
                self.add_box(xyxy, new_img, color=[0,0,255], line_thickness=2)
                table_area = {'bbox': [int(xyxy[0]), int(xyxy[1]), int(xyxy[2]), int(xyxy[3])], 'conf': conf, 'class': names[c]}
                table_areas.append(table_area)
        # --
        if image_path:
            img_name = image_path.split('\\')[-1]
            path_prefix = image_path.split('\\')[0]
            print('{}/det-{}'.format(path_prefix, img_name))
            cv2.imwrite('{}/det-{}'.format(path_prefix, img_name), new_img)
            #print('Saved: nn_data/det-{}'.format(img_name))
        # --
        return table_areas, new_img
    # --



def test_run_images():
    onnx_test = onnx_detection_handler()
    onnx_test.init_session()

    for image_name in os.listdir('nn_data'):
        image_path = os.path.join('nn_data', image_name)
        img = cv2.imread(image_path)
        inference_tensors = onnx_test.run_image_detection(img)
        onnx_test.get_detection_boxes(img, inference_tensors, image_path)
    return
# --


def run_pdf_table_detection(pdf_url, save_images=False):
    """{'table_areas': table_areas, 'page_number': idx},
    table_areas: {'bbox': [int(xyxy[0]), int(xyxy[1]), int(xyxy[2]), int(xyxy[3])], 'conf': conf, 'class': names[c]}
    """
    pdf_images = pdf_to_images(pdf_url)

    #print('PDF URL: ', pdf_url)

    onnx_test = onnx_detection_handler()
    onnx_test.init_session()

    page_detections = []

    for idx, pil_img in enumerate(pdf_images):
        try:
            #print(idx)
            image_path = None
            if save_images:
                image_path = 'nn_data\\{}-img.jpg'.format(str(idx))
            cv2_img = np.array(pil_img)
            inference_tensors = onnx_test.run_image_detection(cv2_img)
            table_areas, new_img = onnx_test.get_detection_boxes(cv2_img, inference_tensors, image_path)
            if len(table_areas) > 0:
                page_det = {'table_areas': table_areas, 'page_number': idx}#- 1
                #print(idx)
                page_detections.append(page_det)
        except Exception as e:
            print(e)
    # --

    return page_detections
# --

#test_url = "https://www.fidelity.com.au/funds/fidelity-australian-equities-fund/related-documents/product-disclosure-statement/"
#run_pdf_table_detection(test_url, True)














