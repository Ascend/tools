#!/bin/bash

# Get COCO 2014 data sets

if [ $1 == 'YoLov3' ];then
	echo 111
	mkdir -p /home/datasets/coco
	pushd /home/datasets/coco

	curl -O http://images.cocodataset.org/zips/train2014.zip
	unzip train2014.zip

	curl -O http://images.cocodataset.org/zips/val2014.zip
	unzip val2014.zip

	curl -O http://images.cocodataset.org/annotations/annotations_trainval2014.zip
	unzip annotations_trainval2014.zip

# Get bert/cule data sets
elif [ $1 == 'Bert' ];then
	echo 222
	mkdir -p /home/datasets/Bertdata
	pushd /home/datasets/Bertdata

	curl -O xxxxxxxxxxx
	tar xxxxx 

# Get imagenet_TF data sets
else
	echo 333
	mkdir -p /home/datasets/imagenet_TF
	pushd /home/datasets/imagenet_TF


	curl -O http://www.image-net.org/challenges/LSVRC/2012/nnoupb/ILSVRC2012_img_val.tar
	tar xvf ILSVRC2012_img_val.tar

	curl -O http://www.image-net.org/challenges/LSVRC/2012/nnoupb/ILSVRC2012_img_train.tar
	tar xvf ILSVRC2012_img_train.tar

	curl -O http://www.image-net.org/challenges/LSVRC/2012/nnoupb/ILSVRC2012_bbox_train_v2.tar
	tar xvf ILSVRC2012_bbox_train_v2.tar
fi



popd
