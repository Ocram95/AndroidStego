import os
import numpy as np
import argparse
from typing import Dict

import cv2
from PIL import Image, UnidentifiedImageError
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from mutagen.wave import WAVE
from mutagen.flac import FLAC


class MediaExtractor:
    
    def __init__(self, file_path: str):
        """
        Init the MediaExtractor class

        Parameters
        ----------
        file_path : str
            path of the file to process
        """
        self.file_path = file_path
        
    def get_filesize(self) -> int:
        """
        Get filesize in bytes

        Returns
        -------
        int
            file size in bytes
        """
        return os.path.getsize(self.file_path)
    
    def __get_audio_info(self, file_extension: str) -> Dict:
        """
        Get audio info

        Parameters
        ----------
        file_extension : str
            file extension of the file

        Returns
        -------
        Dict
            with the required information
        """
        if file_extension == '.mp3':
            audio = MP3(self.file_path)
        elif file_extension == '.wav':
            audio = WAVE(self.file_path)
        elif file_extension == '.flac':
            audio = FLAC(self.file_path)
        return {'file': self.file_path,
                'type': file_extension[1:],
                'info':{
                        'duration': audio.info.length,
                        'audio_channels': audio.info.channels,
                        'sample_rate': audio.info.sample_rate,
                        'size_bytes': self.get_filesize()
                        }
                }

    def __get_mp4_info(self, file_extension: str) -> Dict:
        """
        Get video info

        Parameters
        ----------
        file_extension : str
            file extension of the file
            
        Returns
        -------
        Dict
            with the required info
                width and height in pixels, duration of the video, frame per seconds, size in bytes

        Raises
        ------
        ValueError
            Error if the file is not a vide
        """
        cap = cv2.VideoCapture(self.file_path)
        if not cap.isOpened():
            raise ValueError("Error opening video file")

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0  # Duration in seconds

        cap.release()
        return {'file': self.file_path,
                'type': file_extension[1:],
                'info': {
                    'width': width,
                    'height': height,
                    'duration': duration,
                    'fps': fps,
                    'size_bytes': self.get_filesize()
                    }
                }
    
    def __get_image_info(self, file_extension: str) -> Dict:
        """
        Return image info
        
        Parameters
        ----------
        file_extension : str
            file extension of the file
            
        Returns
        -------
        Dict
            with the required info 
                widht and height in pixels, format, size of the file in bytes, mode (gray-scale, RGB, RGBA, etc. see 
                https://pillow.readthedocs.io/en/stable/handbook/concepts.html#concept-modes), and maximum pixel per channel
        """
        try:
            with Image.open(self.file_path) as img:
                img_np = np.array(img)
                
                if len(img_np.shape) == 2: # Grayscale
                    max_pixel_per_channel = [img_np.max()] # Only one channel
                    min_pixel_per_channel = [img_np.min()]
                else:
                    max_pixel_per_channel = img_np.max(axis=(0, 1)) # Max per channel
                    min_pixel_per_channel = img_np.min(axis=(0, 1))
                    
            return {'file': self.file_path,
                    'type': img.format.lower(),
                    'info':{
                        'width': img.width,
                        'height': img.height,
                        'size_bytes': self.get_filesize(),
                        'mode': img.mode,
                        #'max_pixel_per_channel': max_pixel_per_channel,
                        #'min_pixel_per_channel': min_pixel_per_channel
                        }
                    }

        except UnidentifiedImageError as e:
            print(f"[-] Error: {e} - the file should be an image")
        except OSError as e:
            print(f"[-] Error: {e} - error opening the file")
        
    
    def extract_info(self):
        file_extension = os.path.splitext(self.file_path)[1].lower()
        
        if file_extension in ['.jpg', '.jpeg', '.png', '.bmp', '.gif']:
            return self.__get_image_info(file_extension)
        elif file_extension in ['.mp4']:
            return self.__get_mp4_info(file_extension)
        elif file_extension in ['.mp3', '.wav', '.flac']:
            return self.__get_audio_info(file_extension)
        else:
            raise ValueError("Unsupported file type.")
        

if __name__ == '__main__':
    
    path = 'bling.m4a'
    m = MediaExtractor(path)
    print(m.extract_info())