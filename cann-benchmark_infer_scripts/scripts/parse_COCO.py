"""
    Copyright 2020 Huawei Technologies Co., Ltd

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
    Typical usage example:
"""
import json
import os
import argparse


def get_all_index(lst, item):
    """ get all of the index
        @param lst
        @param item
        @return index list
    """
    return [index for (index, value) in enumerate(lst) if value == item]


def change_class(cls):
    """
     use '_' link the cls which space in between
    """
    if len(cls.split()) == 2:
        temp = cls.split()
        cls = temp[0] + '_' + temp[1]
    return cls


def get_categroie_name(lst, item):
    """ get category name
        @param lst
        @param item
        @return categroie_name
    """
    categroie_name = [dt.get('name') for dt in lst if item == dt.get('id')][0]
    categroie_name = change_class(categroie_name)
    return categroie_name


def check_args(args):
    """ check input arguments
        @param args input arguments
        @return args
    """
    if not os.path.exists(args.json_file):
        print('-' * 55)
        print("The specified '{}' file does not exist".format(args.json_file))
        print('You can get the correct parameter information from -h')
        print('-' * 55)
        exit()
    if not os.path.exists(args.gtp):
        os.makedirs(args.gtp)
    return args


def main(args):
    """ main process
        @param args input arguments
        @return none
    """
    with open(args.json_file, 'r') as file:
        content = file.read()
    content = json.loads(content)
    images = content.get('images')
    annotations = content.get('annotations')
    categroies = content.get('categories')

    with open(args.classes, 'w') as f:
        for categroie in categroies:
            cls = categroie.get('name')
            cls = change_class(cls)
            f.write(cls)
            f.write('\n')
    
    file_names = [image.get('file_name') for image in images]
    widths = [image.get('width') for image in images]
    heights = [image.get('height') for image in images]
    image_ids = [image.get('id') for image in images]
    assert len(file_names) == len(widths) == len(heights) == len(image_ids), "must be equal"

    annotation_ids = [annotation.get('image_id') for annotation in annotations]
    bboxs = [annotation.get('bbox') for annotation in annotations]
    category_ids = [annotation.get('category_id') for annotation in annotations]
    assert len(annotation_ids) == len(bboxs) == len(category_ids)
    
    with open(args.info, 'w') as f:
        for index, file_name in enumerate(file_names):
            file_name = args.img_path + '/' + file_name
            line = "{} {} {} {}".format(index, file_name, widths[index], heights[index])
            f.write(line)
            f.write('\n')
    
    for index, image_id in enumerate(image_ids):
        indexs = get_all_index(annotation_ids, image_id)
        with open('{}/{}.txt'.format(args.gtp, file_names[index].split('.')[0]), 'w') as f:
            for idx in indexs:
                f.write(get_categroie_name(categroies, category_ids[idx]))
                f.write(' ')
                # change label
                bboxs[idx][2] = bboxs[idx][0] + bboxs[idx][2]
                bboxs[idx][3] = bboxs[idx][1] + bboxs[idx][3]
                f.write(' '.join(map(str, bboxs[idx])))
                f.write('\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse the coco dataset label')
    parser.add_argument("--json_file", default="./instances_val2017.json", help='Original json file')
    parser.add_argument("--img_path", default="val2017", help='The image path')
    parser.add_argument("--classes", default="coco2017.names", help='The file of record the category')
    parser.add_argument("--info", default="coco2017.info", help='The file of record image info')
    parser.add_argument("--gtp", default="ground-truth/", help='The ground true file path')
    args = parser.parse_args()
    args = check_args(args)
    main(args)
