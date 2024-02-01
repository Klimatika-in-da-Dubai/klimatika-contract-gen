from dataclasses import dataclass
from datetime import date, datetime
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
class ServiceData:
    name: str
    price: float


@dataclass
class OneTimeContractData:
    contract_number_cpm: str
    _date: date
    client_name: str
    address: str
    services: list[ServiceData]
    discount: float

    @property
    def date(self):
        return self._date.strftime("%d.%m.%Y")

    def services_price(self) -> float:
        return sum([service.price for service in self.services])

    @property
    def price(self):
        return self.services_price() - self.discount_price

    @property
    def discount_price(self) -> float:
        return self.services_price() * (self.discount / 100)

    @property
    def vat(self) -> float:
        return self.price * 0.05

    @property
    def total(self) -> float:
        return self.price + self.vat


class OneTimeContractPDF:
    FIELDS = [
        "contract_number_cpm",
        "date",
        "client_name",
        "address",
        "discount_price",
        "vat",
        "total",
    ]

    def __init__(self, data: OneTimeContractData):
        self.doc: Document = docx.Document(str(ONE_TIME_CONTRACT_TEMPLATE_PATH))
        self.data = data
        self.insert_data()
        self.insert_services_data()

    def generate_docx(self, path: Path):
        self.doc.save(path)

    def generate_pdf(self, path: Path, filename: str) -> Path:
        filename = f"MAINTENANCE_{filename}_{datetime.now().date()}"
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

    def insert_services_data(self) -> None:
        for i, service in enumerate(self.data.services, start=1):
            index = re.compile(rf"\[index{i}\]")
            name = re.compile(rf"\[service{i}_name\]")
            price = re.compile(rf"\[service{i}_price\]")
            aed = re.compile(rf"\[AED{i}\]")
            docx_replace_regex(self.doc, re.compile(index), str(i))
            docx_replace_regex(self.doc, re.compile(name), str(service.name))
            docx_replace_regex(self.doc, re.compile(price), str(service.price))
            docx_replace_regex(self.doc, re.compile(aed), "AED")

        for i in range(len(self.data.services), 3):
            j = i + 1
            index = re.compile(rf"\[index{j}\]")
            name = re.compile(rf"\[service{j}_name\]")
            price = re.compile(rf"\[service{j}_price\]")
            aed = re.compile(rf"\[AED{j}\]")
            docx_replace_regex(self.doc, re.compile(index), "")
            docx_replace_regex(self.doc, re.compile(name), "")
            docx_replace_regex(self.doc, re.compile(price), "")
            docx_replace_regex(self.doc, re.compile(aed), "")
