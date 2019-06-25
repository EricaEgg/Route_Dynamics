""" Needs work to adapt to changes made for this package. Tests carreid over from seds hw4 """

from ..route_energy import knn


import numpy as np
import pandas as pd
from sklearn import model_selection

def test_find_knn():
    """ A wrapping function that is the primary way of interacting with your
        code.  It takes as parameters, a training dataframe, a value of k and
        some input data to be classified. It returns the classification for
        the input data.
        """
    # Test 1: build a set of 2D data spanning [-1,1] in x and [-1,1]
    # in y, classified as 'left' or 'right' depending on whether x is
    # positive or negative

    # 100 data points spanninc two columns
    test1_coords = np.random.random((100, 2))*2 - 1
    df1 = pd.DataFrame(test1_coords, columns=['x','y'])

    class_list = []
    for i in df1['x'].values:
        if i>0.:
            class_list.append('right')
        elif i<0.:
            class_list.append('left')
    df1.loc[:,'which half'] = class_list

    train_data, test_data = model_selection.train_test_split(df1, test_size=10)

    k = 5
    classified_test = knn.find_knn(
        k=k,
        numberic_column_name_list=['x','y'],
        class_column_name='which half',
        tr_df=train_data,
        test_df=test_data
        )

    assigned_test_class = classified_test['which half'].values
    true_class = test_data['which half'].values

    for a_class, the_class in zip(assigned_test_class, true_class):
        assert a_class == the_class, (
            "wrong"
            )



def test_euclidean_distance():
    """ A function that returns the Euclidean distance between a row in the
        intput data to be classified.
        """
    random_int = np.random.randint(1,10)
    # Asser that the distance between the origin and a random point is
    # equal to norm its coordinate.
    random_point = np.random.random(random_int)

    dist = knn.euclidean_distance(
        np.zeros((random_int)),
        random_point
        )

    assert dist == np.linalg.norm(random_point), "say something"
