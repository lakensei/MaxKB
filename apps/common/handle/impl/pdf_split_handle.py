# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： text_split_handle.py
    @date：2024/3/27 18:19
    @desc:
"""
import re
from typing import List

import fitz

from common.handle.base_split_handle import BaseSplitHandle
from common.util.split_model import SplitModel
from dataset.models import Image

default_pattern_list = [re.compile('(?<=^)# .*|(?<=\\n)# .*'),
                        re.compile('(?<=\\n)(?<!#)## (?!#).*|(?<=^)(?<!#)## (?!#).*'),
                        re.compile("(?<=\\n)(?<!#)### (?!#).*|(?<=^)(?<!#)### (?!#).*"),
                        re.compile("(?<=\\n)(?<!#)#### (?!#).*|(?<=^)(?<!#)#### (?!#).*"),
                        re.compile("(?<=\\n)(?<!#)##### (?!#).*|(?<=^)(?<!#)##### (?!#).*"),
                        re.compile("(?<=\\n)(?<!#)###### (?!#).*|(?<=^)(?<!#)###### (?!#).*"),
                        re.compile("(?<!\n)\n\n+")]


def number_to_text(pdf_document, page_number):
    page = pdf_document.load_page(page_number)
    text = page.get_text()
    return text


class PdfSplitHandle(BaseSplitHandle):
    def _handle(self, file, pattern_list: List, with_filter: bool, limit: int, get_buffer, save_image):
        try:
            buffer = get_buffer(file)
            pdf_document = fitz.open(file.name, buffer)
            content = "\n".join([number_to_text(pdf_document, page_number) for page_number in range(len(pdf_document))])
            if pattern_list is not None and len(pattern_list) > 0:
                split_model = SplitModel(pattern_list, with_filter, limit)
            else:
                split_model = SplitModel(default_pattern_list, with_filter=with_filter, limit=limit)
        except BaseException as e:
            return {'name': file.name,
                    'content': []}
        return {'name': file.name,
                'content': split_model.parse(content)
                }

    def handle(self, file, pattern_list: List, with_filter: bool, limit: int, get_buffer, save_image,
               mllm_model=None, rule_type="1"):
        buffer = get_buffer(file)
        pdf_document = fitz.open(file.name, buffer)
        image_list = []
        if rule_type == "1":
            content = "\n".join(
                [number_to_text(pdf_document, page_number) for page_number in range(len(pdf_document))])
            split_content = SplitModel(default_pattern_list, with_filter=with_filter, limit=limit).parse(
                content)
        elif rule_type == "2":
            content = "\n".join(
                [number_to_text(pdf_document, page_number) for page_number in range(len(pdf_document))])
            split_content = SplitModel(pattern_list, with_filter=with_filter, limit=limit).parse(
                content)
        elif rule_type == "3":
            from common.util.split_util import OcrLayoutContent
            from common.config.layout_config import LayoutModel
            layout_obj = OcrLayoutContent(pdf_document, file.name, LayoutModel(), mllm_model)
            split_content = layout_obj.get_section()
            image_list = layout_obj.image_list
            # if pattern_list is not None and len(pattern_list) > 0:
            #     split_content = SplitModel(pattern_list, with_filter=with_filter, limit=limit).parse(content)
            # else:
            #     split_content = text_to_chunk(content, limit)
        elif rule_type == "4":
            from common.util.split_util import MllmContent
            mllm_obj = MllmContent(pdf_document, file.name, mllm_model)
            split_content = mllm_obj.get_section()
            image_list = mllm_obj.image_list
        else:
            return {'name': file.name,
                    'content': []}
        if len(image_list) > 0:
            save_image([Image(**item) for item in image_list])
        return {'name': file.name,
                'content': split_content,
                # 'attachments': attachments
                }

    def support(self, file, get_buffer):
        file_name: str = file.name.lower()
        if file_name.endswith(".pdf"):
            return True
        return False
