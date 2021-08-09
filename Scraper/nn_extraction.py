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

#from pdf2image import convert_from_path, convert_from_bytes
#pip3 install torch torchvision torchaudio
#pip install onnx
#pip install pdfplumber
#pip install onnxruntime


#ONNEX_MODEL_PATH = 'best2.onnx'



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
        assert 0 <= conf_thres <= 1, f'Invalid Confidence threshold {conf_thres}, valid values are between 0.0 and 1.0'
        assert 0 <= iou_thres <= 1, f'Invalid IoU {iou_thres}, valid values are between 0.0 and 1.0'
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
        filterd_predictions = self.non_max_suppression(torch.tensor(outputs[0]), conf_thres = 0.1, iou_thres = 0.45)
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
            cv2.imwrite('{}/det-{}'.format(path_prefix, img_name), new_img)
            #print('Saved: data/det-{}'.format(img_name))
        # --
        return table_areas, new_img
    # --




onnx_test = onnx_detection_handler()
onnx_test.init_session()

for image_name in os.listdir('data'):
    image_path = os.path.join('data', image_name)
    img = cv2.imread(image_path)
    inference_tensors = onnx_test.run_image_detection(img)
    onnx_test.get_detection_boxes(img, inference_tensors, image_path)









'''
table_areas = []

for image_name in os.listdir(source):
    image_path = os.path.join(source, image_name)
    cv2_img = cv2.imread(image_path)
    cv2_img = letterbox(cv2_img, imgsz, stride)[0] 
    cv2_img = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
    # ascontiguousarray == combine all memory into same memory block for the sake of pointers
    cv2_img = np.ascontiguousarray(cv2_img)
    image_np = Image.fromarray(cv2_img)
    resized =  image_np.resize((img_size_w, img_size_h))
    img_in = np.transpose(resized, (2, 0, 1)).astype(np.float32)
    img_in = np.expand_dims(img_in, axis=0)
    img_in /= 255.0
    input_name = session.get_inputs()[0].name
    outputs = session.run(None, {input_name: img_in})
    filterd_predictions = non_max_suppression(torch.tensor(outputs[0]), conf_thres = 0.1, iou_thres = 0.45)
    img_name = image_path.split('\\')[-1]
    

    xyxy = []
    im0 = cv2.imread(image_path)
    for i, det in enumerate(filterd_predictions):
        #im0 = cv2.imread(image_path)
        print(det[:, :4])
        det[:, :4] = scale_coords([img_size_h, img_size_w], det[:, :4], im0.shape).round()
        
        max_conf = 0.01
        for *xyxy, conf, cls in reversed(det):
            if conf > max_conf:
                max_conf = conf
        # --
        
        for *xyxy, conf, cls in reversed(det):
            # Integer class
            c = int(cls)
            # Classes list
            names = ['table']
            label = '{} {}'.format(names[c], conf)
            #img_name = image_path.split('/')[-1]
            img_name = image_path.split('\\')[-1]
            plot_one_box(xyxy, im0, color=[0,0,255], line_thickness=3)
            if max_conf > 0.1 and conf >= max_conf - 0.05:
                table_areas.append([int(xyxy[0]), int(xyxy[1]), int(xyxy[2]), int(xyxy[3])])
    cv2.imwrite('data/det-{}'.format(img_name), im0)
    print('data/det-{}'.format(img_name))
    out_test_img = im0
# --
'''






#onnx_model = onnx.load(ONNEX_MODEL_PATH)


'''
try:
    onnx.checker.check_model(onnx_model)
except (Exception, err):
    print('model error:', err)
else:
    print('model is good to go!')
finally:
    print('model check is over!')

session_options = onnxruntime.SessionOptions()
session_options.enable_profiling = True
session = onnxruntime.InferenceSession(ONNEX_MODEL_PATH)
batch_size = session.get_inputs()[0].shape[0]
img_size_h = session.get_inputs()[0].shape[2]
img_size_w = session.get_inputs()[0].shape[3]
print ('batch_size: {}, h:{}, w:{}'.format(batch_size, img_size_h ,img_size_w))

source = 'data'
imgsz = 640
stride = 32

'''








'''
# ------------------------------

def letterbox(img, new_shape=(640, 640), color=(114, 114, 114), auto=False, scaleFill=False, scaleup=True, stride=32):
    # Resize and pad image while meeting stride-multiple constraints
    shape = img.shape[:2]  # current shape [height, width]
    if isinstance(new_shape, int):
        new_shape = (new_shape, new_shape)
    # Scale ratio (new / old)
    r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
    if not scaleup:  # only scale down, do not scale up (for better test mAP)
        r = min(r, 1.0)
    # Compute padding
    ratio = r, r  # width, height ratios
    new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
    dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]  # wh padding
    if auto:  # minimum rectangle
        dw, dh = np.mod(dw, stride), np.mod(dh, stride)  # wh padding
    elif scaleFill:  # stretch
        dw, dh = 0.0, 0.0
        new_unpad = (new_shape[1], new_shape[0])
        ratio = new_shape[1] / shape[1], new_shape[0] / shape[0]  # width, height ratios
    dw /= 2  # divide padding into 2 sides
    dh /= 2
    if shape[::-1] != new_unpad:  # resize
        img = cv2.resize(img, new_unpad, interpolation=cv2.INTER_LINEAR)
    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
    img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)  # add border
    return img, ratio, (dw, dh)


def non_max_suppression(prediction, conf_thres=0.25, iou_thres=0.45, classes=None, agnostic=True, multi_label=False,
                        labels=(), max_det=300):
    """Runs Non-Maximum Suppression (NMS) on inference results
    Returns:
         list of detections, on (n,6) tensor per image [xyxy, conf, cls]
    """
    # Cut off for number of classes
    nc = prediction.shape[2] - 5
    # Candidates that fall over the confidence threshold
    xc = prediction[..., 4] > conf_thres
    # Checks
    assert 0 <= conf_thres <= 1, f'Invalid Confidence threshold {conf_thres}, valid values are between 0.0 and 1.0'
    assert 0 <= iou_thres <= 1, f'Invalid IoU {iou_thres}, valid values are between 0.0 and 1.0'
    # Settings
    min_wh, max_wh = 2, 4096  # (pixels) min and max box width and height
    max_nms = 30000  # Maximum number of boxes into torchvision.ops.nms()
    time_limit = 10.0  # Seconds to quit after
    redundant = True  # Require redundant detections
    multi_label &= nc > 1  # Multiple labels per box (adds 0.5ms/img)
    t = time.time()
    output = [torch.zeros((0, 6), device=prediction.device)] * prediction.shape[0]
    for xi, x in enumerate(prediction):  # image index, image inference
        # Apply constraints
        # x[((x[..., 2:4] < min_wh) | (x[..., 2:4] > max_wh)).any(1), 4] = 0  # width-height
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
        # Box (center x, center y, width, height) to (x1, y1, x2, y2)
        box = xywh2xyxy(x[:, :4])
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
            print(f'WARNING: NMS time limit {time_limit}s exceeded')
            break  # Time limit exceeded
    return output

def xywh2xyxy(x):
    # Convert nx4 boxes from [x, y, w, h] to [x1, y1, x2, y2] where xy1=top-left, xy2=bottom-right
    y = x.clone() if isinstance(x, torch.Tensor) else np.copy(x)
    y[:, 0] = x[:, 0] - x[:, 2] / 2  # top left x
    y[:, 1] = x[:, 1] - x[:, 3] / 2  # top left y
    y[:, 2] = x[:, 0] + x[:, 2] / 2  # bottom right x
    y[:, 3] = x[:, 1] + x[:, 3] / 2  # bottom right y
    return y


def clip_coords(boxes, img_shape):
    # Clip bounding xyxy bounding boxes to image shape (height, width)
    boxes[:, 0].clamp_(0, img_shape[1])  # x1
    boxes[:, 1].clamp_(0, img_shape[0])  # y1
    boxes[:, 2].clamp_(0, img_shape[1])  # x2
    boxes[:, 3].clamp_(0, img_shape[0])  # y2



def scale_coords(img1_shape, coords, img0_shape, ratio_pad=None):
    # Rescale coords (xyxy) from img1_shape to img0_shape
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
    clip_coords(coords, img0_shape)
    return coords


def plot_one_box(x, im, color=(128, 128, 128), label=None, line_thickness=3):
    # Plots one bounding box on image 'im' using OpenCV
    assert im.data.contiguous, 'Image not contiguous. Apply np.ascontiguousarray(im) to plot_on_box() input image.'
    # Line/font thickness
    tl = line_thickness or round(0.002 * (im.shape[0] + im.shape[1]) / 2) + 1
    c1, c2 = (int(x[0]), int(x[1])), (int(x[2]), int(x[3]))
    cv2.rectangle(im, c1, c2, color, thickness=tl, lineType=cv2.LINE_AA)
    if label:
        tf = max(tl - 1, 1)  # font thickness
        t_size = cv2.getTextSize(label, 0, fontScale=tl / 3, thickness=tf)[0]
        c2 = c1[0] + t_size[0], c1[1] - t_size[1] - 3
        cv2.rectangle(im, c1, c2, color, -1, cv2.LINE_AA)  # filled
        cv2.putText(im, label, (c1[0], c1[1] - 2), 0, tl / 3, [225, 255, 255], thickness=tf, lineType=cv2.LINE_AA)

'''














