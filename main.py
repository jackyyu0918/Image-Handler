import math
import multiprocessing
import logging
from PIL import Image, UnidentifiedImageError
import os.path
from os import path
import imagehash
import glob
import datetime

# Config your source/destination
root_dir = 'F:\\Backup\\Mobilephone'

# Image format list
image_file_format_list = ('.jpg', '.gif', '.jpeg', '.png', '.svg')

# Image similarity
# Threshold
hash_diff_threshold = 5  # maximum bits that could be different between the hashes.

# Multi-processing number
worker_number = 5

def get_image_hash(file_name):
    if path.exists(file_name):
        return imagehash.average_hash(Image.open(file_name))

def get_image_hash_dict(worker_id, file_list, image_hash_dict):
    for image in file_list:
        try:
            image_hash_dict[image] = get_image_hash(image)
        except UnidentifiedImageError as e:
            logging.error(e)

        print('Worker ' + str(worker_id) + ': Finshed hash calculation of ' + image)

def is_image_similar(hash_val_0, hash_val_1, threshold):
    if hash_val_0 - hash_val_1 < threshold:
        return True
    else:
        return False

def logger_init():
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

    log_folder = os.path.join(os.getcwd(), 'log')
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    log_filename = log_folder + '\\' + timestamp + '.log'
    logging.basicConfig(filename=log_filename, format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')


if __name__ == '__main__':
    logger_init()

    image_list = []
    error_count = 0

    logging.info('Program started')

    # Add all images into a list
    logging.info('Start adding all images into a list')
    for filename in glob.iglob(root_dir + '**/**', recursive=True):
        if filename.endswith(image_file_format_list):
            image_list.append(filename)

    logging.info('Completed')
    image_count = len(image_list)
    print(str(image_count))
    logging.info('Image found: ' + str(image_count))

    # Multi process
    logging.info('Start calculating the hash values for images in parallel')
    manager = multiprocessing.Manager()
    image_hash_dict = manager.dict()

    # Round up the image processed by each worker
    image_idx = 0
    image_idx_max = image_count-1
    image_idx_increment = int(math.floor(image_count/worker_number)) # round down

    # Split the list and calculate interval according to worker number


    jobs = []
    image_idx_start = image_idx
    is_end = False
    for worker_id in range(worker_number):
        # Calculate the end range
        if image_idx_start + image_idx_increment > image_idx_max:
            image_idx_end = image_idx_max
        else:
            image_idx_end = image_idx_start + image_idx_increment

        if image_idx_end <= image_idx_max and is_end is False:
            if image_idx_end == image_idx_max:
                is_end = True

            logging.info('Worker ' + str(worker_id) + ' idx from ' + str(image_idx_start) + ' to ' + str(image_idx_end))
            p = multiprocessing.Process(target=get_image_hash_dict, args=(worker_id, image_list[image_idx_start:image_idx_end+1], image_hash_dict)) # end idx needs to add 1
            jobs.append(p)
            p.start()

            image_idx_start += image_idx_increment + 1

    for proc in jobs:
        proc.join()