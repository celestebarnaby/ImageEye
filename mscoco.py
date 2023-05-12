import pylab
import matplotlib.pyplot as plt
import skimage.io as io
import numpy as np
from cocoapi.PythonAPI.pycocotools.coco import COCO
import os

pylab.rcParams['figure.figsize'] = (8.0, 10.0)

dataDir = '../mscoco'
dataType = 'val2017'
annFile = '{}/annotations/instances_{}.json'.format(dataDir, dataType)

# initialize COCO api for instance annotations
coco = COCO(annFile)

filename_to_id = {img["file_name"]: img["id"]
                  for img in coco.dataset["images"]}

# display COCO categories and supercategories
cats = coco.loadCats(coco.getCatIds())
nms = [cat['name'] for cat in cats]
id_to_name = {cat['id']: cat['name'] for cat in cats}
print(nms)
print()
# print('COCO categories: \n{}\n'.format(' '.join(nms)))

nms = set([cat['supercategory'] for cat in cats])
# print('COCO supercategories: \n{}'.format(' '.join(nms)))

# get all images containing given categories, select one at random
catIds = coco.getCatIds(catNms=['person'])
imgIds = coco.getImgIds(catIds=catIds)
# imgIds = coco.getImgIds(imgIds = [324158])
# RANDOM IMAGE
img = coco.loadImgs(imgIds[np.random.randint(0, len(imgIds))])[0]

annIds = coco.getAnnIds(imgIds=img['id'])
anns = coco.loadAnns(annIds)

ann_id = anns[0]['category_id']
# print(catIds)
# print(cats)


def preprocess():
    img_folder = "../mscoco/smallcoco/"
    i = 0
    for filename in os.listdir(img_folder):
        img_dir = img_folder + filename
        img_id = filename_to_id[filename]
        annIds = coco.getAnnIds(imgIds=img_id)
        anns = coco.loadAnns(annIds)
        env = {}
        for ann in anns:
            details = {}
            details['bbox'] = ann['bbox']
            details['Type'] = 'Object'
            details['Name'] = id_to_name[ann['category_id']]
            env[i] = details
            i += 1
    print(env)


preprocess()
