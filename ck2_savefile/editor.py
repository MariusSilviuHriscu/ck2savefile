from pathlib import Path
from typing import List, Union, Generator

from ck2_savefile.info_representation import SimpleInfoChange,ComplexChanges

class EditorHandler:
    def __init__(self, changes: List[Union[SimpleInfoChange, ComplexChanges]], file_path: Path):
        self.changes = changes
        self.file_path = file_path
        self.content = self.read_file(file_path)

    def read_file(self, file_path: Path) -> List[str]:
        with file_path.open('r') as file:
            return file.readlines()

    def apply_changes(self):
        sorted_changes = sorted(self.changes, key=lambda c: (c.line_number if isinstance(c, SimpleInfoChange) else c.insertion_index))
        offset = 0

        for change in sorted_changes:
            if isinstance(change, SimpleInfoChange):
                self.apply_simple_change(change, offset)
            elif isinstance(change, ComplexChanges):
                lines_added = self.apply_complex_change(change, offset)
                offset += lines_added

    def apply_simple_change(self, change: SimpleInfoChange, offset: int):
        adjusted_line_number = change.line_number + offset
        self.content[adjusted_line_number] = change.new_line

    def apply_complex_change(self, change: ComplexChanges, offset: int) -> int:
        new_lines = list(change.insertion_generator)
        insertion_index = change.insertion_index + offset
        self.content[insertion_index:insertion_index] = new_lines
        return len(new_lines)

    def write_to_file(self, new_file_path: Path):
        with new_file_path.open('w') as file:
            file.writelines(self.content)