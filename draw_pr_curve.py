#!/usr/bin/python

import numpy as np
import matplotlib  
matplotlib.use("Agg")  
import numpy as np  
import matplotlib.pyplot as plt  

def calculate_pr(sameface_result_file,difface_result_file):
    
    threshs = np.linspace(0.1,1,20)
    fn = np.zeros(20)
    tp = np.zeros(20)
    tn = np.zeros(20)
    fp = np.zeros(20)

    with open(sameface_result_file,'r') as fs:
        for line in fs:
            cardpath,facepath,score = line.split('\t')
            score = float(score)
        
            for i in range(20):
                if score < threshs[i]:
                   fn[i] += 1
                else:
                   tp[i] += 1        

    with open(difface_result_file,'r') as fs:
        for line in fs:
            cardpath,facepath,score = line.split('\t')
            score = float(score)

            for i in range(20):
                if score < threshs[i]:
                   tn[i] += 1
                else:
                   fp[i] += 1           
    
    return fn,tp,tn,fp

def draw_analysis_figure(fn,tp,tn,fp):
    
    plt.figure(1)   
    plt.title('Precision/Recall Curve') 
    plt.xlabel('Recall')
    plt.ylabel('Precision')  
    
    x=[]
    y=[]

    recall = tp/(tp+fn)
    precision = tp/(tp+fp)
 
    plt.figure(1)  
    plt.plot(recall, precision)  
    plt.show()  
    plt.savefig('p-r.png')  


if __name__=="__main__":

    sameface_result_file = "samefacesim.txt"
    difface_result_file = "diffacesim.txt"

    fn,tp,tn,fp = calculate_pr(sameface_result_file,difface_result_file)
    draw_analysis_figure(fn,tp,tn,fp)