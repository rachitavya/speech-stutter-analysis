import os
import pathlib
import subprocess
import requests
import numpy as np
import librosa
import soundfile as sf

episode_uri = 'SEP-28k_episodes.csv'
wav_dir ='[WAV_DIR]'

table = np.loadtxt(episode_uri, dtype=str, delimiter=",")
urls = table[:,2]
n_items = len(urls)

audio_types = [".mp3", ".m4a", ".mp4"]

for i in range(n_items):
    # Get show/episode IDs
    show_abrev = table[i,-2]
    ep_idx = table[i,-1]
    episode_url = table[i,2]
    ext = ''
    for ext in audio_types:
        if ext in episode_url:
            break
    episode_dir = pathlib.Path(f"{wav_dir}/{show_abrev}/")
    os.makedirs(episode_dir, exist_ok=True)

    # Get file paths
    audio_path_orig = pathlib.Path(f"{episode_dir}/{ep_idx}{ext}")
    wav_path = pathlib.Path(f"{episode_dir}/{ep_idx}.wav")
    # Check if this file has already been downloaded
    if os.path.exists(wav_path):
        continue
    
    try:
        print("Processing", show_abrev, ep_idx)
        # Download raw audio file. This could be parallelized.
        if not os.path.exists(audio_path_orig):
            print(f"Downloading {episode_url} to {audio_path_orig}")
            response = requests.get(episode_url)
            if response.status_code == 200:
                with open(audio_path_orig, 'wb') as file:
                    file.write(response.content)
                    print('hello')
        else:
            print(f"File {audio_path_orig} already exists, skipping download.")

        # Convert to 16khz mono wav file
        # Replace with the path to your audio file
        audio, sample_rate = librosa.load(audio_path_orig, sr=None)  # sr=None to preserve the original sample rate

        # Resample to 16kHz
        target_sample_rate = 16000
        audio = librosa.resample(audio,orig_sr=sample_rate,target_sr= target_sample_rate)
        
        # Convert to mono (if not already)
        if audio.ndim == 2:
            audio = librosa.to_mono(audio)

        # Save as a WAV file
        sf.write(wav_path, audio, target_sample_rate)

        print(f"Audio file saved to {wav_path}")

        os.remove(audio_path_orig)
    
    except Exception as e:
        print('error',e)
        
        
