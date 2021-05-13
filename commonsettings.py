import json, os, re, math

def imShow(path, cvtColor=False, resize=False):
    import cv2
    import matplotlib.pyplot as plt
    isfile = False if str(type(path)).find("ndarray")!=-1 else True
    image = cv2.imread(path) if isfile else path
    height, width = image.shape[:2]
    resized_image = cv2.resize(image,(3*width, 3*height), interpolation = cv2.INTER_CUBIC) if resize else image
    fig = plt.gcf()
    fig.set_size_inches(18, 10)
    plt.axis("off")
    if cvtColor:
        plt.imshow(cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB))
    else:
        plt.imshow(resized_image)
    plt.show()

def getLabelStudioData():
    import requests
    session_requests = requests.session()
    session_requests.headers.update({'Authorization': 'Token 21def27b3c847debd02963eb70a0db33b6375991'})
    r = session_requests.get('http://192.168.10.200:8081/api/projects/2/tasks?page_size=9999&page=1')
    rawSrcAnnotations = r.json()
    return rawSrcAnnotations

def generatePaths(targetOssep="/", traindataSrcPathBase = '/opt/mnt/code-391ff5ac-6576-460f-ba4d-7e03433c68b6/Users/Jerry.Hsieh/coffeebeans/darknet/data', traindataSrcPathBaseDisplayed = '/opt/mnt/code-391ff5ac-6576-460f-ba4d-7e03433c68b6/Users/Jerry.Hsieh/coffeebeans/darknet/data', specificProjName = 'purebeans_tiny_filtered_w608h608_20210609'):
    #traindataSrcPathBase = os.path.join(os.sep, "mnt", "f", "coffeebeans", "data") #WSL
    #traindataSrcPathBase = "/content" #google colab
    #traindataSrcPathBase = os.path.join("F:", os.sep, "coffeebeans", "data") #Windows
    traindataSrcPathBase = traindataSrcPathBase if traindataSrcPathBase !='' else os.path.join(os.getcwd(), 'darknet', 'data') #this is real file path
    #change traindataSrcPathBaseDisplayed for transfer platform
    traindataSrcPathImgsBase = os.path.join(traindataSrcPathBase, 'obj')
    traindataSrcPathImgsBaseDisplayed = os.path.join(traindataSrcPathBaseDisplayed, 'obj').replace(os.sep, targetOssep)
    specificProjName = 'purebeans_tiny_notfiltered_20210529' if specificProjName=='' else specificProjName
    baseConfigFilenames = {
        'meaningJsonFileName':{
            'base': ['backup',specificProjName,'labelMeaning.json'],
        },
        'objNamesFileName':{
            'base': ['backup',specificProjName,'obj.names'],
        },
        'objDataFileName':{
            'base': ['backup',specificProjName,'obj.data'],
        },
        'modelCfgFileName':{
            'base': ['backup',specificProjName,'yolov4-tiny-custom.cfg'],
        },
        'modelCfgFileNameInTesting':{
            'base': ['backup',specificProjName,'yolov4-tiny-custom-test.cfg'],
        },
        'trainListFileName':{
            'base': ['backup',specificProjName,'Train.txt'],
        },
        'validationListFileName':{
            'base': ['backup',specificProjName,'Validation.txt'],
        },
        'trainingRecordsFileName':{
            'base': ['backup',specificProjName,'trainingRecords.txt'],
        },
        'backupFileName':{
            'base': ['backup',specificProjName],
        },
        'pretrainedWeightFileName':{
            'base': ['yolov4-tiny.conv.29'],
        },
        'backupLastWeightFileName':{
            'base': ['backup',specificProjName,'yolov4-tiny-obj_last.weights'],
        },
        'backupBestWeightFileName':{
            'base': ['backup',specificProjName,'yolov4-tiny-obj_best.weights'],
        },
        'allTakenImages':{
            'base': [f for f in os.listdir(traindataSrcPathImgsBase) if re.search(".jpg|.JPG", f)!=None]
        },
        'allTakenImagesFilelist':{
            'base': ['allTakenImagesFilelist.txt'],
        },
    }

    for key,value in baseConfigFilenames.items():
        if key=='allTakenImages':
            baseConfigFilenames[key]['orig'] = [os.path.join(traindataSrcPathImgsBase, f) for f in baseConfigFilenames[key]['base']]
            baseConfigFilenames[key]['display'] = [os.path.join(traindataSrcPathImgsBaseDisplayed, f).replace(os.sep, targetOssep) for f in baseConfigFilenames[key]['base']]
        else:
            baseConfigFilenames[key]['orig'] = [traindataSrcPathBase]+baseConfigFilenames[key]['base']
            baseConfigFilenames[key]['orig'] = os.path.join(*baseConfigFilenames[key]['orig'])
            baseConfigFilenames[key]['display'] = [traindataSrcPathBaseDisplayed]+baseConfigFilenames[key]['base']
            baseConfigFilenames[key]['display'] = os.path.join(*baseConfigFilenames[key]['display']).replace(os.sep, targetOssep)

    baseConfigFilenames['traindataSrcPathBase'] = traindataSrcPathBase
    baseConfigFilenames['traindataSrcPathImgsBase'] = traindataSrcPathImgsBase
    baseConfigFilenames['traindataSrcPathBaseDisplayed'] = traindataSrcPathBaseDisplayed
    baseConfigFilenames['traindataSrcPathImgsBaseDisplayed'] = traindataSrcPathImgsBaseDisplayed
    return baseConfigFilenames

def rawSrcAnnotationsToPdDF(dictdata):
    import pandas as pd
    testdf = pd.json_normalize(dictdata)
    testdf2 = [pd.json_normalize(d) for d in testdf['annotations']]
    testdf2 = pd.concat(testdf2).rename(columns={'id':'annotation_from_an_author_id'}).reset_index(drop=True)
    testdf3 = [pd.json_normalize(testdf2.iloc[row_i,:]['result']).assign(annotation_from_an_author_id=testdf2.iloc[row_i,:]['annotation_from_an_author_id'], task=testdf2.iloc[row_i,:]['task']).rename(columns={'id':'annotation_id'})
        for row_i in range(len(testdf2.index))
        ]
    testdf3 = pd.concat(testdf3).reset_index(drop=True)
    #<x_center> <y_center> <width> <height>
    testdf3['value.yolo.width'] = testdf3['value.width'].apply(lambda x: x/100)
    testdf3['value.yolo.height'] = testdf3['value.height'].apply(lambda x: x/100)
    testdf3['value.yolo.x.center'] = testdf3['value.x'].apply(lambda x: x/100)+(testdf3['value.yolo.width']/2)
    testdf3['value.yolo.y.center'] = testdf3['value.y'].apply(lambda x: x/100)+(testdf3['value.yolo.height']/2)
    testdf2 = testdf2.drop(columns=['result']).rename(columns={'created_at':'annotation_from_an_author_updated_at','updated_at':'annotation_from_an_author_updated_at'})
    testdf1 = testdf.drop(columns=['annotations']).rename(columns={'id':'task','created_at':'task_created_at','updated_at':'task_updated_at'})
    mergedf = testdf2.merge(testdf3, how='inner').reset_index(drop=True)
    mergedf = testdf1.merge(mergedf, how='inner').reset_index(drop=True)
    #mergedf['value.rectanglelabels'] = mergedf['value.rectanglelabels'].apply(lambda x: x[0])
    mergedf['data.image.basename'] = mergedf['data.image'].apply(os.path.basename).reset_index(drop=True)
    return mergedf

def calcSteps(case_nums=1000, batch_size=32, epochs=50, warmup_steps_ratio=0.1):
    steps_per_epoch = math.ceil(case_nums / batch_size)
    num_train_steps = math.ceil(case_nums*epochs/batch_size)
    warmup_steps = math.ceil(num_train_steps * warmup_steps_ratio)
    return steps_per_epoch,num_train_steps,warmup_steps

def plot_model_history(srcModelHistory):
    # summarize history
    import matplotlib.pyplot as plt
    for basedisplayhistorykey in [key for key in srcModelHistory.history.keys() if key.find("val")==-1]:
        plt.plot(srcModelHistory.history[basedisplayhistorykey])
        try:
            plt.plot(srcModelHistory.history['val_'+basedisplayhistorykey])
        except:
            pass
        plt.title('model '+basedisplayhistorykey)
        plt.ylabel(basedisplayhistorykey)
        plt.xlabel('epoch')
        plt.legend(['train', 'validation'], loc='upper left')
        plt.show()