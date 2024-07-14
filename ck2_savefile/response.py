import typing
from ck2_savefile.info_representation import InfoRepresentation
from ck2_savefile.search_type import DictSearch, OneLineKeyValueSearch , OptionalKeyDictSearch

DataGeneratorFuncType = typing.Callable[..., typing.Generator[InfoRepresentation, None, None]]
SearchType = DictSearch | OneLineKeyValueSearch | OptionalKeyDictSearch

class ParseResponse:
    def __init__(self, first_line: str, response_generator_func: DataGeneratorFuncType | typing.Generator):
        self.first_line = first_line
        self.response_generator_func = response_generator_func

    @property
    def generator(self) -> typing.Generator[InfoRepresentation, None, None]:
        """Return the generator for producing InfoRepresentation objects."""
        if callable(self.response_generator_func):
            return self.response_generator_func()
        return self.response_generator_func    
    def search_by_term(self, term: SearchType, current_data: typing.Generator[InfoRepresentation, None, None] | None = None
                      ) -> typing.Generator[InfoRepresentation, None, None]:
        """Search within the data based on the provided term."""
        if current_data is None:
            current_data = self.generator
        
        for info in current_data:
            if term.check_if_valid(info = info):
                data_generator,multiple_values_flag  = term.get_values(info = info)
                
                yield from data_generator
                
                if not multiple_values_flag:
                    return
    def _unravel_dict_generator(self, current_data: typing.Generator[InfoRepresentation, None, None]
                               ) -> typing.Generator[InfoRepresentation, None, None]:
        """Unravel nested dictionary-like structures."""
        for data in current_data:
            
            if isinstance(data , DictSearch.item_info_type):
                data : DictSearch.item_info_type
                for value in data.value:
                    yield value
            elif isinstance(data, OptionalKeyDictSearch.item_info_type):
                data : OneLineKeyValueSearch.item_info_type
                for value in data.value:
                    yield value
            else:
                raise Exception(f'Encountered wrong type of data while unraveling! : {type(data)}')
    def unravel_dict_generator(self, current_data: typing.Generator[InfoRepresentation, None, None] | None, unravel_flag: bool
                              ) -> typing.Generator[InfoRepresentation, None, None]:
        """Conditionally unravel nested dictionary-like structures."""
        if current_data is None:
            return None
        if not unravel_flag:
            return current_data
        return self._unravel_dict_generator(current_data=current_data)

    def get_by_search_term(self, *args: OneLineKeyValueSearch) -> typing.Self:
        """Chain multiple searches and refine results iteratively."""
        current_data = None
        unravel_flag = False

        for search in args:
            
            current_data = self.unravel_dict_generator(current_data=current_data, unravel_flag=unravel_flag)
            current_data = self.search_by_term(term=search, current_data=current_data)
            unravel_flag = not search.get_value_flag if (isinstance(search, DictSearch) or
                                                     isinstance(search , OptionalKeyDictSearch)) else False

        return ParseResponse(
            first_line=self.first_line,
            response_generator_func=current_data
        )

    def __iter__(self ) :
        if callable(self.response_generator_func):
            raise Exception('Do not try to parse the whole file please!')
        return self.generator