from enum import Enum


class RegexProperty(Enum):
    ALL_DATA_API = r'const postData = (\[.+\])'