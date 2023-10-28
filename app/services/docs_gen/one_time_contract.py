from dataclasses import dataclass
from datetime import date
import os
from pathlib import Path
import re

from docx.document import Document
import docx

from app.services.docs_gen.utils import docx_replace_regex, generate_pdf


TEMPLATE_NAME = "OneTimeContractTemplate.docx"
TEMPLATE_FOLDER = "templates"
ONE_TIME_CONTRACT_TEMPLATE_PATH = (
    Path(__file__).parent.resolve() / TEMPLATE_FOLDER / TEMPLATE_NAME
)


@dataclass
class OneTimeContractData:
    contract_number_cpm: str
    _date: date
    client_name: str
    address: str
    ac_maintenance_price: float
    ac_repair_price: float
    other_price: float
    discount_price: float

    @property
    def date(self):
        return self._date.strftime("%d.%m.%Y")

    @property
    def price(self):
        return round(
            (
                self.ac_maintenance_price
                + self.ac_repair_price
                + self.other_price
                - self.discount_price
            ),
            2,
        )

    @property
    def vat(self):
        return round(self.price * 0.05, 2)

    @property
    def total(self):
        return round(self.price + self.vat, 2)


class OneTimeContractPDF:
    FIELDS = [
        "contract_number_cpm",
        "date",
        "client_name",
        "address",
        "ac_maintenance_price",
        "ac_repair_price",
        "other_price",
        "discount_price",
        "vat",
        "total",
    ]

    def __init__(self, data: OneTimeContractData):
        self.doc: Document = docx.Document(str(ONE_TIME_CONTRACT_TEMPLATE_PATH))
        self.data = data
        self.insert_data()

    def generate_docx(self, path: Path):
        self.doc.save(path)

    def generate_pdf(self, path: Path, filename: str) -> Path:
        path_to_docx = path / f"{filename}.docx"
        path_to_pdf = path / f"{filename}.pdf"
        self.generate_docx(path_to_docx)
        generate_pdf(path_to_docx, path)
        os.remove(path_to_docx)
        return path_to_pdf

    def insert_data(self) -> None:
        for field in self.FIELDS:
            text = rf"\[{field}\]"
            docx_replace_regex(
                self.doc, re.compile(text), str(getattr(self.data, field))
            )
