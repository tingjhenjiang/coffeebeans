#https://labelstud.io/tutorials/dummy_model.html
#https://github.com/heartexlabs/label-studio/blob/master/docs/source/tutorials/object-detector.md#Installation
#https://labelstud.io/guide/ml.html
#https://github.com/heartexlabs/label-studio-ml-backend#Create_your_own_ML_backend


from label_studio_ml.model import LabelStudioMLBase
import os, json, cv2
import importlib.util
#import tensorflow as tf

overall_workingdir = '/opt/mnt/code-391ff5ac-6576-460f-ba4d-7e03433c68b6/Users/Jerry.Hsieh/coffeebeans'
overall_darknetdir = os.path.join(overall_workingdir,'darknet')
overall_traindataSrcPathBase = os.path.join(overall_darknetdir,'data')
overall_traindataSrcPathBaseDisplayed = '/opt/mnt/code-391ff5ac-6576-460f-ba4d-7e03433c68b6/Users/Jerry.Hsieh/coffeebeans/darknet/data'
os.environ['DARKNET_PATH'] = overall_darknetdir

spec = importlib.util.spec_from_file_location("commonsettings", os.path.join(overall_workingdir,'commonsettings.py'))
commonsettings = importlib.util.module_from_spec(spec)        
spec.loader.exec_module(commonsettings)

spec2 = importlib.util.spec_from_file_location("darknet", os.path.join(overall_darknetdir,'darknet.py'))
darknet = importlib.util.module_from_spec(spec2)        
spec2.loader.exec_module(darknet)

specificProjName = 'purebeans_tiny_filtered_w608h608_20210609' #best in pure positioning'purebeans_tiny_filtered_w608h608_20210609'
#purebeans_yolo4_w544h544_filtered_20210613
#3classbeans_yolo4tiny_filtered_w512h512_20210618
clsModelSourceFile = '/opt/mnt/code-391ff5ac-6576-460f-ba4d-7e03433c68b6/Users/tj/ownbeansclassify-badcondense-DenseNet121-normalized-circleloss-norefreshtflearnweights-sampleweights-lrschedule-leakyrelu-.epoch059-val_loss5.80211-val_f1_score0.89-val_AUC0.97-val_recall0.90-val_precision0.92-val_binary_accuracy0.94.hdf5'

#tf.keras.models.load_model(conti_model, custom_objects={'CircleLoss':preferredLoss})

class DummyModel(LabelStudioMLBase):

    def __init__(self, **kwargs):
        # don't forget to call base class constructor
        super(DummyModel, self).__init__(**kwargs)
    
        # you can preinitialize variables with keys needed to extract info from tasks and completions and form predictions
        print( "self.parsed_label_config.items() is {}".format(self.parsed_label_config.items()) )
        from_name, schema = list(self.parsed_label_config.items())[0]
        self.from_name = from_name
        self.to_name = schema['to_name'][0]
        self.labels = schema['labels']
        self.argThresh = 0.25
        
        self.baseConfigFilenames = commonsettings.generatePaths(targetOssep=os.sep, traindataSrcPathBase = overall_traindataSrcPathBase, traindataSrcPathBaseDisplayed = overall_traindataSrcPathBaseDisplayed, specificProjName=specificProjName)
        self.load_yolo_model(self.baseConfigFilenames)

    def load_yolo_model(self, baseConfigFilenames):
        self.network, self.class_names, self.class_colors = darknet.load_network(
                self.baseConfigFilenames['modelCfgFileNameInTesting']['orig'],
                self.baseConfigFilenames['objDataFileName']['orig'],
                self.baseConfigFilenames['backupBestWeightFileName']['orig'],
                batch_size=64
        )
        print("self.class_names is {} self.class_colors is {}".format(self.class_names, self.class_colors))
        
    def image_detection(self, image_path, network, class_names, class_colors, thresh):
        # Darknet doesn't accept numpy images.
        # Create one with image we reuse for each detect
        width = darknet.network_width(network)
        height = darknet.network_height(network)
        darknet_image = darknet.make_image(width, height, 3)

        isfile = False if str(type(image_path)).find("ndarray")!=-1 else True
        image = cv2.imread(image_path) if isfile else image_path
        origShape = image.shape

        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_resized = cv2.resize(image_rgb, (width, height),
                                   interpolation=cv2.INTER_LINEAR)

        darknet.copy_image_from_bytes(darknet_image, image_resized.tobytes())
        detections = darknet.detect_image(network, class_names, darknet_image, thresh=thresh)
        #label, confidence, bbox(x_center, y_center, w, h)
        scaleXfactor = 1/width*origShape[1]
        scaleYfactor = 1/height*origShape[0]
        detectionsAdjusted = []
        for detection in detections:
            label, confidence, bbox = detection
            x_center, y_center, w, h = bbox
            left = (int(round(x_center - (w / 2)))/width)*100
            top = (int(round(y_center - (h / 2)))/height)*100
            w = w/width*100
            h = h/height*100
            detectionsAdjusted.append( {'label':label, 'confidence':confidence, 'bbox':[left,top,w,h] } )
        returnDict = {'detections':detections, 'detectionsAdjusted':detectionsAdjusted, 'shape':(width, height), 'origshape':origShape}
        darknet.free_image(darknet_image)
        if False:
            image = darknet.draw_boxes(detections, image_resized, class_colors)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            returnDict['image'] = image
        return returnDict
        
    def predict(self, tasks, **kwargs):
        print("Incoming tasks are {}".format(tasks))
        """This is where inference happens: model returns the list of predictions based on input list of tasks"""
        results = []

        for task_key,task in enumerate(tasks):
            taskid = task['id']
            sendInImg = task['data']['image'] #random.choice(baseConfigFilenames['allTakenImages']['display'])
            print("Incoming taskid is {} and image is {}".format(taskid,sendInImg))
            sendInImg = os.path.basename(task['data']['image'])
            sendInImg = [f for f in self.baseConfigFilenames['allTakenImages']['orig'] if f.find(sendInImg)!=-1][0]
            image_name = sendInImg
            image = cv2.imread(image_name)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            detectionsResult = self.image_detection(
                        image, self.network, self.class_names, self.class_colors, self.argThresh
                        )
            rectanglePredResults = detectionsResult['detectionsAdjusted']
            rectangles = []
            for rectangle_key,rectanglePredResult in enumerate(rectanglePredResults):
                toAppendRectangleDict = {
                    'original_width': detectionsResult['origshape'][0],
                    'original_height': detectionsResult['origshape'][1],
                    'image_rotation': 0,
                    'value': {
                        'x': 0 if rectanglePredResult['bbox'][0]<0 else rectanglePredResult['bbox'][0],
                        'y': 0 if rectanglePredResult['bbox'][1]<0 else rectanglePredResult['bbox'][1],
                        'rotation': 0,
                        'rectanglelabels': [rectanglePredResult['label']], #['UnlabelledBean'], #
                        'confidence': rectanglePredResult['confidence']
                    },
                    #"meta": {
                    #    "text": [
                    #        "confidence 25"
                    #    ]
                    #},
                    'id': 'taskid{}rectangle{}'.format(taskid,rectangle_key),
                    'from_name': self.from_name,
                    'to_name': self.to_name,
                    'type': 'rectanglelabels'
                }
                toAppendRectangleDict['value']['width'] = rectanglePredResult['bbox'][2] if (toAppendRectangleDict['value']['x']+rectanglePredResult['bbox'][2])<=100 else 100-toAppendRectangleDict['value']['x']
                toAppendRectangleDict['value']['height'] = rectanglePredResult['bbox'][3] if (toAppendRectangleDict['value']['y']+rectanglePredResult['bbox'][3])<=100 else 100-toAppendRectangleDict['value']['y']
                rectangles.append(toAppendRectangleDict)
            results.append({
                'result': rectangles
            })
        return results

    def fit(self, completions, **kwargs):
        """This is where training happens: train your model given list of completions, then returns dict with created links and resources"""
        return {'path/to/created/model': 'my/model.bin'}