"""
DESCRIPTION
Preprocesses audio data before sending to Neural Network

See demo in in main()


MIT License

Copyright (c) 2018  The-Instrumental-Specialists

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import neuralnet_02 as NN
import numpy as np
import os
import glob
import json
import time



import scipy
import matplotlib.pylab as plt
import scipy.io.wavfile as wavfile
import scipy.fftpack


def processFile(filename,length = 1024,q=4,error=True,fs_in=44100,plot = False):
    """returns one sided FFT amplitudes of filename
        filename (string): ex) 'sax.wav'
        length (int): Number of datapoints of one-sided fft (must be even,preferably a power of 2)
        q (int): (optional argument) Downsampling Rate 
        error (bool): (optional argument) if True, throw ValueError if fs of filename != fs_in        fs_expected (int): (optional argument) Used when error is True to specify sample rate of file
        fs_in (int): (optional argument) sample rate to compare to when error is true.
        plot (bool): (optional argument) plots the one sided FFT if True, otherwise does not plot
        
        Note: length < total_time*fs//(2*q)
        Ex) length = 1024 < (0.25sec)*(44100Hz)//(2*4) = 1378
    """
    #fs = sample rate, sound = multichannel sound signal
    fs1, sound = wavfile.read(filename)
    if error and fs1 != fs_in:
        raise ValueError('Sampling rate should be ' + str(fs_in) + ' for: ' + filename)
    sig1 = sound[:,0] #left channel
    
    fs2, sig2 = downsample(sig1,fs1,q)
    N2 = len(sig2)
    sig3 = sig2[N2//2-length:N2//2+length]

    FFT = abs(scipy.fft(sig3))
    FFT_side = FFT[range(len(FFT)//2)]
    if len(FFT_side) != length:
        print('ERROR MESSAGE DETAILS')
        print('filename: ' + filename)
        print('length = ' + str(length))
        print('fs_in = ' + str(fs_in))
        print('q = ' + str(q))
        total_time = len(sig1)/fs1
        print('total_time =  ' + str(total_time))
        print('Please check: length < total_time*fs//(2*q)')
        print('Check: ' + str(length) + ' < ' + str(total_time*fs1//(2*q)))
        raise ValueError('Length FFT_side != length: ' + str(len(FFT_side)) + ' != ' + str(length))
        
    
    temp = []
    # normalize FFT
    for value in FFT_side:
        temp.append(value/sum(FFT_side))
    FFT_side = np.array(temp)
    if plot == True:
        freqs = scipy.fftpack.fftfreq(sig3.size, Ts4)
        freqs_side = np.array(freqs[range(N4//2)])
        plt.plot(freqs_side,FFT_side) # plotting the complete fft spectrum
        plt.show()
 
    #print(len(FFT_side))
    return FFT_side



def downsample(sig,fs,q):
    """
    sig (list,array): sound/data signal
    q (int): downsample factor
    """
    N = len(sig)//q
    new_sig = []
    for i in range(len(sig)//q):
        new_sig.append(sig[i*q])
    new_sig = np.array(new_sig)
    return (fs//q,new_sig)

class Preprocess:
    def __init__(self):
        """data_file (string): contains the file to load or store data, ex)data.txt
            process (bool): if False, load data from data_file,
                            if True, process data in directory & store in data_file
            directory (string): (optional) directory of data to be processed
        """
        # Ex) self.output['cel']: np.array([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        self.output = {}
        
         # directory names are names of instruments
        #self.dirs =
        # ['cel', 'cla', 'flu', 'gac', 'gel', 'org', 'pia', 'sax', 'tru', 'vio', 'voi']
        self.dirs = [] # list of names of subdirectories in directory

        # example: self.files['sax'] =
        # IRMAS-TrainingData\sax\006__[sax][nod][cla]1686__1.wav
        self.files = {} # dictionary of dir:[file,file,file]

        # self.data = {} # dictionary of dir:[input_nodes,input_nodes]

        # self.X is dictionary of dir:[input_nodes1,input_nodes2]
        # self.Y is dictionary of dir:[output_nodes1,output_nodes2]
        # self.Y corresponds to self.X
        self.X = [] # list of input vectors
        self.Y = [] # list of output vectors

        #if process == False:
            #self.loadData(data_file)
        #else: #process == True:
            #self.processData(data_file,directory,comment)

    def getXY(self):
        """Returns X (List of Input Vectors), and Y (List of Output Vectors)
            for preprocessed data
            ex) X = [[0,0],[0,1],[1,0],[1,1]]
            ex) Y = [[0],[1],[1],[0]]
        """
        return (self.X,self.Y)
    
    def getFileList(self):
        """Returns a dictionary with key:value 'Output Name':[file list]
            ex) {'sax':['sax1.wav','sax2.wav','sax3.wav']}
        """
        return self.files

    def getOutputVectors(self):
        """ Returns a dictionary with key:value 'OutputName':output vector
        Ex) output['cel']: np.array([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        """
        return self.output

    def getOutputNames(self):
        """Returns a list of the names of the output vectors
        ex) ['cel', 'cla', 'flu', 'gac', 'gel', 'org', 'pia', 'sax', 'tru', 'vio', 'voi']
        """
        return self.dirs

    def loadData(self,data_file):
        """Loads the data in data_file into Trainer"""
        #Load the data from the json
        with open(data_file) as json_file:  
            data = json.load(json_file)

        # Clear all instance variables
        self.dirs = []
        self.files = {}
        self.X = []
        self.Y = []
        self.output = {}

        # stored the data into the instance variables
        self.dirs = data['dirs'] #good
        self.files = data['files'] # good
        
        # self.output is a dict() with string:np.array
        output = data['output']
        for e in output:
            self.output[e] = np.array(output[e]) # -> fine
        #self.X is a list of np.arrays
        X = data['X']
        for x in X:
            self.X.append(np.array(x))# -> fine
        #self.Y is a list of np.arrays
        Y = data['Y']
        for y in Y:
            self.Y.append(list(y))# -> fine
        #Test prints, uncomment to test if data looks correct
        #print('self.dirs = ' + str(self.dirs))
        #print()
        #print('self.files = ' + str(self.files))
        #print()
        #print('self.output = ' + str(self.output))
        #print()
        #print('self.X = ' + str(self.X))
        #print()
        #print('self.Y = ' + str(self.Y))
        #print()
        print('Preprocessed data loaded from ' + str(data_file))
        print(data['comment'])
        return 
        
        

    def processData(self,data_file,directory,comment = '',length = 1024,q=4,error=True,fs_in=44100):
        """Processes the data in directory and stores it in data_file
            directory (string): folder of data to be processed
            data_file (string): name of file for data to be stored ex) data.txt
            comment (string): optional message to be stored with data
            length (int): Number of datapoints of one-sided fft (must be even,preferably a power of 2)
            q (int): Downsampling Rate (must be even, preferably power of 2)
            fs_in (int): (optional argument) sample rate to compare to when error is true.
            error (bool): (optional argument) if True, throw ValueError if fs of filename != fs_in        fs_expected (int): (optional argument) Used when error is True to specify sample rate of file
        
            Note: length < total_time*fs/(q)
            Ex) length = 1024 < (0.25sec)*(44100Hz)/(4) = 2756
        """
        self.dirs = [name for name in os.listdir(directory)
            if os.path.isdir(os.path.join(directory, name))]

        # directory names are names of instruments
        #self.dirs =
        # ['cel', 'cla', 'flu', 'gac', 'gel', 'org', 'pia', 'sax', 'tru', 'vio', 'voi']
        self.dirs = [name for name in os.listdir(directory)
            if os.path.isdir(os.path.join(directory, name))]
        
        # example: self.files['sax'] =
        # IRMAS-TrainingData\sax\006__[sax][nod][cla]1686__1.wav
        self.files = {}
        for d in self.dirs:
            self.files[d] = [] 
            sub_dir = os.path.join(directory, d)
            for filename in glob.glob(os.path.join(sub_dir, '*.wav')):
                self.files[d].append(filename)

        # Ex) self.output['cel']: np.array([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        i = 0
        for name in self.dirs:
            temp = []
            for j in range(len(self.dirs)):
                if i == j:
                    temp.append(1)
                else:
                    temp.append(0)
            self.output[name] = np.array(temp)
            i +=1


        #self.X = [] # list of input vectors
        #self.Y = [] # list of output vectors
        for name in self.dirs:
            t1 = time.time()
            for file in self.files[name]:
                input_vector = processFile(file,length = 1024,q=4,error=True,fs_in=44100,plot = False,)
                self.X.append(input_vector)
                self.Y.append(self.output[name])
            print('Time take to process '+str(name)+ ': ' + str((time.time()-t1)/60) + 'min')

        # Now we can store all of the data in a json
        # Need to store self.X, self.Y, self.dirs,self.output,self.files,self.data
        # self.dirs is a list of strings -> fine
        # self.files is a dict() with string:string -> fine
        # self.output is a dict() with string:np.array
        output = {}
        for d in self.output:
            out_list = []
            for value in self.output[d]:
                out_list.append(int(value))
            output[d] = out_list # -> fine
        #self.X is a list of np.arrays
        X = []
        for i in range(len(self.X)):
            x = []
            for ele in self.X[i]:
                x.append(float(ele))
            X.append(x) # -> fine
        #self.Y is a list of np.arrays
        Y = []
        for i in range(len(self.Y)):
            y = []
            for ele in self.Y[i]:
                y.append(float(ele))
            Y.append(y) # -> fine
            
        store = {}
        store['dirs'] = self.dirs # good
        store['output'] = output # good
        store['files'] = self.files # good
        store['X'] = X # good
        store['Y'] = Y # good
        store['comment'] = comment
        with open(data_file, 'w') as outfile:
            json.dump(store, outfile)
        print('Preprocessed data stored in ' + str(data_file))
        return

        

        
        








def main():
    # Note: Preprocessed data should be in folder preprocessed
    #P = Preprocess('preprocessed/test_01.txt',process=True,directory='phil_temp_03',comment = 'Hello World')
    P = Preprocess()
    #P.processData('preprocessed/test_01.txt',directory='phil_temp_03',comment = 'Hello World')
    P.loadData('preprocessed/rohan_02.rtf')
    X, Y = P.getXY()
    net = NN.NeuralNetwork([1024,256,64,12],'sigmoid')
    net.trainWithPlots(X,Y,learning_rate=0.01,intervals = 10)

    # Test print functions, these print statements can be used to figure
    # out how to use code
    # X, Y = P.getXY()
    # files = P.getFileList()
    # output_vectors = P.getOutputVectors()
    # output_names = P.getOutputNames()
    # print()
    # print('X = ' + str(X))
    # print()
    # print('Y = ' + str(Y))
    # print()
    # print('File List = ' + str(files))
    # print()
    # print('Output Vectors = ' + str(output_vectors))
    # print()
    # print('Output Names = ' + str(output_names))

    
if __name__ == '__main__':
    main()