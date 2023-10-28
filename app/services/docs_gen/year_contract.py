from dataclasses import dataclass
from datetime import date
import os
from dateutil.relativedelta import relativedelta
from pathlib import Path
import re
from typing import Literal

from docx.document import Document
import docx

from app.services.docs_gen.utils import (
    docx_replace_regex,
    generate_pdf,
    remove_table_row_text,
)


TEMPLATE_NAME = "YearContractTemplate.docx"
TEMPLATE_FOLDER = "templates"
YEAR_CONTRACT_TEMPLATE_PATH = (
    Path(__file__).parent.resolve() / TEMPLATE_FOLDER / TEMPLATE_NAME
)


@dataclass
class YearContractData:
    contract_number_cpm: str
    _date: date
    client_name: str
    address: str
    service_count: Literal[2, 3]
    _service1_date: date
    discount: float
    service1_price: float

    @property
    def total_text(self):
        if self.service_count == 2:
            return "Service 2"
        return "Services 2-3"

    @property
    def date(self):
        return self._date.strftime("%d.%m.%Y")

    @property
    def service1_date(self):
        return self._service1_date.strftime("%d.%m.%Y")

    @property
    def service2_date(self):
        if self.service_count == 2:
            date = self._service1_date + relativedelta(months=6)
        date = self._service1_date + relativedelta(months=4)
        return date.strftime("%d.%m.%Y")

    @property
    def service3_date(self):
        date = self._service1_date + relativedelta(months=8)
        return date.strftime("%d.%m.%Y")

    @property
    def service2_price(self):
        return round(self.service1_price * (1 - self.discount / 100), 2)

    @property
    def service3_price(self):
        return round(self.service1_price * (1 - self.discount / 100), 2)

    @property
    def price_last_services(self):
        if self.service_count == 2:
            return self.service2_price
        return round(self.service2_price + self.service3_price, 2)

    @property
    def total(self):
        return round(self.price_last_services + self.price_last_services * 0.05, 2)


class YearContractPDF:
    FIELDS_2_SERVICES = [
        "contract_number_cpm",
        "date",
        "client_name",
        "address",
        "service1_date",
        "service2_date",
        "service1_price",
        "service2_price",
        "discount",
        "total_text",
        "total",
    ]
    FIELDS_3_SERVICES = [
        "contract_number_cpm",
        "date",
        "client_name",
        "address",
        "service1_date",
        "service2_date",
        "service3_date",
        "service1_price",
        "service2_price",
        "service3_price",
        "discount",
        "total_text",
        "total",
    ]

    SERVICE_3_TABLE_INDEX = 2
    SERVICE_3_ROW_INDEX = 6

    def __init__(self, data: YearContractData):
        self.doc: Document = docx.Document(str(YEAR_CONTRACT_TEMPLATE_PATH))
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
        if self.data.service_count == 3:
            self.insert(self.FIELDS_3_SERVICES)
            return

        remove_table_row_text(
            self.doc, self.SERVICE_3_TABLE_INDEX, self.SERVICE_3_ROW_INDEX
        )

        self.insert(self.FIELDS_2_SERVICES)

    def insert(self, fields: list[str]):
        for field in fields:
            text = rf"\[{field}\]"
            docx_replace_regex(
                self.doc, re.compile(text), str(getattr(self.data, field))
            )
