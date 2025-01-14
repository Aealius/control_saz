from dataclasses import dataclass


@dataclass
class CreateMemoDTO():
    department:str
    full_department: str
    headName:str
    headSurname:str
    headPatronymic:str
    headPosition:str
    headSignaturePath:str