import sys
import os
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torchvision.io import read_image
import matplotlib.pyplot as plt
import torchvision.transforms.functional as F
from torch.optim import Adam
import tqdm


class WikiArtImage:
    def __init__(self, imgdir, label, filename):
        self.imgdir = imgdir
        self.label = label
        self.filename = filename
        self.image = None
        self.loaded = False

    def get(self):
        if not self.loaded:
            self.image = read_image(os.path.join(self.imgdir, self.label, self.filename)).float()
            self.loaded = True

        return self.image

class WikiArtDataset(Dataset):
    def __init__(self, imgdir, device="cpu"):
        walking = os.walk(imgdir)
        filedict = {}
        indices = []
        classes = set()
        print("Gathering files for {}".format(imgdir))
        for item in walking:
            sys.stdout.write('.')
            arttype = os.path.basename(item[0])
            artfiles = item[2]
            for art in artfiles:
                filedict[art] = WikiArtImage(imgdir, arttype, art)
                indices.append(art)
                classes.add(arttype)
        print("...finished")
        self.filedict = filedict
        self.imgdir = imgdir
        self.indices = indices
        self.classes = list(classes)
        self.device = device
        
    def __len__(self):
        return len(self.filedict)

    def __getitem__(self, idx):
        imgname = self.indices[idx]
        imgobj = self.filedict[imgname]
        ilabel = self.classes.index(imgobj.label)
        image = imgobj.get().to(self.device)

        return image, ilabel

class WikiArtModel(nn.Module):
    def __init__(self, num_classes=27):
        super().__init__()

        self.conv2d = nn.Conv2d(3, 3, (5,5), padding=2)
        self.flatten = nn.Flatten()
        self.linear1 = nn.Linear(3*416*416, 300)
        self.tanh = nn.Tanh()
        self.linear2 = nn.Linear(300, num_classes)
        self.softmax = nn.LogSoftmax(dim=1)

    def forward(self, image):
        output = self.conv2d(image)
        output = self.flatten(output)
        output = self.linear1(output)
        output = self.tanh(output)
        output = self.linear2(output)
        return self.softmax(output)