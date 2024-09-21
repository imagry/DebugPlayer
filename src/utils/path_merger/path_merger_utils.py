import numpy as np
import math
from scipy import interpolate
from scipy.stats import linregress
import matplotlib.pyplot as plt
import bspline
import bspline.splinelab
from typing import Optional
from utils.path_geom_utils import *


def gdk(z, n, k):
    zt = z[1:-1]
    t = []
    for i in range(n):
        t.append(zt[round((len(zt)-1)*(i+1)/(n+1))])
        
    t = np.concatenate(([z.min()]*(k+1), t, [z.max()]*(k+1)))
    return t

def softmax(w):
    w=np.exp(w)
    w/=w.sum()
    return w

def getSpeedVector(x, double=False):
    m = len(x)
    if len(x.shape) < 2:
        x = np.expand_dims(x,1)
    d = np.sqrt(((x[1:]-x[:-1])**2).sum(axis=1))
    z = []
    zsum = 0
    for i in range(len(x)):
        z.append(zsum)
        if i < m-1:
            if double:
                zsum += d[i]/2
                z.append(zsum)
                zsum += d[i]/2
            else:
                zsum += d[i]
    return np.array(z)

def generateUniformKnotVector(n,k):
    t = np.linspace(0,1,n+2)
    t = np.concatenate(([0]*k, t, [1]*k)) #n+2k+2
    return t

def generateDistKnotVector(x, n, k):
    z = getSpeedVector(x)
    z /= z[-1]
    z = z[1:-1]
    t = []
    for i in range(n):
        t.append(z[round((len(z)-1)*(i+1)/(n+1))])
        
    t = np.concatenate(([0]*(k+1), t, [1]*(k+1)))
    return t

def generateKnot(knotStrategy,x,n,k):
    if knotStrategy == 0:
        t = generateDistKnotVector(x,n,k)
    elif knotStrategy == 1:
        t = generateUniformKnotVector(n,k)
    return t
    
def vieta_formula(roots, n):
    # Initialize an array for polynomial coefficients
    coeff = [0] * (n + 1)
    # Set the highest order coefficient as 1
    coeff[0] = 1
 
    for i in range(n):
        for j in range(i + 1, 0, -1):
            coeff[j] += roots[i] * coeff[j - 1]
            
    return coeff[::-1]
    
def constructSmoothingMatrix(t,n,k):
    AT = np.zeros((n+k+1,n))
    for j in range(n):
        for i in range(k+n+1):
            if i<j+1 or i>j+k+1:
                AT[i][j] = 0
            else:
                roots = np.array(t[i:i+k+2])
                roots = -roots
                # Call the vieta_formula function
                coeffs = vieta_formula(roots, len(roots))
                pi_prime = 0
                for ri in range(1,len(roots)+1):
                    pi_prime += coeffs[ri]*(t[j+k+1]**(ri-1))*ri
                
                #print(i,j, i+1, i-k, len(t), t[j], pi_prime)
                #print(math.factorial(k),(t[i+k+1]-t[i]),pi_prime, t[j+k+1], roots, coeffs)
                AT[i][j] = math.factorial(k)*(t[i+k+1]-t[i])/pi_prime
    return AT.T

def constructSecondDerMatrix(x):
    m = len(x)
    h = x[1:]-x[:-1]
    Q = np.zeros((m,m-2))
    R = np.zeros((m-2,m-2))
    for i in range(m-2):
        Q[i][i] = 1/h[i]
        Q[i+1][i] = -(1/h[i]+1/h[i+1])
        Q[i+2][i] = 1/h[i+1]
        R[i][i] = (h[i]+h[i+1])/3
        if i < m-3:
            R[i+1][i] = R[i][i+1] = h[i+1]/6
            
    return Q @ np.linalg.inv(R) @ Q.T

def get_proj_idx(path_1, path_2, clean=False):
    """
    Returns the indices of the closest points in `path_2` for each point in `path_1`.

    Parameters:
    - path_1 (numpy.ndarray): Array of shape (N, D) representing the first path.
    - path_2 (numpy.ndarray): Array of shape (M, D) representing the second path.
    - clean (bool, optional): If True, removes duplicate indices and sorts them. Default is False.

    Returns:
    - numpy.ndarray: Array of shape (N,) containing the indices of the closest points in `path_2` for each point in `path_1`.
    """
    idx = np.array([np.linalg.norm(path_2-p, axis=1).argmin() for p in path_1])
    if clean:
        idx = np.unique(idx)
        idx.sort()
        
    return idx

def get_path_by_idx(path, idx):
    return [path[i] for i in idx]

def getProj(p1, p2):
    """
    Get the projections of two paths onto each other.

    Parameters:
    p1 (array-like): The first path.
    p2 (array-like): The second path.

    Returns:
    tuple: A tuple containing the projections of p1 onto p2 (proj1), p2 onto p1 (proj2),
        the index of the projection in p1 (idx1), and the index of the projection in p2 (idx2).
    """
    idx1 = get_proj_idx(p2, p1, clean=True)
    proj1 = np.array(get_path_by_idx(p1, idx1))
    
    idx2 = get_proj_idx(proj1, p2)
    proj2 = np.array(get_path_by_idx(p2, idx2))

    return proj1, proj2, idx1, idx2

def FitSpline(path, k, lm, clamp=True):
    """
    Fits a spline curve to a given path.

    Args:
        path (numpy.ndarray): The input path as a numpy array.
        k (int): The degree of the spline curve.
        lm (float): The lambda value for controlling the trade-off between smoothness and fidelity to the input path.
        clamp (bool, optional): Whether to clamp the endpoints of the spline curve to the first and last points of the input path. Defaults to True.

    Returns:
        tuple: A tuple containing the spline curve parameters (t, c, k) and the speed vector (z).
        z - speed vector/distance vector of points in spline corresponding to the data points the spline was fit to 
    """
    cn = len(path)
    z = getSpeedVector(path)
    t = gdk(z, cn - k - 1, k)
    bs = bspline.Bspline(t, k)
    B = np.array([bs._Bspline__basis(zi, k) for zi in z])
    B[-1][-1] = 1
    K = constructSecondDerMatrix(z)
    m = len(path)

    eqn = 2
    P = np.zeros((eqn, cn))
    q = np.zeros((eqn, 2))

    if clamp:
        P[0][0] = P[-1][-1] = 1
        q[0] = path[0]
        q[1] = path[-1]

    LHS = np.concatenate(
        (
            np.concatenate(
                (
                    ((1 - lm) * (B.T @ B)) + (lm * ((B).T @ K @ (B))),
                    P.T
                ),
                axis=1
            ),
            np.concatenate(
                (
                    P,
                    np.zeros((P.shape[0], P.shape[0]))
                ),
                axis=1
            )
        ),
        axis=0
    )
    RHS = np.concatenate(((1 - lm) * (B.T @ path), q), axis=0)
    cz = np.linalg.pinv(LHS) @ RHS
    c = cz[:cn]
    t = (t-z.min())/(z.max()-z.min())

    return (t, c.T, k), z

def FitSplineWithAngleConstraint(path, k, lm, lm2, angle_index, theta, w=None, clamp=True):
    """
    Fits a spline curve to a given path with angle constraint.

    Args:
        path (numpy.ndarray): The input path as a 2D numpy array of shape (n, 2), where n is the number of points in the path.
        k (int): The degree of the spline curve.
        lm (float): The weight for the first term in the objective function.
        lm2 (float): The weight for the second term in the objective function.
        angle_index (int): The index of the point in the path to apply the angle constraint.
        theta (float): The angle constraint in radians.
        w (numpy.ndarray, optional): The weight vector for the path points. If not provided, equal weights are used. Defaults to None.
        clamp (bool, optional): Whether to apply clamping constraints. Defaults to True.

    Returns:
        tuple: A tuple containing the spline curve parameters (t, c, k) and the speed vector of the path (z).
            - t (numpy.ndarray): The knot vector of the spline curve.
            - c (numpy.ndarray): The control points of the spline curve as a 2D numpy array of shape (2, n).
            - k (int): The degree of the spline curve.
            - z (numpy.ndarray): The speed vector of the path as a 1D numpy array of shape (n,).
    """
    # Function implementation goes here
    cn = len(path)
    if w is None:
        w=[1]*cn
        w = softmax(w)
    
    w = np.tile(w,2)
    w = np.expand_dims(w,1)
        
    z = getSpeedVector(path)
    t = gdk(getSpeedVector(path, double=True),cn-k-1,k)
    t = gdk(z,cn-k-1,k)
    bs = bspline.Bspline(t, k)
    B = np.array([bs._Bspline__basis(zi,k) for zi in z])
    B[-1][-1] = 1
    K=constructSecondDerMatrix(z)
    m = len(path)
    
    Bp = np.concatenate((np.concatenate((B,np.zeros((m,cn))), axis=1), np.concatenate((np.zeros((m,cn)),B), axis=1)), axis=0)
    Bp = np.concatenate((Bp, np.zeros((2*cn,1))),axis=1)

    Kp = np.concatenate((np.concatenate((K,np.zeros((m,m))), axis=1), np.concatenate((np.zeros((m,m)),K), axis=1)), axis=0)
    
    eqn = 4
    P = np.zeros((eqn, 2*cn+1))
    q = np.zeros((eqn,1))

    if clamp:
        P[0][0] = P[1][cn-1] = P[2][cn] = P[3][2*cn-1] = 1
        q[0] = path[0][0]
        q[1] = path[-1][0]
        q[2] = path[0][1]
        q[3] = path[-1][1]
    
    u = z[angle_index]
    bs_d = bspline.Bspline(t[1:-1], k-1)
    b_d = bs_d._Bspline__basis(u,k-1)
    d = np.concatenate(([-b_d[0]*k/(t[k+1]-t[1])],[b_d[i-1]*k/(t[i+k]-t[i])-b_d[i]*k/(t[i+k+1]-t[i+1]) for i in range(1,cn-1)], [b_d[cn-2]*k/(t[k+cn-1]-t[cn-1])]),axis=0)
    
    D = np.vstack((np.concatenate((d,np.zeros(d.shape)),axis=0),np.concatenate((np.zeros(d.shape),d),axis=0)))
    D = np.concatenate((D,np.array([[-np.cos(theta)], [-np.sin(theta)]])), axis=1)
    
    LHS = np.concatenate((np.concatenate(((1-lm2)*((1-lm)*((w*Bp).T @ (w*Bp))+lm*((Bp).T@Kp@(Bp)))+lm2*(D.T@D),P.T),axis=1), np.concatenate((P, np.zeros((P.shape[0],P.shape[0]))), axis=1)), axis=0)
    RHS = np.concatenate(((1-lm2)*(1-lm)*((w*Bp).T @ (w*path.T.reshape(2*len(path),1))), q),axis=0)
    cz = np.linalg.pinv(LHS) @ RHS
    c = cz[:2*cn+1]
    
    r = c[-1]
    c = c[:-1].reshape(2,cn)
    t = (t-z.min())/(z.max()-z.min())

    d=np.expand_dims(d,0)
    print(d.shape,c.shape)
    der=(d@c.T)[0]
    th = np.arctan(der[1]/der[0])
    return (t,c,k), z
    

def MergePaths(p1, p2, i1, i2, lm1, lm2, theta, k=3, w_inc=1):
    """
    Merge two paths with angle constraint.

    Args:
        p1 (numpy.ndarray): First path.
        p2 (numpy.ndarray): Second path.
        i1 (int): Index of the last point in the first path to track.
        i2 (int): Index of the first point in the second path to track.
        lm1 (float): First angle constraint.
        lm2 (float): Second angle constraint.
        theta (float): Total angle constraint.
        k (int, optional): Degree of the spline. Defaults to 3.
        w_inc (int, optional): Weight increment. Defaults to 1.

    Returns:
        tuple: Tuple containing the spline representation of the merged path and additional information.
    """
    proj1, proj2, idx1, idx2 = getProj(p1, p2)
    i12 = idx1.min()
    n1 = np.max(i1 - i12, 0)
    i21 = min(idx2.min() + n1, i2)

    path = np.concatenate((p1[:i1], p2[i21:]))
    w = np.concatenate(([1] * i1, np.linspace(0, 1, i2 - i21) ** w_inc if i2 > i21 else [], [1] * (len(p2) - i2)))

    # w = softmax(w)

    tck_new, _ = FitSplineWithAngleConstraint(path, k, lm1, lm2, i1 + i2 - i21, theta, w=w, clamp=True)

    return tck_new


def MergePaths_i12(p1, p2, i1, i12, N2, lm1, lm2, theta, k=3, w_inc=1):
    """
    Merge two paths with angle constraint.

    Args:
        p1 (numpy.ndarray): First path.
        p2 (numpy.ndarray): Second path.
        i1 (int): Index of the last point in the first path to track.
        i2 (int): Index of the first point in the second path to track.
        lm1 (float): First angle constraint.
        lm2 (float): Second angle constraint.
        theta (float): Total angle constraint.
        k (int, optional): Degree of the spline. Defaults to 3.
        w_inc (int, optional): Weight increment. Defaults to 1.

    Returns:
        tuple: Tuple containing the spline representation of the merged path and additional information.
    """
    # proj1, proj2, idx1, idx2 = getProj(p1, p2)
    # i12 = idx1.min()
    # n1 = np.max(i1 - i12, 0)
    # i12 = min(idx2.min() + n1, i2)
    # i2 = i12 + N2
    i2 = min(i12 + N2, p2.shape[0]-1)    # Note this caused stability issues before the min was added 
    path = np.concatenate((p1[:i1], p2[i12:]))
    w = np.concatenate(([1] * i1, np.linspace(0, 1, i2 - i12) ** w_inc if i2 > i12 else [], [1] * (len(p2) - i2)))

    # w = softmax(w)

    tck_new, _ = FitSplineWithAngleConstraint(path, k, lm1, lm2, i1 + i2 - i12, theta, w=w, clamp=True)

    return tck_new

class PathMergerOptions:
    def __init__(self, lambda_1: Optional[float] = None, w: Optional[float] = None, lambda_2: Optional[float] = None):
        self.lambda_1 = lambda_1
        self.w = w
        self.lambda_2 = lambda_2

def path_merger_wrapper(p1_ego_p2: np.ndarray, p2_ego_p2: np.ndarray, X_1_world, X_2_world, X_now_world, tau_1: float, N2: int,  Vnow = 10 /3.6, options: Optional[PathMergerOptions] = None,  DEBUG_MODE = False) -> np.ndarray:
    """
    Wrapper function for the path merger. This function takes two paths, p1 and p2, and merges them together. The first path, p1, is assumed to be the path that is currently being followed by the robot. The second path, p2, is assumed to be the path that the robot should follow after it has finished following p1. The function returns a new path that is the result of merging p1 and p2 together. The parameter tau_1 specifies the time at which the robot should switch from following p1 to following p2. The parameter N2 specifies the number of points in p2 that should be included in the merged path. The merged path is constructed by taking the first N1 points of p1, the last N2 points of p2, and interpolating between the two paths using a linear interpolation.

    Parameters:
    p1 (np.ndarray): The first path to be merged.
    p2 (np.ndarray): The second path to be merged.
    X_1: pose of the car at time t_1 given as SE2 object
    X_now: pose of the car at the current time given as SE2 object
    tau_1 (float): Time constant to approximate system delay from path handler to control at which the car should switch from following p1 to following p2.
    N2 (int): The number of points in p2 that are skipped before requiring the car to follow path 2 
    Vnow (float, optional): The current velocity of the car in m/s. Defaults to 10/3.6.
    options (PathMergerOptions, optional): Additional options for the path merger.

    Returns:
    np.ndarray: The merged path.
    """
    # Example of accessing options
    if options:
        if options.lambda_1:
            lambda_1 = options.lambda_1
        else    :
            lambda_1 = 0.5
        if options.w:    
            w = options.w
        else:   
            w = 1
        if options.lambda_2:
            lambda_2 = options.lambda_2
        else:
            lambda_2 = 0.5
        # Use these options in your implementation

    # compute indices i0, i1, i12, i2
    Xnow_ego_p2 = X_2_world.inv() * X_now_world
    ds = 0.1    
    i0 = int(get_proj_idx(Xnow_ego_p2.t.reshape(-1,1).T, p1_ego_p2, clean=True)[0])
    i0 = min(max(i0, 0), p1_ego_p2.shape[0])
    # pt_i0, i0 = find_close_pt_to_path(p1, X_now.t.reshape(-1,1).T)    
    i1 = int(min(i0 + math.ceil(Vnow*tau_1/ds), p1_ego_p2.shape[0]-2))
    i1 = min(max(i1, 0), p1_ego_p2.shape[0])
    i12 = int(get_proj_idx([p1_ego_p2[i1]], p2_ego_p2, clean=True)[0])
    i12 = min(max(i12, 0), p2_ego_p2.shape[0])
    i2 = (min(i12 + N2, p2_ego_p2.shape[0]-2))
    i2 = min(max(i2, 0), p2_ego_p2.shape[0])
        
    # Extract entering angle at the end of blending region
    tan_vec , theta_rad = compute_tangent_to_path_at_index(p2_ego_p2, i12)       
    k=3           
    p2_merged_ego_p2_tck = MergePaths_i12(p1_ego_p2, p2_ego_p2, i1, i12, N2, lm1 = lambda_1, lm2 = lambda_2, theta = theta_rad, k=k, w_inc=w)    
    p2_merged_ego_p2 = np.asarray(interpolate.splev(np.linspace(0,1,101),p2_merged_ego_p2_tck)).T
    # truncate p2_merged_ego_p2 such that it starts from the origin and discard points before that    
    origin_pt = np.array([0,0])
    i_start = get_proj_idx(origin_pt , p2_merged_ego_p2, clean=True)[0]
    p2_merged_ego_p2_truncated = p2_merged_ego_p2[i_start:]    
    p2_merged_world = apply_se2_transform(X_2_world, p2_merged_ego_p2)
    
    if DEBUG_MODE:        
        return p2_merged_ego_p2_truncated, p2_merged_world, i0, i1, i12, i2
    else:
        return p2_merged_ego_p2_truncated
   
    


    
