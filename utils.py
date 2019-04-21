
from scipy import signal
import numpy as np
import h5py
import soundfile as sf
import os 

#Feature extraction
def feature_extraction(x,fs):

    frame_length_s = 0.04 # window length in seconds
    frame_length = int(fs*frame_length_s) # 40ms window length in samples
    # set an overlap ratio of 50 %
    hop_length = frame_length//2

    # Compute STFT
    _,_,X = signal.stft(x, noverlap=hop_length, fs=fs,nperseg=frame_length)
    number_frequencies, number_time_frames = X.shape
    phaseInfo = np.angle(X)
    X = np.abs(X)

    # Segmentation
    sample_length_s = 0.8 # segment length in seconds
    sample_length = int(sample_length_s/frame_length_s) # ~1s in samples

    # Trim the frames that can't be fitted into the segment size
    trimmed_X = X[:, :-(number_time_frames%sample_length)]
    trimmed_phaseInfo = phaseInfo[:, :-(number_time_frames%sample_length)]

    # Segmentation (number of freqs x number of frames x number of segment x 1). The last dimension is 'channel'.
    features = trimmed_X.reshape((number_frequencies,sample_length,-1,1), order='F')
    # Transpose the feature to be in form (number of segment x number of freqs x number of frames x 1)
    return trimmed_phaseInfo,features.transpose((2,0,1,3))

def get_features(dir_name):
    # loop through the directory and extract features from 
    # the audio files 
    features = []
    trimmed_phases = []
    for filename in os.listdir(dir_name):
        if filename.endswith(".wav"):
            x,fs = sf.read(os.path.join(dir_name, filename))
            phase, feature = feature_extraction(x, fs)
            features.append(feature)
            trimmed_phases.append(phase)
    features = np.vstack(features)
    return features, trimmed_phases


def save_features(features_filename, X_train,X_test,y_train,y_test):
    # used to save the features into hdf5 file
    with h5py.File(features_filename, 'w') as f:
        f.create_dataset('X_train', data=X_train)
        f.create_dataset('X_test', data=X_test)
        f.create_dataset('y_train', data=y_train)
        f.create_dataset('y_test', data=y_test)
    return X_train, X_test, y_train, y_test


def read_features(features_filename):
    # use to read  the features from hdf5 file
    with h5py.File(features_filename, 'r') as f:
            X_train = f.get('X_train').value
            X_test = f.get('X_test').value
            y_train = f.get('y_train').value
            y_test = f.get('y_test').value
    return X_train, y_train, X_test, y_test