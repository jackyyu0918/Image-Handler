import math
import multiprocessing
import logging
import shutil

from PIL import Image, UnidentifiedImageError
import os.path
from os import path
import imagehash
import glob
import datetime

# Config your source/destination
# root_dir = 'F:\\Backup\\Mobilephone'
# root_dir = 'E:\\BackUp_from_Storge_Drive\\Backup\\備份_1'

root_dir = os.path.join(os.getcwd(), 'source')

# Image format list
image_file_format_list = ('.jpg', '.gif', '.jpeg', '.png', '.svg')

# Image similarity
# Threshold
hash_diff_threshold = 1  # maximum bits that could be different between the hashes.

# Multi-processing number
worker_number = 20

def split_interval(total_num, worker_number):
    pass

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

def get_path_drop_file_name(full_path: str):
    return full_path[:str(full_path).rfind('\\')]


def get_similar_folder_path(folder_path: str):
    return os.path.join(get_path_drop_file_name(folder_path), 'similar')

def get_file_name_from_path(full_path: str):
    return full_path[str(full_path).rfind('\\')+1:]

def compare_list_to_dict(worker_id, file_list, image_hash_dict):
    for filename_0 in file_list:
        hash_val_0 = image_hash_dict[filename_0]
        for filename_1, hash_val_1 in image_hash_dict.items():
            if filename_0 != filename_1:
                if path.isfile(filename_0) and path.isfile(filename_1):
                    if is_image_similar(hash_val_0, hash_val_1, hash_diff_threshold):
                        msg = 'Worker ' + str(worker_id) + ': Similar file found: ' + str(filename_0) + ' & ' + str(filename_1)
                        print(msg)

                        # Create a similar folder for storing the similar image in same directory
                        similar_folder_path = get_similar_folder_path(filename_0)
                        if not os.path.exists(similar_folder_path):
                            os.makedirs(similar_folder_path)
                        filename_0_new = os.path.join(similar_folder_path, get_file_name_from_path(filename_0))
                        shutil.move(filename_0, filename_0_new)
                        print('Worker ' + str(worker_id) + ': Moved ' + str(filename_0) + ' to ' + str(filename_0_new))
                        break
def split_list_interval(image_count, worker_number):
    interval_list = []

    image_idx_increment = int(math.floor(image_count / worker_number))  # round down

    image_idx_start = 0
    image_idx_max = image_count - 1

    is_interval_prepared = False

    while not is_interval_prepared:
        if image_idx_start + image_idx_increment >= image_idx_max:
            image_idx_end = image_idx_max
            is_interval_prepared = True
        else:
            image_idx_end = image_idx_start + image_idx_increment
        interval_list.append([image_idx_start, image_idx_end])
        image_idx_start += image_idx_increment + 1

    return interval_list


if __name__ == '__main__':
    logger_init()

    start_time = datetime.datetime.now()

    image_list = []
    error_count = 0

    logging.info('Program started')

    # Add all images into a list
    logging.info('Start adding all images into a list')
    for filename in glob.iglob(root_dir + '**/**', recursive=True):
        if filename.endswith(image_file_format_list) and '\\similar\\' not in filename:
            image_list.append(filename)

    logging.info('Completed')
    image_count = len(image_list)
    print(str(image_count))
    logging.info('Image found: ' + str(image_count))

    print(split_list_interval(image_count, worker_number))

    # Multi process
    logging.info('Start calculating the hash values for images in parallel')
    manager = multiprocessing.Manager()
    image_hash_dict = manager.dict()



    # Round up the image processed by each worker
    interval_list = split_list_interval(image_count, worker_number)

    jobs = []
    for i in range(len(interval_list)):
        image_idx_start = interval_list[i][0]
        image_idx_end = interval_list[i][1] + 1

        logging.info('Worker ' + str(i) + ' idx from ' + str(interval_list[i][0]) + ' to ' + str(interval_list[i][1]))
        p = multiprocessing.Process(target=get_image_hash_dict, args=(i, image_list[image_idx_start:image_idx_end], image_hash_dict)) # end idx needs to add 1
        jobs.append(p)
        p.start()

    for proc in jobs:
        proc.join()

    # Compare the image list to the hash dict
    logging.info('Start compare the image list to the hash dict')
    print(str(type(image_hash_dict)))

    image_list = image_hash_dict.keys()

    interval_list = split_list_interval(len(image_list), worker_number)

    jobs = []
    for i in range(len(interval_list)):
        image_idx_start = interval_list[i][0]
        image_idx_end = interval_list[i][1] + 1  # end idx needs to add 1

        p = multiprocessing.Process(target=compare_list_to_dict, args=(i, image_list[image_idx_start:image_idx_end], image_hash_dict))
        jobs.append(p)
        p.start()

    for proc in jobs:
        proc.join()

    logging.info('Completed')

    end_time = datetime.datetime.now()
    time_spent = (end_time - start_time).seconds
    logging.info('Total time spent: ' + str(time_spent) + ' second(s)')

