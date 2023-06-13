'''Interface definition and common implemetations for file processing classes'''
from io import TextIOWrapper
from typing import List
import csv

import schema

#pylint: disable=too-few-public-methods, unused-argument

class FileProcessingInterface:
    '''Interface for file handling techniques'''
    def process_file(self,
                 file: TextIOWrapper, # TextIOWrapper is just the type() of file object in python
                 labels:List[str]=None,
                 file_type:str=schema.FileType.TEXT,
                 **kwargs) -> List[schema.Document]:
        '''Converts the file contents to Document type, as per the format and its implementation.
        file_type can be more content specific like "paratext manual" or "usfm bible"
        with custom handling for its format and contents.
        Implementations should try to fill as much additional information like links, media etc.
        labels, when provided, should apply to all documents in the o/p list'''

        return []

    def process_file_csv(self,
            file: TextIOWrapper,
            col_delimiter:str=",") -> List[schema.Document]:
        '''Converts CSV files with format, (id, text, labels, links, medialinks)
        labels, links and media links must be comma separated values in the same field.
        into document objects'''
        output_list = []
        reader = csv.DictReader(file, delimiter=col_delimiter)

        for row in reader:
            doc = schema.Document()
            doc.docId = row['id'].strip()
            doc.text = row['text']
            doc.labels = [ lbl.strip() for lbl in row['labels'].split(',')]
            doc.links = [ lnk.strip() for lnk in row['links'].split(',')]
            doc.media = [ med.strip() for med in row['medialinks'].split(',')]
            output_list.append(doc)
        return output_list
