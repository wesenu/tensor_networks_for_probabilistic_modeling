# -*- coding: utf-8 -*-

import numpy as np
import os.path
import sys
import pickle
import time
from tensornetworks.PositiveMPS import PositiveMPS
from tensornetworks.RealBorn import RealBorn
from tensornetworks.ComplexBorn import ComplexBorn
from tensornetworks.RealLPS import RealLPS
from tensornetworks.ComplexLPS import ComplexLPS

def init(datasetload_init='lymphography',batch_size_init='20',learning_rate_init='1.',
         bond_dimension_init='2',n_iter_init='10',ansatz_init='squarecomplex',
         seed_init=None,save_init=False):
    """Initialize parameters :
        ----------
        datasetload : str, path of dataset
        batch_size : int, Number of examples per minibatch.
        learning_rate : float, learning rate
        bond_dimension : int, bond dimension of MPS
        n_iter : int, Number of iterations over the training dataset to perform
        ansatz : choice of MPS type ansatz
        seed_init : int, Choice of seed for random number generation
    """
    global datasetload
    global batch_size
    global learning_rate
    global bond_dimension
    global n_iter
    global ansatz
    global optimmethod
    global rng
    global save
    
    datasetload=str(datasetload_init)
    batch_size=int(batch_size_init)
    learning_rate=float(learning_rate_init)
    bond_dimension=int(bond_dimension_init)
    n_iter=int(n_iter_init)
    ansatz=str(ansatz_init)
    if seed_init==None:
        rng=np.random.RandomState()
    else:
        rng=np.random.RandomState(int(seed_init))
    save=bool(save_init)
        
def run():
    # Load dataset
    if os.path.isdir('/ptmp/mpq/iglasser/unsupervised'):
        path='/ptmp/mpq/iglasser/unsupervised/'
    else:
        path='datasets/'
    with open(path+datasetload, 'rb') as f:
        a=pickle.load(f)
    X=a[0]
    X=X.astype(int)
    X_test=a[1]
    X_test=X_test.astype(int)    

    #define MPS
    if ansatz=="positive":
        mps = PositiveMPS(bond_dimension, learning_rate, batch_size, 
                          n_iter, verbose=False, random_state=rng) 
    elif ansatz=="squarereal":
        mps = RealBorn(bond_dimension, learning_rate, batch_size, 
                            n_iter, verbose=False, random_state=rng) 
    elif ansatz=="squarecomplex":
        mps = ComplexBorn(bond_dimension, learning_rate, batch_size, 
                               n_iter, verbose=False, random_state=rng) 
    elif ansatz=="realLPS":
        mps = RealLPS(bond_dimension, learning_rate, batch_size, 
                       n_iter, verbose=False, random_state=rng, mu=2)
    elif ansatz=="complexLPS":
        mps = ComplexLPS(bond_dimension, learning_rate, batch_size, 
                          n_iter, verbose=False, random_state=rng, mu=2)
    else:
        print('Ansatz choice not valid')
    
    #train MPS
    begin = time.time()  
    mps.fit(X)
    accuracy=mps.likelihood(X)
    accuracy_test=mps.likelihood(X_test)
    time_elapsed = time.time()-begin
    
    print("Negative log likelihood = %.3f" % (accuracy))
    print("Negative log likelihood test = %.3f" % (accuracy_test))
    print("Time elapsed = %.2fs" %(time_elapsed))

    if save:
        name='mpsresult'+'_'+str(datasetload)+'_'+str(ansatz)+'_'+\
            str(batch_size)+'_'+str(learning_rate)+'_'+\
            str(bond_dimension)+'_'+str(n_iter)+'_'+str(accuracy)+'_'+str(accuracy_test)
        with open(path+name, 'wb') as f:
            pickle.dump([mps, datasetload, ansatz, bond_dimension, learning_rate, batch_size, 
                          n_iter, accuracy, accuracy_test], f)

if __name__ == '__main__':
    # Main program : initialize with options from command line and run
    init(*sys.argv[1::])
    run()