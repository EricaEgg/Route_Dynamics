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
    pt_1 = np.asarray(pt_1)
    pt_2 = np.asarray(pt_2)

    eucl_dist = np.linalg.norm(pt_2 - pt_1)
    return eucl_dist

def predict_class(list_eucl_dist_and_class, weight=None):
    """ A function that returns the class prediction based on the list of
        sorted Euclidean distances.

        Args:
            list_eucl_dist: 2D np.array with shape = [distance, class].T
                where distance is a float and class is a string.
            weight: how to weight plurality vote.
        """
    # Plurality vote
    #     weight classes
    #     initialize dict for vote

    class_dict = {}
    # Loop through classes in last column of `list_eucl_dist_and_class`
    for idx in range(list_eucl_dist_and_class.shape[0]):
        # Pull out class key from array
        dist, class_key = list_eucl_dist_and_class[idx]
        # For first occurence of class, add to dict
        if class_key not in class_dict:
            # Add to dict
            if weight == None:
                # Just count first occurence of the class
                class_dict[class_key] = 1
            elif (weight == 'distance') or (weight == 'dist'):
                # weight each occurence by 1/distance
                # print('dist = ',dist)
                try:
                    class_dict[class_key] = 1./dist
                except TypeError:
                    class_dict[class_key] = 1./dist.astype(float)
        elif class_key in class_dict:
            # Add value to current value
            if weight == None:
                # Just count occurences of the class
                class_dict[class_key] += 1
            elif (weight == 'distance') or (weight == 'dist'):
                # weight each occurence by 1/distance
                try:
                    class_dict[class_key] = 1./dist
                except TypeError:
                    class_dict[class_key] = 1./dist.astype(float)

    # Predict class by largest value in `class_dict`, idicating sum of
    # votes for each class.
    #
    classes_predicted = keys_with_max_val_in_dict(class_dict)
    if len(classes_predicted) == 1:
        return classes_predicted[0]
    elif len(classes_predicted) > 1:
        print("knn tied, can't assign class")
        return None
    else:
        print("type(classes_predicted) = ", type(classes_predicted))
        print("classes_predicted = ", (classes_predicted))
        raise TypeError("unexpected error in output")


def keys_with_max_val_in_dict(a_dict):
    """ Returns all keys in dictionary with maximum values.
        """

    max_value = 0
    max_keys = []

    for k, v in a_dict.items():
        if v >= max_value:
            if v > max_value:
                max_value = v
                max_keys = [k]
            else:
                max_keys.append(k)

    return max_keys


def percentage_correct_given_k(
    k_list,
    numberic_column_name_list,
    class_column_name,
    tr_df,
    test_df,
    weight=None
    ):
    """ A wrapping function that helps the user decide on what `k` to use.
        This function takes as parameters, a training dataframe, a testing
        dataframe and a list of values of `k` to try. It returns a dictionary
        with `k` as the keys and the training accuracy of the test set.
        Accuracy is measured by percentage of classifications that were
        correct for that value of `k`.
        """
        # Initialize output dict
    k_acc_dict = {}

    # Make sure test dataframe has classes
    if not class_column_name in test_df:
        raise ValueError('Test data frame needs classes asigned for ',
            'accuracy evaluation.')

    for k in k_list:
        # Store classified dataframs in dictionary under keys defined
        # by 'k' value.

        classified_test_df = knn_classify(
            k,
            numberic_column_name_list,
            class_column_name,
            tr_df,
            test_df,
            weight
            )

        is_right = (classified_test_df.Type == classified_test_df.knn_class).values
        num_right = np.sum(is_right)
        percent_right = num_right/len(is_right)
        # evaluate accuracy
        k_acc_dict['k='+str(k)] = percent_right

    return k_acc_dict
