from os import listdir
from os.path import isfile, join
import pickle, csv

import numpy as np
from scipy.misc import imread


PATH_TO_PLACE_TASK_DATA = '../../mediaeval_placing_task_2015_data/'

# FOR SMALL DATASET
PATH_TO_PLACE_TASK_DATA_ALL = '../data/000_small/'
PATH_TO_PLACE_TASK_DATA_TRAIN = '../data/train'
PATH_TO_PLACE_TASK_DATA_TEST = '../data/test'
PATH_TO_PLACE_TASK_DATA_VAL = '../data/validation'

IMG_HEIGHT = 500
IMG_WIDTH = 300
NUM_CHANNELS = 3

TRUTH_LABELS_FILENAME = 'mediaeval2015_placing_locale_train'


def get_image_filenames(path):
  '''
  Returns a list of filenames in the folder of the specified path
  '''

  # NOTE: Make sure to delete any hidden files in this folder (such as .DS_STORE) that may get added to the image_filenames list
  image_filenames = [f.split(".")[0] for f in listdir(path) if isfile(join(path, f))]  # remove the ".png" part of filename
  # print 'image_filenames = {}'.format(image_filenames)
  return image_filenames

def open_labels_data(image_filename_list = [], pickle_filename = None):
  '''
  1) Opens file with truth labels and saves info on images in a map. Loads only image data pertaining to given image filenames if a list of images is specified.
    { image ID: (node_id, node_name, long, lat) }

  Note: ignore data on videos

  2) Saves data to a pickle file
  '''
  image_info_map = {}
  file_path = PATH_TO_PLACE_TASK_DATA + TRUTH_LABELS_FILENAME

  # 1) Open ground truth data
  print 'INFO: Loading ground truth data...'
  print 'Loading labels for {} images'.format(len(image_filename_list))
  ncount = 0
  added_to_map_count = 0
  with open(file_path) as tsv:
    for line in csv.reader(tsv, dialect="excel-tab"):
      if ncount % 50000 == 0:
        print 'processed {} * 50k photos'.format(ncount/50000)
        print 'map count: {}'.format(added_to_map_count)
      ncount += 1
      obj_id = line[0]
      if obj_id not in image_filename_list:  # check if we are using a shortened list of images
        # print 'Skipped: Not in given list'
        continue
      obj_type = line[1]
      if obj_type == 1:  # ignore video data
        continue
      image_info_map[obj_id] = line[2:]  # [year, node_id, node_name, long, lat]
      # print '{} added to map'.format(obj_id)
      added_to_map_count += 1

      if added_to_map_count == len(image_filename_list):
        print 'Found all the {} needed labels!'.format(added_to_map_count)
        break

  print 'Created map with {} objects.'.format(len(image_info_map))

  # 2) Save to pickle file
  print 'INFO: Saving to pickle file...'
  if pickle_filename: 
    with open(pickle_filename, 'w') as f:
      pickle.dump(image_info_map, f)

    # test pickle file
    obj_id = '00cb928aff9719f0d57c21e371288b'
    print 'obj_id = {}'.format(obj_id)
    print 'original value = {}'.format(image_info_map[obj_id])
    with open(pickle_filename, 'r') as f:
      test_map = pickle.load(f)
      print 'pickled value = {}'.format(test_map[obj_id])

  return image_info_map


def map_image_id_to_node(pickle_file, image_node_map, image_filenames_list, truth_labels_all):
  '''
  Loads the pickle file and updates the given map with the following key, value pairs.
    Key: names of images from the given list
    Value: associated node location names taken from the truth labels
    {image ID: (node_id, node_name)}
  '''
  truth_labels_for_image_filenames = {}

  for image_id in image_filenames_list:
    # node_id = 
    # node_name = 
    # image_node_map[image_id] = (node_id, node_name)
    pass



def load_images_data(image_filenames_list, np_save_filename):
  '''
  Loads all images from list of filenames and saves them to a numpy file.
  Returns list of image filenames that passed the spec test (correct width, height, channel size)
  '''
  print 'Loading folder with {} images.'.format(len(image_filenames_list))
  all_image_data = np.empty((len(image_filenames_list), IMG_WIDTH, IMG_HEIGHT, NUM_CHANNELS))
  final_image_filenames_list = [] # list of all image filenames added to X input data
  img_count = 0
  for img_index, image_filename in enumerate(image_filenames_list):
    if img_index % 100 == 0:
      print 'Processed {} *100 images.'.format(img_index/100)
    # if img_count == 10:
    #   break
    filename = PATH_TO_PLACE_TASK_DATA_ALL + image_filename + '.png'
    with open(filename, 'rb') as img_file:
      image_array = imread(img_file)  # (W, H, C)
      # print filename
      # print image_array.shape
      if image_array.shape != (IMG_WIDTH, IMG_HEIGHT, NUM_CHANNELS):   # skip if image does not have 3 channels
        continue
      all_image_data[img_count] = image_array
      final_image_filenames_list.append(image_filename)
      img_count += 1

      # if all_image_data is not None:
      #   image_array = np.expand_dims(image_array, axis=0)  # (1, H, W, C)
      #   all_image_data = np.vstack((all_image_data, image_array))  
      # else:
      #   all_image_data = image_array
      #   print 'created image_data_matrix with shape: {}'.format(all_image_data.shape)

  print 'Num images loaded that passed spec: {}'.format(img_count)
  all_image_data = all_image_data[:img_count]
  print 'Final image data shape: {}'.format(all_image_data.shape)

  # Save data
  print 'INFO: Saving X as np file'
  print np_save_filename
  np.save(np_save_filename, all_image_data)

  # arr = np.load(np_save_filename)
  # print 'INFO: Loading np file'
  # print 'Loaded array with shape {}'.format(arr.shape)

  return final_image_filenames_list

def get_truth_labels(image_filenames_list, pickled_all_info_file, np_save_filename):
  '''
  Extract Y in correct order (based on image_filenames_list).
  Save Y as numpy file
  '''
  with open(pickled_all_info_file, 'r') as f:
    image_info_map = pickle.load(f)
    Y = np.empty((len(image_filenames_list)), dtype=str)
    for index, img_name in enumerate(image_filenames_list):
      country_name = image_info_map[img_name][2].split('@')[0]  # take country name from node name in index 4
      # if index <= 10:
      #   print country_name
      Y[index] = country_name

    # Save data
    print 'INFO: Saving Y vector as np file'
    print np_save_filename
    np.save(np_save_filename, Y)

    arr = np.load(np_save_filename)
    print 'INFO: Loading np file'
    print 'Loaded array with shape {}'.format(arr.shape)



if __name__ == "__main__":

  # test pickle file
  # obj_id = '001188ddf4be8e85477ca09d6b742f'
  # print 'obj_id = {}'.format(obj_id)
  # # print 'original value = {}'.format(image_info_map[obj_id])
  # with open('../data_maps/image_id_to_node_info_000_labels.pickle', 'r') as f:
  #   test_map = pickle.load(f)
  #   print 'pickled value = {}'.format(test_map[obj_id])

  # path = PATH_TO_PLACE_TASK_DATA + '000/'
  # image_filenames_train = get_image_filenames(PATH_TO_PLACE_TASK_DATA_TRAIN)
  # image_filenames_test = get_image_filenames(PATH_TO_PLACE_TASK_DATA_TEST)
  # image_filenames_val = get_image_filenames(PATH_TO_PLACE_TASK_DATA_VAL)
  # image_filenames = image_filenames_train + image_filenames_test + image_filenames_val

  # 0) Load labels data from mediaeval train file and saves to pickle file
  # open_labels_data(image_filenames, pickle_filename = '../data_maps/image_id_to_node_info_000_small_labels.pickle')

  image_filenames_small = get_image_filenames(PATH_TO_PLACE_TASK_DATA_ALL)
  # 1) Get input data X
  # print image_filenames_small[:10]
  final_image_filenames_small = load_images_data(image_filenames_small, '../data_maps/x_input_000_small.npy') # Pass in npy file name to save to
  # 2) Get truth labels Y
  # get_truth_labels(final_image_filenames_small, '../data_maps/image_id_to_node_info_000_small.pickle', '../data_maps/y_country_name_000_small.npy')  # Pass in pickle file to load image data from and np save filename

  # truth_labels_for_image_filenames = map_image_id_to_node(image_node_map, image_filenames, truth_labels_all)