from copy import deepcopy
from typing import List, Dict, Any, Optional, Union, Type, TypeVar

from pymongo.results import DeleteResult

from antispam.caches.mongo.document import Document, return_converted

T = TypeVar("T")


class MockedDocument(Document):
    """
    This only mocks the required methods.

    'Mongo' is just a local, internal dict.
    """

    def __init__(self, data, converter=None):
        self._data: List[Dict[str, Any]] = data
        self.converter: Type[T] = converter

    @staticmethod
    def compare_keys(filter_dict: Dict, compare_to_dict: Dict):
        """Given a two dicts, return True if is subset"""
        for k, v in filter_dict.items():
            try:
                if compare_to_dict[k] != v:
                    return False
            except KeyError:
                return False

        return True

    @return_converted
    async def find_by_custom(
        self, filter_dict: Dict[str, Any]
    ) -> Optional[Union[Dict[str, Any], Type[T]]]:
        self.__ensure_dict(filter_dict)

        for entry in self._data:
            if self.compare_keys(filter_dict, entry):
                return entry

        return None

    @return_converted
    async def find_many_by_custom(
        self, filter_dict: Dict[str, Any]
    ) -> List[Union[Dict[str, Any], Type[T]]]:
        self.__ensure_dict(filter_dict)
        to_return = []
        for entry in self._data:
            if self.compare_keys(filter_dict, entry):
                to_return.append(deepcopy(entry))

        return to_return

    @return_converted
    async def get_all(
        self, filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Optional[Union[Dict[str, Any], Type[T]]]]:
        if filter_dict is None:
            return deepcopy(self._data)

        return await self.find_many_by_custom(filter_dict)

    async def delete_by_custom(self, filter_dict: Dict[str, Any]):
        to_delete = []
        for i, entry in enumerate(deepcopy(self._data)):
            if self.compare_keys(filter_dict, entry):
                to_delete.append(i)

        for item in reversed(to_delete):
            self._data.pop(item)

    async def update_by_custom(
        self,
        filter_dict: Dict[str, Any],
        update_data: Dict[str, Any],
        option: str = "set",
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.__ensure_dict(filter_dict)
        self.__ensure_dict(update_data)

        for entry in self._data:
            if self.compare_keys(filter_dict, entry):
                entry.update(**update_data)
                return

        # Insert when it doesnt exist
        self._data.append({**filter_dict, **update_data})

    @staticmethod
    def __ensure_list_of_dicts(data: List[Dict]):
        assert isinstance(data, list)
        assert all(isinstance(entry, dict) for entry in data)

    @staticmethod
    def __ensure_dict(data: Dict[str, Any]) -> None:
        assert isinstance(data, dict)

    @staticmethod
    def __ensure_id(data: Dict[str, Any]) -> None:
        assert "_id" in data

    @staticmethod
    def __convert_filter(data: Union[Dict, Any]) -> Dict:
        return data if isinstance(data, dict) else {"_id": data}
