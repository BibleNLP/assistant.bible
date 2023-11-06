"""Langchain based implementation for file handling"""
from typing import List
from langchain.text_splitter import TokenTextSplitter
from langchain.document_loaders import TextLoader, UnstructuredPDFLoader

from core.file_processor import FileProcessorInterface
import schema
from custom_exceptions import GenericException


# pylint: disable=too-few-public-methods, unused-argument, too-many-arguments, R0801


class LangchainLoader(FileProcessorInterface):
    """Langchain based implementation for file handling"""

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
        name = kwargs.get("name", file_path)
        if file_type in [schema.FileType.TEXT, schema.FileType.MD]:
            metadata = kwargs.get("metadata", {})
            texts = self.text_loader(file_path = file_path)
            output_list = self.process_texts(
                texts = texts,
                label=label,
                name=name,
                metadata=metadata
                )
        elif file_type == schema.FileType.PDF:
            metadata = kwargs.get("metadata", {})
            texts = self.pdf_loader(file_path = file_path)
            output_list = self.process_texts(
                texts = texts,
                label=label,
                name=name,
                metadata=metadata
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


    def text_loader(self, file_path: str) -> List[schema.Document]:
        """Uses langchain's TextLoader to load text contents from file"""
        loader = TextLoader(file_path)
        texts = loader.load()
        return texts


    def pdf_loader(self, file_path: str) -> List[schema.Document]:
        """Uses langchain's UnstructuredPDFLoader to load text contents from file"""
        loader = UnstructuredPDFLoader(file_path)
        texts = loader.load()
        return texts


    def process_texts(
        self,
        texts: List[schema.Document],
        label:str,
        name: str = None,
        metadata: dict = None,
    ) -> List[schema.Document]:
        """Uses langchain's TokenTextSplitter to convert text contents into document format"""
        output_list = []
        text_splitter = TokenTextSplitter(chunk_size=1000, chunk_overlap=50)
        text_splits = text_splitter.split_documents(texts)

        if not label:
            label = "open-access"
        if metadata is None:
            metadata = {}
        for i, split in enumerate(text_splits):
            meta = {}
            meta.update(split.metadata)
            meta.update(metadata)
            doc = schema.Document(
                docId=f"{name}-{i}", text=split.page_content, label=label, metadata=meta
            )
            output_list.append(doc)
        return output_list
