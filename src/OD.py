'''
Created on 26-Feb-2020

@author: OGGY
'''
import cv2 as cv
import numpy as np

confThreshold = 0.25
nmsThreshold = 0.40
inpWidth=416
inpHeight=416

# Get the names of the output layers
def getOutputsNames(net):
    # Get the names of all the layers in the network
    layersNames = net.getLayerNames()
    # Get the names of the output layers, i.e. the layers with unconnected outputs
    return [layersNames[i[0] - 1] for i in net.getUnconnectedOutLayers()]

# Remove the bounding boxes with low confidence using non-maxima suppression
def postprocess(frame, outs):
    frameHeight = frame.shape[0]
    frameWidth = frame.shape[1]

    # Scan through all the bounding boxes output from the network and keep only the
    # ones with high confidence scores. Assign the box's class label as the class with the highest score.
    classIds = []
    confidences = []
    boxes = []
    for out in outs:
        for detection in out:
            scores = detection[5:]
            classId = np.argmax(scores)
            confidence = scores[classId]
            if confidence > confThreshold:
                center_x = int(detection[0] * frameWidth)
                center_y = int(detection[1] * frameHeight)
                width = int(detection[2] * frameWidth)
                height = int(detection[3] * frameHeight)
                left = int(center_x - width / 2)
                top = int(center_y - height / 2)
                classIds.append(classId)
                confidences.append(float(confidence))
                boxes.append([left, top, width, height])

    # Perform non maximum suppression to eliminate redundant overlapping boxes with
    # lower confidences.
    indices = cv.dnn.NMSBoxes(boxes, confidences, confThreshold, nmsThreshold)
    for i in indices:
        i = i[0]
        box = boxes[i]
        left = box[0]
        top = box[1]
        width = box[2]
        height = box[3]
        
        drawPred(classIds[i], confidences[i], left, top, left + width, top + height)

# Draw the predicted bounding box
def drawPred(classId, conf, left, top, right, bottom):
    # Draw a bounding box.
    cv.rectangle(frame, (left, top), (right, bottom), (0, 0, 255))
    
    label = '%.2f' % conf
        
    # Get the label for the class name and its confidence
    if classes:
        assert(classId < len(classes))
        label = '%s:%s' % (classes[classId], label)

    #Display the label at the top of the bounding box
    labelSize, baseLine = cv.getTextSize(label, cv.FONT_HERSHEY_SIMPLEX, 0.5, 1)
    top = max(top, labelSize[1])
    cv.putText(frame, label, (left, top), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255))

classesFile ="coco.names"
classes=None

with open(classesFile,'rt') as f:
    classes=f.read().rstrip('\n').split('\n')
    
modelConf='yolov3.cfg'
modelWeights = 'yolov3.weights'
#modelWeights = 'yolov3-tiny.weights'

net = cv.dnn.readNetFromDarknet(modelConf,modelWeights)
net.setPreferableBackend(cv.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv.dnn.DNN_TARGET_CPU) #OPENCL for GPU 

winName = 'DL OD with OpenCV'
cv.namedWindow(winName,cv.WINDOW_NORMAL)
cv.resizeWindow(winName,1000,1000)

cap=cv.VideoCapture(0)
#for external camera
#cap=cv.VideoCapture(0)
while cv.waitKey(1) < 0:
    hasFrame, frame = cap.read()
    
    blob = cv.dnn.blobFromImage(frame,1/255,(inpWidth,inpHeight),[0,0,0],1,crop=False)
    net.setInput(blob)
    
    outs = net.forward(getOutputsNames(net))
    
    postprocess(frame, outs)
    
    cv.imshow(winName, frame)
    
    
    
    
    
    
