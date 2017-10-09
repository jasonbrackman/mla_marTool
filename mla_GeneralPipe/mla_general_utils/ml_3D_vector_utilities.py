__author__ = 'm.lanton'
import math as math

def vector_difference(a_vector=(0, 0, 0), b_vector=(0, 0, 0)):
    """
    Calculate the difference between vectors A and B : C=B-A
    :param a_vector: coordinates of first vector (tuple)
    :param b_vector: coordinates of second vector (tuple)
    :return c_vector: difference from a_vector and b_vector (tuple)
    """

    c_vector = (b_vector[0]-a_vector[0], b_vector[1]-a_vector[1], b_vector[2]-a_vector[2])

    return c_vector


# ----------------------------------------------------------------------------------------------------------------------
def vector_length(vector=(0, 0, 0)):
    """
    Calculate the length of the given vector
    :param vector: coordinates of given vector (tuple)
    :return vector_length: length of the given vector (float)
    """

    length = math.sqrt((vector[0]*vector[0])+(vector[1]*vector[1])+(vector[2]*vector[2]))

    return length


# ----------------------------------------------------------------------------------------------------------------------
def vector_round(vector=(0, 0, 0), tolerance=4):
    """
    Round values of given vector
    :param vector: coordinates of the given vector (tuple)
    :return rounded_vector: rounded coordinates of the given vector (tuple)
    """

    rounded_vector = (round(vector[0], tolerance), round(vector[1], tolerance), round(vector[2], tolerance))

    return rounded_vector


# ----------------------------------------------------------------------------------------------------------------------
def vector_addition(a_vector=(0, 0, 0), b_vector=(0, 0, 0)):
    """
    Add one vector to another : C=A+B
    :param a_vector: coordinates of first vector (tuple)
    :param b_vector: coordinates of second vector (tuple)
    :return c_vector: addition of a_vector and b_vector (tuple)
    """
    
    c_vector = (a_vector[0]+b_vector[0], a_vector[1]+b_vector[1], a_vector[2]+b_vector[2])
    
    return c_vector