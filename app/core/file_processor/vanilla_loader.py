"""Langchain based implementation for file handling"""
from io import TextIOWrapper
from typing import List

from core.file_processor import FileProcessorInterface
import schema
from custom_exceptions import GenericException


# pylint: disable=too-few-public-methods, unused-argument, too-many-arguments, R0801

class VanillaLoader(FileProcessorInterface):
    """Vanilla implementation for file handling"""

    def process_file(
        self,
        file_path: str,
        label: str = "open-access",
        file_type: str = schema.FileType.TEXT,
        **kwargs,
    ) -> List[schema.Document]:
        """Converts the file contents to Document type, as per the format and its implementation.
        file_type can be more content specific like "paratext manual" or "usfm bible"
        with custom handling for its format and contents.
        Implementations should try to fill as much additional information like links, media etc.
        label, when provided, should apply to all documents in the o/p list"""
        if file_type in [schema.FileType.TEXT, schema.FileType.MD]:
            name = kwargs.get("name", None)
            metadata = kwargs.get("metadata", {})
            output_list = self.process_file_text(
                file=file_path, label=label, name=name, metadata=metadata
            )
        elif file_type == schema.FileType.CSV:
            args = {}
            col_delimiter = kwargs.get("col_delimiter")
            if col_delimiter is not None:
                args["col_delimiter"] = col_delimiter
            output_list = self.process_file_csv(file=file_path, **args)
        else:
            raise GenericException("This file type is not supported (yet)!")
        return output_list

    def process_file_text(
        self, file: TextIOWrapper, label: str, name: str = None, metadata: dict = None
    ) -> List[schema.Document]:
        """Uses plain Python to convert text contents into document format"""
        output_list = []
        texts = file.readlines()

        if not label:
            label = "open-access"
        if name is None or name.strip() == "":
            name = file.name
        if metadata is None:
            metadata = {}

        chunk_size = 1000
        chunk_overlap = 0
        i = 0

        while i < len(texts):
            split_text = texts[i: i + chunk_size]
            meta = metadata.copy()
            doc = schema.Document(
                docId=f"{name}-{i // chunk_size}",
                text="".join(split_text),
                label=label,
                metadata=meta,
            )
            output_list.append(doc)
            i += chunk_size - chunk_overlap

        return output_list
