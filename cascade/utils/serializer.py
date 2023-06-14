import pickle
from typing import Any


class Serializer:
    @staticmethod
    def deserialize(obj: str):
        return pickle.loads(bytes.fromhex(obj))

    @staticmethod
    def serialize(obj: Any) -> str:
        return pickle.dumps(obj).hex()
