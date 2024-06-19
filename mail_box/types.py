from dataclasses import dataclass, field


@dataclass
class MessageAction:
    ids: list[str]
    add_labels: list[str] = field(default_factory=lambda: [])
    remove_labels: list[str] = field(default_factory=lambda: [])
