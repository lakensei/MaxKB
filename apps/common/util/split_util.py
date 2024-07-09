import re
import uuid
from collections import defaultdict
from typing import List

import cv2
import jieba
import requests

from .bbox_util import remove_duplicates_and_contained_bbox, sort_bbox
from .img_util import PdfImgConversion, image_to_base64


class SentenceSplitter:
    def __init__(self, chunk_size: int = 250, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text: str) -> List[str]:
        if self._is_has_chinese(text):
            return self._split_chinese_text(text)
        else:
            return self._split_english_text(text)

    def _split_chinese_text(self, text: str) -> List[str]:
        sentence_endings = {'\n', '。', '！', '？', '；', '…'}  # 句末标点符号
        chunks, current_chunk = [], ''
        for word in jieba.cut(text):
            if len(current_chunk) + len(word) > self.chunk_size:
                chunks.append(current_chunk.strip())
                current_chunk = word
            else:
                current_chunk += word
            if word[-1] in sentence_endings and len(current_chunk) > self.chunk_size - self.chunk_overlap:
                chunks.append(current_chunk.strip())
                current_chunk = ''
        if current_chunk:
            chunks.append(current_chunk.strip())
        if self.chunk_overlap > 0 and len(chunks) > 1:
            chunks = self._handle_overlap(chunks)
        return chunks

    def _split_english_text(self, text: str) -> List[str]:
        # 使用正则表达式按句子分割英文文本
        sentences = re.split(r'(?<=[.!?])\s+', text.replace('\n', ' '))
        chunks, current_chunk = [], ''
        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= self.chunk_size or not current_chunk:
                current_chunk += (' ' if current_chunk else '') + sentence
            else:
                chunks.append(current_chunk)
                current_chunk = sentence
        if current_chunk:  # Add the last chunk
            chunks.append(current_chunk)

        if self.chunk_overlap > 0 and len(chunks) > 1:
            chunks = self._handle_overlap(chunks)

        return chunks

    def _is_has_chinese(self, text: str) -> bool:
        # check if contains chinese characters
        if any("\u4e00" <= ch <= "\u9fff" for ch in text):
            return True
        else:
            return False

    def _handle_overlap(self, chunks: List[str]) -> List[str]:
        # 处理块间重叠
        overlapped_chunks = []
        for i in range(len(chunks) - 1):
            chunk = chunks[i] + ' ' + chunks[i + 1][:self.chunk_overlap]
            overlapped_chunks.append(chunk.strip())
        overlapped_chunks.append(chunks[-1])
        return overlapped_chunks


def langchain_text_chunks(
        text,
        chunk_size: int = 768,
        chunk_overlap: int = 200
):
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len
    )
    return text_splitter.split_text(text)  # split_document()


# def text_to_chunks(texts, word_length=150, start_page=1):
#     text_toks = [t.split('\n') for t in texts]
#     chunks = []
#
#     for idx, words in enumerate(text_toks):
#         for i in range(0, len(words), word_length):
#             chunk = words[i: i + word_length]
#             if (
#                     (i + word_length) > len(words)
#                     and (len(chunk) < word_length)
#                     and (len(text_toks) != (idx + 1))
#             ):
#                 text_toks[idx + 1] = chunk + text_toks[idx + 1]
#                 continue
#             chunk = ' '.join(chunk).strip()
#             chunk = f'[Page no. {idx + start_page}]' + ' ' + '"' + chunk + '"'
#             chunks.append(chunk)
#     return chunks


def text_to_chunk(text,
                  chunk_size: int = 768,
                  chunk_overlap: int = 0):
    contents = SentenceSplitter(chunk_size, chunk_overlap).split_text(text)
    return [{"content": content, "title": ""} for content in contents]


class MllmModelMixin:
    def gen_picture_summary(self, base64_img):
        return '请将图片转换为文本内容，如果图片是表格转为markdown格式的表格，否则详细描述内容'
        # self.vlm_model: OpenAIChatModel
        use_stream = False
        model = "cogvlm2"
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        # "text": "请描述该图片",
                        # "text": "请将图片转换为文本内容，如果图片是表格转为markdown格式的表格，否则详细描述内容",
                        "text": """请仔细查看并分析以下图片中的内容。图片可能包含常规表格、复杂表格、流程图、组织结构图等。请按照以下步骤提取并描述图片中的所有信息，确保提取的信息具有可读性和逻辑性：
- 表格：将其转换为Markdown格式。对于复杂表格，请使用空白单元格表示合并单元格或将一个表格拆分为多个表格来。
- 流程图：描述每个步骤及其连接关系，确保所有节点和流程线都被准确描述。
- 组织结构图：描述每个组织单元的名称及其上下级关系。
- 目录：描述每个目录项及其对应的页码或编号。
- 特殊字符和注释：确保提取所有特殊字符、符号或注释。""",
                        # "text": "根据图片生成文本概述",
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": base64_img
                        },
                    },
                ],
            }
        ]
        data = {
            "model": model,
            "messages": messages,
            "stream": use_stream,
            "max_tokens": 2048,
            "temperature": 0.8,
            "top_p": 0.8,
        }
        base_url = self.mllm_model.openai_api_base
        response = requests.post(f"{base_url}/chat/completions", json=data, stream=use_stream)
        decoded_line = response.json()
        content = decoded_line.get("choices", [{}])[0].get("message", "").get("content", "")
        return content

    # @staticmethod
    # def save_img(img, img_title):
    #     img_url = f'./dataset_img/{img_title}'
    #     img_path = f'../data/dataset_img/{img_title}'
    #     is_success, img_encoded = cv2.imencode('.jpeg', img)
    #     if is_success:
    #         with open(img_path, mode='wb') as f:
    #             f.write(img_encoded)
    #         return img_url

    def image_to_mode(self, img, image_name):
        image_uuid = uuid.uuid1()
        is_success, img_encoded = cv2.imencode('.jpeg', img)
        self.image_list.append({
            "id": image_uuid,
            "image": img_encoded,
            "image_name": image_name,
        })
        return f'![](/api/image/{image_uuid})'


class OcrLayoutContent(MllmModelMixin):
    """
    版面分析获取文本内容
    """

    def __init__(self, pdf_document, file_name, layout_engine, mllm_model):
        self.pdf_document = pdf_document
        self.file_name = file_name.split('.')[0]  # + f'_{int(time.time() * 1000)}'
        self.layout_engine = layout_engine
        self.mllm_model = mllm_model
        self.skip_pages = 0
        self.image_list = []
        self.limit_size = 750

    def parse_layout(self):
        pdf_document = self.pdf_document
        layout_engine = self.layout_engine
        img_conversion = PdfImgConversion()
        for page_num in range(len(pdf_document)):
            if page_num < self.skip_pages:
                continue
            # 读取pdf页面
            page = pdf_document.load_page(page_num)
            # 整页转图片
            img = img_conversion.page_to_img(page)
            # 版面分析
            layout_res, elapse = layout_engine(img)
            print(page_num, elapse)
            # vis_layout(img, layout_res, f'./{page_num}.png')
            # 版面分析结果清理
            layout_res = remove_duplicates_and_contained_bbox(layout_res)
            # 读取文本内容
            text_items = []
            for block in page.get_text("dict")["blocks"]:
                if block['type'] != 0:  # 类型0通常包含文本信息
                    continue
                for line in block['lines']:
                    for span in line['spans']:
                        text = span['text']
                        bbox = tuple(map(round, span['bbox']))
                        size = round(span['size'])
                        text_items.append(
                            {"content": text, "bbox": bbox, "scale_bbox": img_conversion.scale_up_bbox(*bbox),
                             "size": size})
            text_dict = {item["scale_bbox"]: item for item in text_items}
            # 对文本进行分行排序 （直接去lines存在错行）
            bias = 15  # page_to_img时进行了放大3倍
            sorted_text_line = sort_bbox(list(text_dict.keys()), bias)
            # todo: 按行对文本与版面进行比对
            paragraph_list = defaultdict(list)
            for line in sorted_text_line:
                min_x1 = line[0][0]
                max_x2 = line[-1][2]
                max_y1 = max((box[1] for box in line))
                content_list = [text_dict[box] for box in line]
                avg_size = round(sum((box["size"] for box in content_list)) / len(line))
                line_box = {"y1": max_y1, "size": avg_size,
                            "content": "".join([box["content"] for box in content_list])}
                for layout in layout_res:
                    # fixme: 当图片与内容处于同一行时
                    # if layout['bbox'][1] <= max_y1 <= layout['bbox'][3] and min_x1 + bias >= layout['bbox'][0] and max_x2 <= layout['bbox'][2] + bias:
                    if layout['bbox'][1] - bias <= max_y1 <= layout['bbox'][3] + bias:
                        line_box["label"] = layout["label"]
                        line_box["bbox"] = layout["bbox"]
                        break
                if line_box.get("label"):
                    y1 = line_box["bbox"][1]
                else:
                    y1 = max_y1
                paragraph_list[y1].append(line_box)
            sections = []
            i = 0
            for paragraph in paragraph_list.values():
                sum_size = 0
                contents = []
                for line in paragraph:
                    sum_size += line["size"]
                    if line.get("label") in ("figure", "table"):
                        # print(page_num)
                        x_start, y_start, x_end, y_end = map(round, line["bbox"])
                        cropped_img = img[y_start:y_end, x_start:x_end]
                        img_title = f'{self.file_name}_{page_num}_{i}.jpeg'
                        img_url = self.image_to_mode(cropped_img, img_title)
                        # 调用大模型获取图片描述
                        img_dsc = self.gen_picture_summary(image_to_base64(cropped_img))
                        content = f'{img_dsc}\n {img_url}'
                        contents.append(content)
                        i += 1
                        break
                    else:
                        content = line["content"]
                        contents.append(content)
                sections.append({
                    "content": "\n".join(contents),
                    "label": paragraph[0].get("label", "text"),
                    "size": round(sum_size / len(paragraph)),
                    "page": page_num
                })

            yield sections

    @staticmethod
    def get_title_size(sections):
        # 标题
        size_list = sorted(set([l["size"] for sec in sections for l in sec if l.get("label") == 'title']), reverse=True)
        level = 4
        seg = int(len(size_list) / level)
        return [size_list[seg * i:seg * (i + 1)][-1] for i in range(level)]
        # return [size_list[0:seg][-1], size_list[seg:seg * 2][-1], size_list[seg * 2:seg * 3][-1]]

    def get_content(self):
        sections = [sec for sec in self.parse_layout()]
        content_list = []
        lvl_list = self.get_title_size(sections)
        for lines in sections:
            for line in lines:
                if line.get("label") == 'footer':
                    continue
                if line.get("label") == 'title':
                    for i, lvl in enumerate(lvl_list):
                        if line["size"] >= lvl:
                            line["content"] = "#" * (i + 1) + " " + line["content"]
                            # line["content"] = "\n" + line["content"]
                            break
                    # line["content"] = "# " + line["content"]
                content_list.append(line["content"])
        return '\n'.join(content_list)

    def get_section(self):
        sections = [sec for sec in self.parse_layout()]
        lvl_list = self.get_title_size(sections)
        # print(lvl_list)
        title = ''
        # lst_lvl = 9
        section_list = []
        for lines in sections:
            for line in lines:
                if line.get("label") == 'footer':
                    continue
                if line.get("label") == 'title':
                    # title_lvl = 0
                    # for i, lvl in enumerate(lvl_list):
                    #     if line["size"] >= lvl:
                    #         title_lvl += i
                    # if lst_lvl < title_lvl and title != '':
                    #     title = title + "" + line.get("content")
                    # else:
                    #     title = line.get("content")
                    #     lst_lvl = title_lvl
                    # # title = title + "" + line.get("content")
                    # print(title, line["size"], title_lvl, lst_lvl)
                    title = line.get("content")
                else:
                    section_list.append({
                        "content": line["content"],
                        "chunk_size": len(line["content"]),
                        "title": title
                    })
                    # title = ''
        title_dict = defaultdict(list)
        for section in section_list:
            title_dict[section["title"]].append(section)
        res = []
        limit_size = self.limit_size
        for title, sections in title_dict.items():
            chunk_size = 0
            content = ""
            for section in sections:
                chunk_size += section["chunk_size"]
                content += "\n" + section["content"]
                if chunk_size >= limit_size:
                    res.append({
                        "content": title + '\n' + content,
                        "chunk_size": chunk_size,
                        "title": title,
                    })
                    chunk_size = 0
                    content = ""
            if chunk_size:
                res.append({
                    "content": title + '\n' + content,
                    "chunk_size": chunk_size,
                    "title": title,
                })
        return res


class MllmContent(MllmModelMixin):
    def __init__(self, pdf_document, file_name, mllm_model):
        self.pdf_document = pdf_document
        self.file_name = file_name.split('.')[0]  # + f'_{int(time.time() * 1000)}'
        self.mllm_model = mllm_model
        self.skip_pages = 0
        self.image_list = []

    def parse_page(self):
        pdf_document = self.pdf_document
        img_conversion = PdfImgConversion()
        for page_num in range(len(pdf_document)):
            if page_num < self.skip_pages:
                continue
            # 读取pdf页面
            page = pdf_document.load_page(page_num)
            # 整页转图片
            img = img_conversion.page_to_img(page)
            img_title = f'{self.file_name}_{page_num}.jpeg'
            # 调用大模型获取图片描述
            img_url = self.image_to_mode(img, img_title)
            img_dsc = self.gen_picture_summary(image_to_base64(img))
            content = f'{img_dsc}\n {img_url}'
            section = {
                "title": "",
                "content": content,
                "page": page_num
            }
            yield section

    def get_section(self):
        return [section for section in self.parse_page()]

    def get_content(self):
        return '\n'.join([section["content"] for section in self.parse_page()])
