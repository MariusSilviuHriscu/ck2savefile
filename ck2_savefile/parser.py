from pathlib import Path
import typing

from ck2_savefile.info_representation import (
    InfoRepresentation,
    OneLineKeyListInfo,
    OneLineListInfo,
    OneLineKeyValueInfo,
    DictInfo,
    MultiKeyValueInfo,
    OptionalKeyDict
    )
from ck2_savefile.response import ParseResponse

DataGeneratorFuncType = typing.Callable[...,typing.Generator[InfoRepresentation, None , None]]

class SaveFileParser:
    
    def __init__(self , file_path : Path ):
        self.path = file_path
    @staticmethod
    def read_file_line_by_line(file_path : Path):
        with open(file_path, 'r') as file:
            for index , line in enumerate(file):
                yield index , line
    
    def one_line_data(self , line) -> bool:
        return '"' in line
    def _parse_data(self, 
                    generator : typing.Generator[str, None, None]
                    ) -> typing.Generator[InfoRepresentation , None ,None]:
        for index , line in generator:
        
            if OneLineKeyValueInfo.corresponds(raw_info = line):
                    
                new_value = OneLineKeyValueInfo.create(raw_info = line, index= index)
                yield new_value
                continue
            
            if MultiKeyValueInfo.corresponds(raw_info= line):
                
                new_value = MultiKeyValueInfo.create(raw_info= line, index= index)
                yield new_value
                continue
            
            if OneLineListInfo.corresponds(raw_info = line):
                
                new_value = OneLineListInfo.create(raw_info = line, index= index)
                yield new_value
                continue
            
            if OneLineKeyListInfo.corresponds(raw_info = line):
                
                new_value = OneLineKeyListInfo.create(raw_info = line, index= index)
                yield new_value
                continue
            
            if DictInfo.corresponds(raw_info = line):
                
                new_value = DictInfo.create(raw_key_data = line,start_index=index , ck2generator = generator)
                yield new_value
                continue
            
            if OptionalKeyDict.corresponds(raw_info = line):
                
                new_value = OptionalKeyDict.create(raw_key_data = line,start_index=index , ck2generator = generator)
                yield new_value
                continue
    def get_path_generator(self) -> DataGeneratorFuncType:
        def func():
            generator = SaveFileParser.read_file_line_by_line(file_path = self.path)
            next(generator)
            return self._parse_data(generator = generator)
        
        return func
            
    def parse_data(self) -> ParseResponse:
        generator = SaveFileParser.read_file_line_by_line(file_path = self.path)
        first_line = next(generator) 
        
        return ParseResponse(
            first_line = first_line,
            response_generator_func = self.get_path_generator()
            )
        
        
        