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

    @property
    def model_field(self):
        return getattr(MailMessage, self.field_name)

    def fail(self, msg="Error occurred"):
        raise ValueError(msg)

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
        match self.predicate.strip().lower():
            case "equals":
                return self.model_field == self.value
            case "not equals":
                return self.model_field != self.value
            case "contains":
                return self.model_field.contains(self.value)
            case "does not contain":
                return ~self.model_field.contains(self.value)

        self.fail(f"This predicate is not supported: {self.predicate}")


@dataclass
class IntegerRules(RuleBase):
    type = "int"

    def filter(self):
        _datetime = datetime.datetime.now() - datetime.timedelta(days=self.value)

        match self.predicate.strip().lower():
            case "greater than":
                return self.model_field > _datetime
            case "less than":
                return self.model_field < _datetime

        self.fail(f"This predicate is not supported: {self.predicate}")
