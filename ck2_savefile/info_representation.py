from pathlib import Path
import typing
from dataclasses import dataclass

@dataclass
class LastPositionData:
    last_line_index : int
    last_line_start : int
    last_line_end : int
    

@dataclass
class SimpleInfoChange :
    line_number : int
    new_line : str

@dataclass
class ComplexChanges:
    insertion_index : int
    insertion_generator : typing.Generator[str, None, None]
    

class InfoRepresentation(typing.Protocol):
    
    @staticmethod
    def create(raw_into : str) -> typing.Self:
        pass
    
    def to_raw_string(self) -> typing.Generator[str , None , None] | str:
        pass
    @staticmethod
    def corresponds(raw_info:str) ->bool:
        pass
    def change_value(self , other : typing.Any) -> list[tuple[int , str]]:
        pass
    
    @property
    def last_line_position(self) -> LastPositionData:
        pass
    
    @staticmethod
    def create_from_dict(input_dict : dict) -> typing.Self:
        pass

    
class OneLineKeyValueInfo:
    def __init__(self ,
                 index : int ,
                 data_key : str ,
                 data_value : str , 
                 start_spaces : int ,
                 end_spaces : int):
        self.index = index
        self.data_key = data_key
        self.data_value = data_value
        self.start_spaces= start_spaces
        self.end_spaces = end_spaces
    @staticmethod
    def create(raw_info : str , index : int) -> typing.Self:
        start_spaces = raw_info.count('\t')
        end_spaces = raw_info.count('\n')
        data_name , data_value = raw_info.replace('\t' , '').replace('\n', '').split('=')
        return OneLineKeyValueInfo(
            index = index ,
            data_key = data_name,
            data_value = data_value,
            start_spaces = start_spaces, 
            end_spaces= end_spaces
        )
    
    @staticmethod
    def corresponds(raw_info : str) -> bool:
        
        return ('=' in raw_info and
                not raw_info.endswith('=\n') and
                "{" not in raw_info and
                raw_info.count('=') == 1
        )
    
    def to_raw_string(self) -> str:
        return "\t"*self.start_spaces + f'{self.data_key}={self.data_value}' + "\n"*self.end_spaces
    
    def change_value(self , value : str) -> SimpleInfoChange:
        self.data_value = value
        
        return SimpleInfoChange(
            line_number = self.index,
            new_line = self.to_raw_string()
        )
    
    @property
    def last_line_position(self) -> LastPositionData:
        return LastPositionData(
            last_line_index = self.index,
            last_line_start = self.start_spaces,
            last_line_end = self.end_spaces
        )
    

        
class MultiKeyValueInfo():
    def __init__(self,
                 index : int,
                 values : list[OneLineKeyValueInfo],
                 start_space : int ,
                 end_spaces : int ) :
        self.index = index
        self.values = values
        self.start_space = start_space
        self.end_spaces = end_spaces
    
    @staticmethod
    def create(raw_info : str , index : int) -> typing.Self :
        
        start_spaces = raw_info.count('\t')
        end_spaces = raw_info.count('\n')
        
        data_raw = raw_info.replace('\n' , '').replace('\t ', '')
        pairs = data_raw.split(' ')
        data = [OneLineKeyValueInfo.create(raw_info=x , index = index) 
                for x in pairs if '=' in x]

        
        return MultiKeyValueInfo(
            index = index,
            values=data,
            start_space=start_spaces,
            end_spaces=end_spaces
        )
    
    @staticmethod
    def corresponds(raw_info : str) -> bool:
    
        return ('=' in raw_info and
                    not raw_info.endswith('=\n') and
                    "{" not in raw_info and
                    raw_info.count('=') != 1
            )
    def to_raw_string(self) -> str :
        return ('\t' * self.start_space +
                ' '.join((x.to_raw_string() for x in self.values)) +
                '\n' * self.end_spaces
        )
    def change(self, key : str , new_value : str)-> SimpleInfoChange:
        for value in self.values:
            if value.data_key == key:
                value.data_value = new_value
        
                return SimpleInfoChange(
                    line_number = self.index,
                    new_line = self.to_raw_string()
                )
        raise Exception("Couldn't find the key in the info .")
    @property
    def last_line_position(self) -> LastPositionData:
        return LastPositionData(
            last_line_index = self.index,
            last_line_start = self.start_space,
            last_line_end = self.end_spaces
        )

class OneLineListInfo:
    def __init__(self ,
                 index : int, 
                 info_list : list[str],
                 start_spaces : int ,
                 end_spaces : int
                 ):
        self.index = index
        self.info_list = info_list
        self.start_spaces = start_spaces
        self.end_spaces = end_spaces
    
    @staticmethod
    def create(raw_info : str , index : int) -> typing.Self:
        
        start_spaces = raw_info.count('\t')
        end_spaces = raw_info.count('\n')
        
        data = raw_info.replace('\t' , '').replace('\n' , '').split(' ')
        
        return OneLineListInfo(index= index ,
                               info_list = data,
                               start_spaces = start_spaces,
                               end_spaces = end_spaces
                               )
    @staticmethod
    def corresponds(raw_info : str) -> bool:
        
        return '=' not in raw_info and raw_info.count(' ') > 1
    
    def to_raw_string(self) -> str:
        return '\t' * self.start_spaces + ' '.join(self.info_list) + '\n' * self.end_spaces
    
    def change_value(self , other_list : list[str])-> SimpleInfoChange:
        self.info_list = other_list
        
        return SimpleInfoChange(
            line_number = self.index,
            new_line = self.to_raw_string()
        )
    @property
    def last_line_position(self) -> LastPositionData:
        return LastPositionData(
            last_line_index = self.index,
            last_line_start = self.start_spaces,
            last_line_end = self.end_spaces
        )

class OneLineKeyListInfo:
    
    def __init__(self ,
                 index : int ,
                 data_key : str ,
                 data_list : OneLineListInfo,
                 start_spaces : int ,
                 end_spaces : int):
        self.index = index
        self.data_key = data_key
        self.data_list = data_list
        self.start_spaces = start_spaces
        self.end_spaces = end_spaces
    @staticmethod
    def create(raw_info : str , index : int) -> typing.Self:
        
        start_spaces = raw_info.count('\t')
        end_spaces = raw_info.count('\n')
        
        data_key , data_list_str = raw_info.replace('\t' , '').replace('\n' , '').split('=')
        data_list = OneLineListInfo.create(
                    raw_info = data_list_str.replace('{','\t').replace('}','\n'),
                    index = index
        )
        return OneLineKeyListInfo(
            index = index ,
            data_key = data_key ,
            data_list = data_list,
            start_spaces=start_spaces,
            end_spaces=end_spaces
        )
    
    @staticmethod
    def corresponds(raw_info : str) -> bool:
        return '=' in raw_info and '{' in raw_info
    def to_raw_string(self) -> str:
        data_list_str = self.data_list.to_raw_string().replace('\t','{').replace('\n','}')
        
        return "\t" *self.start_spaces + f'{self.data_key}={data_list_str}' + "\n"*self.end_spaces
    def change_value(self , other_list : list[str])-> SimpleInfoChange:
        self.data_list = other_list
        
        return SimpleInfoChange(
            line_number = self.index,
            new_line = self.to_raw_string()
        )
    @property
    def last_line_position(self) -> LastPositionData:
        return LastPositionData(
            last_line_index = self.index,
            last_line_start = self.start_spaces,
            last_line_end = self.end_spaces
        )
class DictInfo:
    
    def __init__(self ,
                 start_index : int,
                 end_index : int ,
                 key : str ,
                 value : list[InfoRepresentation] ,#list[typing.Self | OneLineKeyListInfo | OneLineListInfo | OneLineKeyValueInfo],
                 start_spaces : int,
                 end_spaces : int
                 ):
        self.start_index = start_index
        self.end_index = end_index
        self.key = key
        self.value = value
        self.start_spaces = start_spaces
        self.end_spaces = end_spaces
    
    @staticmethod
    def corresponds(raw_info : str):
        
        return raw_info[-2::] == '=\n'

    @staticmethod
    def create( raw_key_data :str,start_index : int , ck2generator : typing.Generator[str,None,None] ) -> typing.Self:
        
        start_spaces = raw_key_data.count('\t')
        end_spaces = raw_key_data.count('\n')
        
        key_data = raw_key_data.replace('\n','').replace('\t','').replace('=','')
        
        dict_data = []
        
        index_paranthesis , open_parenthesis = next(ck2generator)
        
        if not open_parenthesis.endswith('{\n'):
            raise ValueError(f'Expected a curly bracket but only got {open_parenthesis}')
        
        for index,line in ck2generator:
            
            if OneLineKeyValueInfo.corresponds(raw_info = line):
                
                new_value = OneLineKeyValueInfo.create(raw_info = line , index = index)
                dict_data.append(new_value)
            
            if MultiKeyValueInfo.corresponds(raw_info= line):
                
                new_value = MultiKeyValueInfo.create(raw_info= line , index = index)
                dict_data.append(new_value)
            
            if OneLineListInfo.corresponds(raw_info = line):
                
                new_value = OneLineListInfo.create(raw_info = line, index = index)
                dict_data.append(new_value)
            
            if OneLineKeyListInfo.corresponds(raw_info = line):
                
                new_value = OneLineKeyListInfo.create(raw_info = line, index = index)
                dict_data.append(new_value)
            
            if OptionalKeyDict.corresponds(raw_info=line):
                new_value = OptionalKeyDict.create(first_line = line,start_index = index , ck2generator = ck2generator)
                dict_data.append(new_value)
            
            if DictInfo.corresponds(raw_info = line):
                
                new_value = DictInfo.create(raw_key_data = line , start_index= index, ck2generator = ck2generator)
                dict_data.append(new_value)
            
            if line.endswith('}\n') and '{' not in line:
                return DictInfo(
                    start_index = start_index ,
                    end_index = index ,
                    key = key_data ,
                    value = dict_data,
                    start_spaces= start_spaces,
                    end_spaces = end_spaces
                )
        raise Exception('something is wrong !')
    
    def to_raw_string(self) -> typing.Generator[str , None , None]:
        
        first_line : str = '\t' * self.start_spaces + f'{self.key}=' + '\n' * self.end_spaces
        open_paranthesis : str = '\t' * self.start_spaces + '{' + '\n' * self.end_spaces
        
        yield first_line
        yield open_paranthesis
        
        for value in self.value :
            
            raw_string = value.to_raw_string()
            if isinstance(raw_string , str):
                yield raw_string
            else:
                yield from raw_string
        
        end_parenthesis : str = '\t' * self.start_spaces + '}' + '\n' * self.end_spaces
        
        
        yield end_parenthesis
    @property
    def last_line_position(self) -> LastPositionData:
        return LastPositionData(
            last_line_index = self.last_line_position,
            last_line_start = self.start_spaces,
            last_line_end = self.end_spaces
        )
    def _extend_one_line_key_value_info(self ,
                                        input : dict |  OneLineKeyValueInfo,
                                        last_line_data : LastPositionData
                                        ) -> ComplexChanges:
        
        if isinstance(input , OneLineKeyListInfo):
            
            input.end_spaces = last_line_data.last_line_end
            input.start_spaces = last_line_data.last_line_start
            
            return ComplexChanges(
                insertion_index = last_line_data.last_line_index + 1,
                insertion_generator = (x for x in [input.to_raw_string()])
            )
        
        new_line = OneLineKeyValueInfo(
            index = last_line_data.last_line_index + 1 ,
            data_key = input.get('data_key'),
            data_value= input.get('data_value'),
            start_spaces= last_line_data.last_line_start ,
            end_spaces = last_line_data.last_line_end
        )
        
        return ComplexChanges(
            insertion_index = new_line.index,
            insertion_generator= (x for x in [new_line.to_raw_string()])
        )
    def _extend_dict_info(self, 
                          input : dict | typing.Self ,
                          last_line_data : LastPositionData
                          ) -> ComplexChanges:
        if isinstance(input,dict):
            pass
        
    def extend(self , input : dict | InfoRepresentation , class_type : typing.Type[InfoRepresentation]) -> ComplexChanges:
        final_value = self.value[-1]
        last_line_data = final_value.last_line_position 
        if issubclass(class_type, OneLineKeyValueInfo):
            
            return self._extend_one_line_key_value_info(input = input ,
                                                        last_line_data = last_line_data
                                                        )
        if issubclass(class_type , DictInfo):
            pass
            
    
    

class OptionalKeyDict:
    
    def __init__(self ,
                 start_index : int,
                 end_index : int ,
                 first_line_start : int ,
                 last_line_start: int ,
                 value : list[typing.Self | OneLineKeyListInfo | OneLineListInfo | OneLineKeyValueInfo | DictInfo],
                 key : typing.Optional[str] = None ):
        
        self.start_index = start_index
        self.end_index = end_index
        self.first_line_start = first_line_start
        self.last_line_start = last_line_start
        self.value= value
        self.key= key
    
    @staticmethod
    def corresponds(raw_info : str):
        
        return raw_info.endswith('{\n') or raw_info.endswith('{\n')
    
    @staticmethod
    def create(first_line : str,start_index: int, ck2generator : typing.Generator[str,None,None] ) -> typing.Self:
        
        first_line_start = first_line.count('\t')
        
        key = None
        
        if '=' in first_line:
            
            key = first_line.split('=')[0].replace('\t','')
        
        dict_data = []
        for index , line in ck2generator:
            
            if OneLineKeyValueInfo.corresponds(raw_info = line):
                
                new_value = OneLineKeyValueInfo.create(raw_info = line , index= index)
                dict_data.append(new_value)
            
            if MultiKeyValueInfo.corresponds(raw_info= line):
                
                new_value = MultiKeyValueInfo.create(raw_info= line, index= index)
                dict_data.append(new_value)
            
            if OneLineListInfo.corresponds(raw_info = line):
                
                new_value = OneLineListInfo.create(raw_info = line, index= index)
                dict_data.append(new_value)
            
            if OneLineKeyListInfo.corresponds(raw_info = line):
                
                new_value = OneLineKeyListInfo.create(raw_info = line, index= index)
                dict_data.append(new_value)
            
            if DictInfo.corresponds(raw_info = line):
                
                new_value = DictInfo.create(raw_key_data = line ,start_index=index, ck2generator = ck2generator)
                dict_data.append(new_value)
            
            if OptionalKeyDict.corresponds(raw_info=line):
                new_value = OptionalKeyDict.create(first_line = line,start_index = start_index , ck2generator = ck2generator)
                dict_data.append(new_value)
            
            if line.endswith('}\n') and '{' not in line:
                last_line_spaces = line.count('\t')
                return OptionalKeyDict(
                    start_index = start_index,
                    end_index= index,
                    first_line_start = first_line_start,
                    last_line_start = last_line_spaces,
                    value = dict_data,
                    key = key
                )
        raise Exception('something is wrong !')
    
    def to_raw_string(self) -> typing.Generator[str , None , None]:
        
        first_line : str = '\t' * self.first_line_start + f'{self.key}='*(self.key is not None) + '{' + '\n' 
        
        yield first_line
        
        for value in self.value :
            
            raw_string = value.to_raw_string()
            if isinstance(raw_string , str):
                yield raw_string
            else:
                yield from raw_string
        
        end_parenthesis : str = '\t' * self.last_line_start + '}' + '\n'
        
        
        yield end_parenthesis
    @property
    def last_line_position(self) -> LastPositionData:
        return LastPositionData(
            last_line_index = self.last_line_position,
            last_line_start = self.last_line_start,
            last_line_end = 1
        )