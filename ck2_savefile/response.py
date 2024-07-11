import typing
from ck2_savefile.info_representation import InfoRepresentation
from ck2_savefile.search_type import (DictSearch,
                                      OneLineKeyValueSearch
                                      )

DataGeneratorFuncType = typing.Callable[...,typing.Generator[InfoRepresentation, None , None]]
SearchType = DictSearch | OneLineKeyValueSearch

class ParseResponse:
    
    def __init__(self,  
                 first_line : str ,
                 response_generator_func : DataGeneratorFuncType | typing.Generator
                 ):
        self.first_line = first_line
        self.response_generator_func = response_generator_func
    @property
    def generator(self) -> typing.Generator[InfoRepresentation, None , None]:
        if callable(self.response_generator_func):
            return self.response_generator_func()
        return self.response_generator_func
    
    def search_by_term(self , 
                       term : SearchType ,
                       current_data : typing.Generator[InfoRepresentation, None , None] = None
                       ) -> typing.Generator[InfoRepresentation, None , None]:
        
        if current_data is None:
            current_data = self.generator
        for info in current_data:
            
            if (isinstance(info , term.item_info_type) and 
                term.item_info_type == OneLineKeyValueSearch.item_info_type and
                info.data_key == term.search_key
                ):
                
                if term.multiple_values_flag :
                    yield info
                else:
                    yield info
                    return
            if (isinstance(info , term.item_info_type) and
                term.item_info_type == DictSearch.item_info_type and
                info.key == term.search_key
                ):
                if term.multiple_values_flag :
                    yield from (x for x in info.value)
                else:
                    yield from (x for x in info.value)
                    return 
            
    def get_by_search_term(self , *args : OneLineKeyValueSearch) -> typing.Self:
        current_data = None
        for search in args:
            
            current_data = self.search_by_term(term=search,current_data = current_data )
        
        return ParseResponse(
            first_line = self.first_line,
            response_generator_func = current_data
        )
        
    