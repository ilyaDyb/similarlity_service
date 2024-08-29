import librosa
import numpy as np

"""
There is no difference between the different file extensions.
Both mp3 (compressed) and wav (exact) formats do not have any significant differences.
"""
filename = "tests/computing/test_audios/example01.mp3" # *

y, sr = librosa.load(filename)
hop_length = 512
n_fft = 512

y_harmonic, y_percussive = librosa.effects.hpss(y)#, n_fft=n_fft)
tempo, beat_frames = librosa.beat.beat_track(y=y_percussive, sr=sr)


mfcc = librosa.feature.mfcc(y=y, sr=sr, hop_length=hop_length)#, n_mfcc=13)
# print(mfcc)

mfcc_delta = librosa.feature.delta(mfcc)
# print(mfcc_delta)

beat_mfcc_delta = librosa.util.sync(np.vstack([mfcc, mfcc_delta]), beat_frames)
# print(beat_mfcc_delta)

chromagram = librosa.feature.chroma_cqt(y=y_harmonic, sr=sr)
# print(chromagram)

beat_chroma = librosa.util.sync(chromagram, beat_frames, aggregate=np.median)
# print(beat_chroma)

print("beat_chroma shape:", beat_chroma.shape)
print("beat_mfcc_delta shape:", beat_mfcc_delta.shape)

# if beat_chroma.shape[1] < beat_mfcc_delta.shape[1]:
#     beat_chroma = np.pad(beat_chroma, ((0, 0), (0, beat_mfcc_delta.shape[1] - beat_chroma.shape[1])), mode='constant')
# elif beat_mfcc_delta.shape[1] < beat_chroma.shape[1]:
#     beat_mfcc_delta = np.pad(beat_mfcc_delta, ((0, 0), (0, beat_chroma.shape[1] - beat_mfcc_delta.shape[1])), mode='constant')

# beat_features = np.vstack([beat_chroma, beat_mfcc_delta])
# # print(beat_features)

# mfcc_mean = np.mean(mfcc, axis=1)
# mfcc_std = np.std(mfcc, axis=1)

# chroma_mean = np.mean(chromagram, axis=1)
# chroma_std = np.std(chromagram, axis=1)
# print(mfcc_std)
# print(chroma_std)
# song_signature1 = np.hstack([mfcc_mean, mfcc_std, chroma_mean, chroma_std])
# song_signature2 = np.hstack([mfcc_mean, mfcc_std, chroma_mean, chroma_std])
# # print(song_signature)
# from scipy.spatial.distance import euclidean

# distance = euclidean(song_signature1, song_signature2)
# print(distance)
spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)
zcr = librosa.feature.zero_crossing_rate(y)

mfcc_mean = np.mean(mfcc, axis=1)
mfcc_std = np.std(mfcc, axis=1)

chroma_mean = np.mean(chromagram, axis=1)
chroma_std = np.std(chromagram, axis=1)

spectral_centroid_mean = np.mean(spectral_centroid, axis=1)
spectral_bandwidth_mean = np.mean(spectral_bandwidth, axis=1)
zcr_mean = np.mean(zcr, axis=1)


song_signature = np.hstack([
    mfcc_mean, mfcc_std, 
    chroma_mean, chroma_std, 
    spectral_centroid_mean, 
    spectral_bandwidth_mean, 
    zcr_mean
])
from scipy.spatial.distance import euclidean
# print(song_signature)
distance = euclidean(song_signature, song_signature)
# print("Distance between songs:", distance)
sign = [-1.47444916e+02,  9.22828140e+01,  3.13079987e+01,  3.32870560e+01,
  1.17695599e+01,  1.16937768e+00,  9.94367409e+00, -1.28817701e+00,
 -9.02728081e+00,  9.66639042e+00, -5.10154295e+00,  5.25324011e+00,
  4.23911619e+00,  2.49331594e+00,  2.61623645e+00,  1.87899613e+00,
 -2.55546427e+00,  1.14740658e+00, -6.74656105e+00,  2.62351489e+00,
  1.01182907e+02,  3.73664551e+01,  2.76871986e+01,  1.81662769e+01,
  1.46346254e+01,  1.76834412e+01,  1.56287899e+01,  1.41261721e+01,
  1.43880615e+01,  1.37262344e+01,  1.10697184e+01,  9.42771721e+00,
  9.92797756e+00,  8.41138554e+00,  8.96286106e+00,  8.54643250e+00,
  7.73079252e+00,  7.47657394e+00,  7.05090714e+00,  7.66599321e+00,
  7.38309681e-01,  3.35730404e-01,  2.72117853e-01,  1.39205128e-01,
  2.61056811e-01,  4.62897807e-01,  4.04991746e-01,  4.33984041e-01,
  3.53556126e-01,  4.11511213e-01,  2.30712876e-01,  3.74580622e-01,
  2.57785738e-01,  2.40177333e-01,  2.13837221e-01,  1.42253384e-01,
  1.92956820e-01,  3.89581949e-01,  3.31362784e-01,  2.86158085e-01,
  3.18389028e-01,  3.06180447e-01,  2.09767759e-01,  2.63603538e-01,
  1.94382830e+03,  2.52419607e+03,  5.69282632e-02]

sign_str = ','.join(map(str, sign))
print(sign_str)
print(type(sign_str))
sign_ = list(map(float, sign_str.split(",")))
from scipy.spatial.distance import euclidean
distance = euclidean(sign_, sign_)
print(distance)