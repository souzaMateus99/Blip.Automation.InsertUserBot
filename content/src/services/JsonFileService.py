import os
import json

class JsonFileService:
    def __init__(self, partial_filepath) -> None:
        base_path = self.__get_base_path()
        self.filepath = base_path + partial_filepath
    
    def do_read_config_file(self):        
        file = open(file=self.filepath, mode='r')
        
        return json.load(file)

    def __get_base_path(self):
        script_path = os.path.realpath(__file__)
        
        file_split = __file__.split('/')

        if len(file_split) == 1:
            file_split = __file__.split('\\')

        return script_path.replace('src', '').replace('services', '').replace('\\\\', '').replace('//', '').replace(file_split[-1], '')