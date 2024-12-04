# utils/text_extraction.py

import olefile
import zlib
import struct
import re
from docx import Document
from PyPDF2 import PdfReader
import gethwp
import re
from .text_cleaning import clean_extracted_text
import logging

# 모듈별 로거 생성
logger = logging.getLogger(__name__) 

def get_hwp_text(filename):
    """
    HWP 파일에서 텍스트를 추출합니다.

    Args:
        filename (str): HWP 파일 경로.

    Returns:
        str: 추출된 텍스트 또는 빈 문자열 (추출 실패 시).
    """
    f = olefile.OleFileIO(filename)
    dirs = f.listdir()

    if ["FileHeader"] not in dirs or ["\x05HwpSummaryInformation"] not in dirs:
        raise Exception("Not Valid HWP.")

    header = f.openstream("FileHeader")
    header_data = header.read()
    is_compressed = (header_data[36] & 1) == 1

    nums = []
    for d in dirs:
        if d[0] == "BodyText":
            nums.append(int(d[1][len("Section"):]))
    sections = ["BodyText/Section" + str(x) for x in sorted(nums)]

    text = ""
    for section in sections:
        bodytext = f.openstream(section)
        data = bodytext.read()
        try:
            unpacked_data = zlib.decompress(data, -15) if is_compressed else data
        except zlib.error as e:
            print(f"Decompression error: {e}")
            continue

        section_text = ""
        i = 0
        size = len(unpacked_data)
        while i < size:
            header = struct.unpack_from("<I", unpacked_data, i)[0]
            rec_type = header & 0x3ff
            rec_len = (header >> 20) & 0xfff

            if rec_type == 67:
                rec_data = unpacked_data[i + 4:i + 4 + rec_len]
                try:
                    decoded_text = rec_data.decode('utf-16-le', errors='ignore')

                    # 한글, 숫자, 영어, 공백만 유지
                    cleaned_text = re.sub(r'[^\uAC00-\uD7A3a-zA-Z0-9\s]', '', decoded_text)
                    section_text += cleaned_text + "\n"
                except UnicodeDecodeError as e:
                    print(f"Decoding error at position {i}: {e}")

            i += 4 + rec_len

        text += section_text
        text += "\n"

    return text

def get_hwpx_text(filename):
    """
    HWPX 파일에서 텍스트를 추출하는 내부 함수.

    Args:
        file_path (str): HWPX 파일 경로.

    Returns:
        str: 추출된 텍스트.
    """
    try:
        hwpx = gethwp.read_hwpx(filename)
        cleaned_text = clean_extracted_text(hwpx)
        return cleaned_text
    except Exception as e:
        print(f"HWPX 파일 읽기 오류: {e}")
        return None

def get_docx_text(filename):
    """
    DOCX 파일에서 텍스트를 추출합니다.

    Args:
        filename (str): DOCX 파일 경로.

    Returns:
        str: 추출된 텍스트 또는 빈 문자열 (추출 실패 시).
    """
    try:
        doc = Document(filename)
        text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        print("Error reading DOCX file:", e)
        return None

def get_txt_text(filename):
    """
    TXT 파일에서 텍스트를 추출합니다.

    Args:
        filename (str): TXT 파일 경로.

    Returns:
        str: 추출된 텍스트 또는 빈 문자열 (추출 실패 시).
    """
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            text = file.read()
        return text
    except Exception as e:
        print("Error reading TXT file:", e)
        return None

def get_pdf_text(filename):
    """
    PDF 파일에서 텍스트를 추출합니다.

    Args:
        filename (str): PDF 파일 경로.

    Returns:
        str: 추출된 텍스트 또는 None (추출 실패 시).
    """
    try:
        reader = PdfReader(filename)
        text = ""
        for page_num, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception as e:
        print("Error reading PDF file:", e)
        return None

def extract_text(file_path):
    """
    파일 형식에 따라 적절한 텍스트 추출 함수를 호출합니다.

    Args:
        file_path (str): 분석할 파일의 경로.

    Returns:
        str: 추출된 텍스트 또는 None (지원되지 않는 파일 형식 또는 추출 실패 시).
    """
    extension = file_path.split('.')[-1].lower()
    if extension == 'hwp':
        try:
            return get_hwp_text(file_path)
        except Exception as e:
            print(f"Error processing HWP file: {e}")
            return None
    elif extension == 'docx':
        return get_docx_text(file_path)
    elif extension == 'txt':
        return get_txt_text(file_path)
    elif extension == 'pdf':
        return get_pdf_text(file_path)
    elif extension == 'hwpx':
        return get_hwpx_text(file_path)
    else:
        print("Unsupported file type.")
        return None