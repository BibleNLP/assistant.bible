"""Interface definition and common implemetations for file processing classes"""
from io import TextIOWrapper
from typing import List
import csv

import schema

# pylint: disable=too-few-public-methods, unused-argument


class FileProcessorInterface:
    """Interface for file handling techniques"""

    def process_file(
        self,
        file: str,
        label: str = None,
        file_type: str = schema.FileType.TEXT,
        **kwargs
    ) -> List[schema.Document]:
        """Converts the file contents to Document type, as per the format and its implementation.
        file_type can be more content specific like "paratext manual" or "usfm bible"
        with custom handling for its format and contents.
        Implementations should try to fill as much additional information like links, media etc.
        label, when provided, should apply to all documents in the o/p list"""

        return []

    def process_file_csv(
        self, file: str, col_delimiter: str = ","
    ) -> List[schema.Document]:
        """Converts CSV files with format, (id, text, label, links, medialinks)
        label, links and media links must be comma separated values in the same field.
        into document objects"""
        output_list = []
        with open(file, "r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile, delimiter=col_delimiter)
            for row in reader:
                if row["links"] is None or row["links"].strip() == "":
                    links = []
                else:
                    links = [lnk.strip() for lnk in row["links"].split(",")]
                if row["medialinks"] is None or row["medialinks"].strip() == "":
                    media = []
                else:
                    media = [med.strip() for med in row["medialinks"].split(",")]
                doc = schema.Document(
                    docId=row["id"].strip(),
                    text=row["text"],
                    label=row["label"],
                    links=links,
                    media=media,
                )
                output_list.append(doc)
            return output_list
