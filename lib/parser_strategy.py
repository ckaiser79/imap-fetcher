from abc import ABC, abstractmethod
from email.message import Message

class EmailParserStrategy(ABC):
    @abstractmethod
    def parse(self, msg: Message) -> None:
        pass
