from sqlalchemy import Double, String
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    type_annotation_map = {
        str: String(255),
        float: Double,
    }