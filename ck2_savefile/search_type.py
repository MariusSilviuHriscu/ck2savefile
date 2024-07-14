import typing
from ck2_savefile.info_representation import InfoRepresentation ,DictInfo, OneLineKeyValueInfo, OptionalKeyDict

class DictSearch:
    """
    Represents a search configuration for finding instances of DictInfo in CK2 save files.

    Attributes:
        item_info_type (type): The type of item to search for (DictInfo in this case).
        return_type (type): The type of return value from the search (list of DictInfo).

    Args:
        search_key (str): The key to search for within the dictionary structures.
        get_value_flag (bool, optional): Flag indicating whether to retrieve values associated with the key. Defaults to True.
        multiple_values_flag (bool, optional): Flag indicating whether to allow multiple values for the same key. Defaults to False.
    """

    item_info_type = DictInfo
    return_type = list
    
    def __init__(self, 
                 search_key: str|None = None,
                 search_func : None | typing.Callable[[InfoRepresentation],bool] = None,
                 get_value_flag: bool = True,
                 multiple_values_flag: bool = False
                 ):
        """
        Initializes a new instance of DictSearch.

        Args:
            search_key (str): The key to search for within the dictionary structures.
            get_value_flag (bool, optional): Flag indicating whether to retrieve values associated with the key. Defaults to True.
            multiple_values_flag (bool, optional): Flag indicating whether to allow multiple values for the same key. Defaults to False.
        """
        self.search_key = search_key
        self.search_func = search_func
        self.get_value_flag = get_value_flag
        self.multiple_values_flag = multiple_values_flag
    
    def check_if_valid(self , info : InfoRepresentation) -> bool:
        
        if self.search_key is None and self.search_key is None:
            raise ValueError('Expected at least one type of criteria for sort')
        
        if not isinstance(info , self.item_info_type):
            return False
        if self.search_key is None and self.search_func is not None:
            
            return self.search_func(info)
        
        return self.search_key == info.key
    
    def _get_values(self , info : DictInfo) -> typing.Generator[InfoRepresentation , None , None]:
        if self.get_value_flag:
            yield from (x for x in info.value)
        else :
            yield info
    
    def get_values(self , info : DictInfo) -> tuple[typing.Generator[InfoRepresentation, None, None] , bool]:
        
        return (
            self._get_values(info = info),
            self.multiple_values_flag
        )
        

class OptionalKeyDictSearch:
    """
    Represents a search configuration for finding instances of OptionalKeyDict in CK2 save files.

    Attributes:
        item_info_type (type): The type of item to search for (OptionalKeyDict in this case).
        return_type (type): The type of return value from the search (list of OptionalKeyDict).

    Args:
        search_key (str, optional): The optional key to search for within the optional dictionary structures.
        get_value_flag (bool, optional): Flag indicating whether to retrieve values associated with the key. Defaults to True.
        multiple_values_flag (bool, optional): Flag indicating whether to allow multiple values for the same key. Defaults to False.
    """

    item_info_type = OptionalKeyDict
    return_type = list
    
    def __init__(self, 
                 search_key: typing.Optional[str] = None,
                 search_func: None | typing.Callable[[OptionalKeyDict],bool] = None,
                 get_value_flag: bool = True,
                 multiple_values_flag: bool = False
                 ):
        """
        Initializes a new instance of OptionalKeyDictSearch.

        Args:
            search_key (str, optional): The optional key to search for within the optional dictionary structures.
            get_value_flag (bool, optional): Flag indicating whether to retrieve values associated with the key. Defaults to True.
            multiple_values_flag (bool, optional): Flag indicating whether to allow multiple values for the same key. Defaults to False.
        """
        self.search_key = search_key
        self.search_func = search_func
        self.get_value_flag = get_value_flag
        self.multiple_values_flag = multiple_values_flag
    
    def check_if_valid(self , info : InfoRepresentation) -> bool:
        if not isinstance(info , self.item_info_type):
            return False
        
        if self.search_func is not None:
            return self.search_func(info)
        
        return self.search_key is None or self.search_key == info.key
    
    def _get_values(self , info : OptionalKeyDict) -> typing.Generator[InfoRepresentation , None , None]:
        if self.get_value_flag:
            yield from (x for x in info.value)
        else :
            yield info
    
    def get_values(self , info : OptionalKeyDict) -> tuple[typing.Generator[InfoRepresentation, None, None] , bool]:
        
        return (
            self._get_values(info = info),
            self.multiple_values_flag
        )
            
            
        

class OneLineKeyValueSearch:
    """
    Represents a search configuration for finding instances of OneLineKeyValueInfo in CK2 save files.

    Attributes:
        item_info_type (type): The type of item to search for (OneLineKeyValueInfo in this case).
        return_type (type): The type of return value from the search (OneLineKeyValueInfo).

    Args:
        search_key (str): The key to search for within the key-value pairs.
        multiple_values_flag (bool, optional): Flag indicating whether to allow multiple values for the same key. Defaults to False.
    """

    item_info_type = OneLineKeyValueInfo
    return_type = OneLineKeyValueInfo
    
    def __init__(self,
                 search_key: str| None = None ,
                 search_func : None | typing.Callable[[OneLineKeyValueInfo],bool] = None,
                 multiple_values_flag: bool = False):
        """
        Initializes a new instance of OneLineKeyValueSearch.

        Args:
            search_key (str): The key to search for within the key-value pairs.
            multiple_values_flag (bool, optional): Flag indicating whether to allow multiple values for the same key. Defaults to False.
        """
        self.search_key = search_key
        self.search_func = search_func
        self.multiple_values_flag = multiple_values_flag
    
    def check_if_valid(self , info : InfoRepresentation) -> bool:
        
        if self.search_key is None and self.search_key is None:
            raise ValueError('Expected at least one type of criteria for sort')
        
        if not isinstance(info, self.item_info_type):
            return False
        if self.search_key is None and self.search_func is not None:
            
            return self.search_func(info)
        
        return self.search_key == info.data_key
        
    def _get_values(self , info : DictInfo) -> typing.Generator[InfoRepresentation , None , None]:
        yield info
    
    def get_values(self , info : DictInfo) -> tuple[typing.Generator[InfoRepresentation, None, None] , bool]:
        
        return (
            self._get_values(info = info),
            self.multiple_values_flag
        )