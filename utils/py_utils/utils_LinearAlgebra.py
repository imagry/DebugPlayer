import numpy as np
from scipy import linalg
from scipy.linalg import block_diag

import math
def procurustes_tranasformation(X, Y):
    """
    Compute the Procrustes transformation between two sets of points.

    Parameters:
    - X: numpy.ndarray
        The first set of points represented as an nxd matrix, where each row is a 2D or 3D point.
    - Y: numpy.ndarray
        The second set of points represented as an nxd matrix, where each row is a 2D or 3D point.

    Returns:
    - X_4: numpy.ndarray
        The transformed points from the first set, X, after applying the Procrustes transformation.
    - T: numpy.ndarray
        The transformation matrix T of size (d+1)x(d+1) that minimizes \|A*T^T - B\|_2, where A and B are the input matrices X and Y, respectively.

    Note:
    The Procrustes transformation consists of translation, scaling, and rotation to align two sets of points. The function computes the transformation matrix T such that \|A*T^T - B\|_2 is minimized, where A and B are the input matrices X and Y, respectively. The transformed points X_4 are obtained by applying the transformation matrix T to the points X.
    """
    
    # Function implementation goes here
    d,N = X.shape
    
   # step 1 - translation
    m_X = np.reshape(np.mean(X ,axis = 1),(d,1))
    m_Y = np.reshape(np.mean(Y, axis = 1),(d,1))

    Y_1 = Y-m_Y
    X_1 = X-m_X
    # t = np.reshape(m_Y - m_X,(d,1))
    # t = np.reshape(m_Y-m_X, (d,1))
    # A = np.identity(d)
    # A[:-1,d-1] = np.squeeze(t[:-1])
    
    A1 = np.identity(d)
    A1[:-1,d-1] = np.squeeze(-m_X[:-1])    
    A2 = np.identity(d)
    A2[:-1,d-1] = np.squeeze(+m_Y[:-1])
    
    # uniform scaling
    s_X =  np.sum(np.sqrt(np.sum((X_1)**2,axis=1)/2))
    s_Y =  np.sum(np.sqrt(np.sum((Y_1)**2,axis=1)/2))
    s3 = s_Y/s_X
    S = np.identity(d)*s3
    S[-1,-1]=1

    X_2 = S@X_1

    # rotation
    M = (X_2@Y_1.T)[0:d-1,0:d-1] 
    U, D_, Vh = np.linalg.svd(M, full_matrices=True)
    V = Vh.T
    R_ = V@U.T
    # Ensure that R_ is rotation matrix - see "Kabsch algorithm 
    # (https://en.wikipedia.org/wiki/Kabsch_algorithm)"
    det_sign = np.sign(linalg.det(R_))
    D = np.eye(d-1)
    # we modify the sign at the diagonal coordinate correponding to the last coordinate, 
    # not counting the extra dimension due to the homogeneous representation
    D[-1,-1] = linalg.det(U)*linalg.det(V)
    R_ = V@D@U.T
    R = block_diag(R_,1)
    
    X_3 = R@X_2    
    
    # compensate for m_Y ~= 0
    X_4 = X_3 + np.reshape(m_Y, (d,1))
    
    # compute the overall transformation
    T = A2@R@S@A1
    
    return X_4, T


    # with plt.ioff():
    #     fig_cpm, ax_cpm = plt.subplots()

    # ax_cpm.scatter(   Y[0,:],   Y[1,:], s=20, c='b', label='Y' ,marker="s" )
    # ax_cpm.scatter( Y_1[0,:], Y_1[1,:], s=20, c='b', label='Y_1' ,marker="x" )
    # ax_cpm.scatter( X[0,:], X[1,:], s=20, c='r', label='X' ,marker="s" )
    # ax_cpm.scatter( X_1[0,:],X_1[1,:], s=20, c='r', label='X_1' ,marker="x" )
    # ax_cpm.scatter( X_2[0,:],X_2[1,:], s=20, c='r', label='X_2' ,marker="8" )
    # ax_cpm.scatter( X_3[0,:],X_3[1,:], s=20, c='g', label='X_3' ,marker="^" )
    # ax_cpm.legend()
