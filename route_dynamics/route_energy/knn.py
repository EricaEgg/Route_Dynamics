""" Knn Classifier for SEDS hw 4 """
import numpy as np
import pandas as pd


def find_knn(
    k,
    candidate_pts,
    test_pts,
    weight=None
    ):
    """ Takes list of points as candidate neighbors (route points) and
        returns one for reach test point (stops) which is the nearest
        route point to the stop.
        """

    num_train_pts = len(candidate_pts)
    num_test_pts = len(test_pts)
    # Find the k nearest neighbors.

    # Initialize array to store distances between data points
    distance_array = np.zeros((num_test_pts, num_train_pts))

    # Loop through rows in test data
    for test_idx in range(num_test_pts):
        test_coord = test_pts[test_idx]

        # Loop through rows in training data
        for train_idx in range(num_train_pts):
            train_coord = candidate_pts[train_idx]

            # Calc distance between training_data and data
            dist = euclidean_distance(
                train_coord,
                test_coord
                )

            # Store distance in array
            distance_array[test_idx, train_idx] = dist

    # print('distance_array = ',distance_array)
    # sort rows corresponding to each unclassified data point
    sorting_idicies = np.argsort(distance_array)

    # Keep only first k columns, corresponding to k nearest neighbors
    # for each unclassified data point
    k_nearest_indicies = sorting_idicies[:,:k]
    # print(k_nearest_indicies.shape)
    # print('k_nearest_indicies = ',k_nearest_indicies)
    k_nearest_distances = distance_array[
        np.arange(num_test_pts)[:,None], k_nearest_indicies
        ]

    # Build array to hold class of each training data point
    points_array = np.asarray([candidate_pts]*num_test_pts)
    k_nearest_neighbors = points_array[
        np.arange(num_test_pts)[:,None], k_nearest_indicies
        ]

    return k_nearest_indicies, k_nearest_neighbors


# def extract_numeric_columns_from_df(df):
#     numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
#     newdf = test_df.select_dtypes(include=numerics)
#     return newdf


def euclidean_distance(pt_1, pt_2):
    """ A function that returns the Euclidean distance between a row in the
        intput data to be classified.
        """
    # make sure input are np arrays
    pt_1 = np.asarray(pt_1.coords)
    pt_2 = np.asarray(pt_2)

    eucl_dist = np.linalg.norm(pt_2 - pt_1)
    return eucl_dist
