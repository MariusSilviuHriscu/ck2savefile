from pathlib import Path
import typing
import json

class InfoRepresentation(typing.Protocol):
    
    @staticmethod
    def create(raw_into : str) -> typing.Self:
        pass
    
    def to_raw_string(self) -> str:
        pass
    @staticmethod
    def corresponds(raw_info:str) ->bool:
        pass
    def change_value(self , other : typing.Any) -> None:
        pass

class OneLineKeyValueInfo:
    def __init__(self , 
                 data_key : str ,
                 data_value : str , 
                 start_spaces : int ,
                 end_spaces : int):
        self.data_key = data_key
        self.data_value = data_value
        self.start_spaces= start_spaces
        self.end_spaces = end_spaces
    @staticmethod
    def create(raw_info : str) -> typing.Self:
        start_spaces = raw_info.count('\t')
        end_spaces = raw_info.count('\n')
        data_name , data_value = raw_info.replace('\t' , '').replace('\n', '').split('=')
        return OneLineKeyValueInfo(
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
    
    def change_value(self , value : str) :
        self.data_value = value
class MultiKeyValueInfo():
    def __init__(self,
                 values : list[OneLineKeyValueInfo],
                 start_space : int ,
                 end_spaces : int ) :
        self.values = values
        self.start_space = start_space
        self.end_spaces = end_spaces
    
    @staticmethod
    def create(raw_info : str) -> typing.Self :
        
        start_spaces = raw_info.count('\t')
        end_spaces = raw_info.count('\n')
        
        data_raw = raw_info.replace('\n' , '').replace('\t ', '')
        pairs = data_raw.split(' ')
        data = [OneLineKeyValueInfo.create(raw_info=x) 
                for x in pairs if '=' in x]

        
        return MultiKeyValueInfo(
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

class OneLineListInfo:
    def __init__(self , info_list : list[str],start_spaces : int , end_spaces : int):
        self.info_list = info_list
        self.start_spaces = start_spaces
        self.end_spaces = end_spaces
    
    @staticmethod
    def create(raw_info : str) -> typing.Self:
        
        start_spaces = raw_info.count('\t')
        end_spaces = raw_info.count('\n')
        
        data = raw_info.replace('\t' , '').replace('\n' , '').split(' ')
        
        return OneLineListInfo(info_list = data,
                               start_spaces = start_spaces,
                               end_spaces = end_spaces
                               )
    @staticmethod
    def corresponds(raw_info : str) -> bool:
        
        return '=' not in raw_info and raw_info.count(' ') > 1
    
    def to_raw_string(self) -> str:
        return '\t' * self.start_spaces + ' '.join(self.info_list) + '\n' * self.end_spaces
    
    def change_value(self , other_list : list[str]):
        self.info_list = other_list

class OneLineKeyListInfo:
    
    def __init__(self , data_key : str , data_list : OneLineListInfo,start_spaces : int , end_spaces : int):
        
        self.data_key = data_key
        self.data_list = data_list
        self.start_spaces = start_spaces
        self.end_spaces = end_spaces
    
    def create(raw_info : str) -> typing.Self:
        
        start_spaces = raw_info.count('\t')
        end_spaces = raw_info.count('\n')
        
        data_key , data_list_str = raw_info.replace('\t' , '').replace('\n' , '').split('=')
        data_list = OneLineListInfo.create(
                    raw_info = data_list_str.replace('{','\t').replace('}','\n')
        )
        return OneLineKeyListInfo(
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
class DictInfo:
    
    def __init__(self , 
                 key : str ,
                 value : list[typing.Self | OneLineKeyListInfo | OneLineListInfo | OneLineKeyValueInfo],
                 start_spaces : int,
                 end_spaces : int
                 ):
        
        self.key = key
        self.value = value
        self.start_spaces = start_spaces
        self.end_spaces = end_spaces
    
    @staticmethod
    def corresponds(raw_info : str):
        
        return raw_info[-2::] == '=\n'

    @staticmethod
    def create( raw_key_data :str , ck2generator : typing.Generator[str,None,None] ) -> typing.Self:
        
        start_spaces = raw_key_data.count('\t')
        end_spaces = raw_key_data.count('\n')
        
        key_data = raw_key_data.replace('\n','').replace('\t','').replace('=','')
        
        dict_data = []
        
        open_parenthesis = next(ck2generator)
        if not open_parenthesis.endswith('{\n'):
            raise ValueError(f'Expected a curly bracket but only got {open_parenthesis}')
        
        for line in ck2generator:
            
            if OneLineKeyValueInfo.corresponds(raw_info = line):
                
                new_value = OneLineKeyValueInfo.create(raw_info = line)
                dict_data.append(new_value)
            
            if MultiKeyValueInfo.corresponds(raw_info= line):
                
                new_value = MultiKeyValueInfo.create(raw_info= line)
                dict_data.append(new_value)
            
            if OneLineListInfo.corresponds(raw_info = line):
                
                new_value = OneLineListInfo.create(raw_info = line)
                dict_data.append(new_value)
            
            if OneLineKeyListInfo.corresponds(raw_info = line):
                
                new_value = OneLineKeyListInfo.create(raw_info = line)
                dict_data.append(new_value)
            
            if DictInfo.corresponds(raw_info = line):
                
                new_value = DictInfo.create(raw_key_data = line , ck2generator = ck2generator)
                dict_data.append(new_value)
            
            if line.endswith('}\n') and '{' not in line:
                return DictInfo(
                    key = key_data ,
                    value = dict_data,
                    start_spaces= start_spaces,
                    end_spaces = end_spaces
                )
        raise Exception('something is wrong !')