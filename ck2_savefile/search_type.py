
import typing

from ck2_savefile.info_representation import DictInfo,OneLineKeyValueInfo,OptionalKeyDict



class DictSearch:
    item_info_type = DictInfo
    return_type = list
    
    def __init__(self , search_key : str , get_value_flag : bool = True ,multiple_values_flag : bool = False):
        
        self.search_key = search_key
        self.multiple_values_flag = multiple_values_flag
        self.get_value_flag = get_value_flag

class OptionalKeyDictSearch:
    item_info_type = OptionalKeyDict
    return_type = list
    
    def __init__(self , 
                 search_key : str | None ,
                 get_value_flag : bool = True ,
                 multiple_values_flag : bool = False
                 ):
        
        self.search_key = search_key
        self.get_value_flag = get_value_flag
        self.multiple_values_flag = multiple_values_flag
    

class OneLineKeyValueSearch:
    
    item_info_type = OneLineKeyValueInfo
    return_type = OneLineKeyValueInfo
    
    def __init__(self , search_key : str , multiple_values_flag : bool = False):
        
        self.search_key = search_key
        self.multiple_values_flag = multiple_values_flag

