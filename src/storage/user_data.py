import dataclasses as dc
import typing as tp

@dc.dataclass
class UserData:
    username: str
    age: int | None = None
    weight: float | None = None
    height: float | None = None
    activity_time: int | None = None
    city: str | None = None


    def __getitem__(self, key):
        data = dc.asdict(self)
        if key in data:
            return data[key]
        else:
            raise KeyError(f"Key '{key}' not found")


    def __setitem__(self, key, value):
        if hasattr(self, key):
            setattr(self, key, value)
        else:
            raise KeyError(f"Key '{key}' not found")


    def keys(self):
        return dc.asdict(self).keys()


    def values(self):
        return dc.asdict(self).values()


    def items(self):
        return dc.asdict(self).items()


users_data: tp.Dict[int, UserData] = {}
