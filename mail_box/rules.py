import datetime
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Type, Union

from .db_tables import MailMessage


@dataclass
class RuleBase(ABC):
    type = None
    __rule_types = {}
    value: Union[int, str]
    field_name: str
    predicate: str

    def __init_subclass__(cls, **kwargs):
        assert cls not in RuleBase.__rule_types, "Duplicate Downloader strategy"
        RuleBase.__rule_types[cls.type] = cls

    @staticmethod
    def get_rule(key: str) -> Type["RuleBase"]:
        if key not in RuleBase.__rule_types:
            raise NotImplementedError
        return RuleBase.__rule_types[key]

    @abstractmethod
    def filter(self):
        pass


@dataclass
class StringRules(RuleBase):
    type = "str"

    def filter(self):
        field = getattr(MailMessage, self.field_name)
        if self.predicate.strip() == "equals":
            return field == self.value
        elif self.predicate.strip() == "not equals":
            return field != self.value
        elif self.predicate.strip().lower() == "contains":
            return field.contains(self.value)
        elif self.predicate.strip() == "does not contain":
            return ~field.contains(self.value)
        raise ValueError(f"This predicate is not supported: {self.predicate}")


@dataclass
class IntegerRules(RuleBase):
    type = "int"

    def filter(self):
        field = getattr(MailMessage, self.field_name)
        _datetime = datetime.datetime.now() - datetime.timedelta(days=self.value)
        if self.predicate.strip() == "greater than":
            return field > _datetime
        elif self.predicate.strip() == "less than":
            return field < _datetime
        raise ValueError(f"This predicate is not supported: {self.predicate}")
