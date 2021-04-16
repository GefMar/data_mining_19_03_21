import typing
import re
from pathlib import Path
import PyPDF2
from PyPDF2.utils import PdfReadError
import pytesseract
from PIL import Image


"""
Форматы файлов различны: JPG PDF
Шаблоны данных Различны: N Вариантов
Искомое поле: 2 Варианта
"""


# PDF to Image
def pdf_image_extract(pdf_path: Path, images_path: Path) -> typing.List[Path]:
    results = []
    with pdf_path.open("rb") as file:
        try:
            pdf_file = PyPDF2.PdfFileReader(file)
        except PdfReadError:
            return results

        for page_num, page in enumerate(pdf_file.pages, 1):
            image_file_name = f"{pdf_path.name}_{page_num}"
            image_data = page["/Resources"]["/XObject"]["/Im0"]._data
            image_path = images_path.joinpath(image_file_name)
            image_path.write_bytes(image_data)
            results.append(image_path)
    return results


# Image to Text
def get_serial_numbers(image_path: Path) -> typing.List[str]:
    results = []
    image = Image.open(image_path)
    text_rus = pytesseract.image_to_string(image, "rus")
    pattern = re.compile(r"(заводской.*[номер|№])")
    matches = len(re.findall(pattern, text_rus))
    if matches:
        text_eng = pytesseract.image_to_string(image, "eng").split("\n")
        for idx, line in enumerate(text_rus.split("\n")):
            if re.match(pattern, line):
                results.append(text_eng[idx].split()[-1])
    return results


if __name__ == "__main__":
    images_path = Path(__file__).parent.joinpath("images")
    if not images_path.exists():
        images_path.mkdir()

    pdf_file = Path(__file__).parent.joinpath("8416_4.pdf")
    images = pdf_image_extract(pdf_file, images_path)
    numbers = sum(map(get_serial_numbers, images), [])
    print(1)
