from dataclasses import dataclass

@dataclass(frozen = True)
class spot:
    id: int
    number: int
    zone_id: int
    status : str
