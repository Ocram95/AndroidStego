from pandas import DataFrame
from typing import Dict, Tuple


class StatisticsExtractor:
    
    def __init__(self, data: DataFrame, type: str):
        self.data = data
        self.type = type
    
    def __get_resolutions(self) -> Dict:
        """
        Compute the resolutionc counts for images and videos only

        Returns
        -------
        Dict
            dictionary with (width, height): counter
        """
        
        resolution_counts = self.data.groupby(['width', 'height']).size().reset_index(name='count').sort_values(by='count', ascending=False)
        resolution_dict = dict()
        for index, row in resolution_counts.iterrows():
            resolution_dict[str((row['width'], row['height']))] = row['count']
        
        return {'resolutions': resolution_dict}

    def __get_avg_std(self) -> Tuple:
        """
        Get avg and std of the features

        Returns
        -------
        Tuple
            tuple with mean and std dictionaries
        """
        if self.type == 'video' or self.type == 'audio':
            data = self.data[['duration', 'size_bytes']]
            return {'avg': data.mean().to_dict(), 'std': data.std().to_dict()}
        elif self.type == 'images':
            data = self.data['size_bytes']
            return {'avg': {'size_bytes': data.mean()}, 'std': {'size_bytes': data.std()}}

    def __get_count(self, feature: str) -> Dict:
        """
        Get counter for feature

        Parameters
        ----------
        feature : str
            feature to count

        Returns
        -------
        Dict
            counter of each feature
        """
        return {feature: self.data[feature].value_counts().sort_values(ascending=False).to_dict()}

    def __get_num(self) -> Dict:
        """
        Get number

        Returns
        -------
        Dict
            number of data
        """
        return {'num': self.data.shape[0]}

    def __get_pixels_per_channel(self) -> Dict:
        """_summary_

        Returns
        -------
        Dict
            _description_
        """
        
        max = self.data[['mode', 'max_pixel_per_channel']]
        max.loc[:, 'max_pixel_per_channel'] = max.loc[:, 'max_pixel_per_channel'].astype('str')
        
        min = self.data[['mode', 'min_pixel_per_channel']]
        min.loc[:, 'min_pixel_per_channel'] = min.loc[:, 'min_pixel_per_channel'].astype('str')
        
        return {'max_pixel_per_channel': max.groupby('mode').value_counts().sort_values(ascending=False).to_dict(), 
                'min_pixel_per_channel': min.groupby('mode').value_counts().sort_values(ascending=False).to_dict()}
        
    
    def compute_statistics(self):
        
        if self.type == 'video':
            return self.__get_num(), self.__get_resolutions(), self.__get_avg_std(), self.__get_count(feature='fps')
        elif self.type == 'audio':
            return self.__get_num(), self.__get_count(feature='audio_channels'), self.__get_avg_std(), self.__get_count(feature='sample_rate')
        elif self.type == 'images':
            return self.__get_num(), self.__get_resolutions(), self.__get_avg_std(), self.__get_count(feature='mode')#, self.__get_pixels_per_channel()