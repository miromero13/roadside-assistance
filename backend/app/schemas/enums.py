# app/schemas/enums.py
from enum import Enum

class UserTypeEnum(str, Enum):
    hearing = "hearing"
    deaf_mute = "deaf_mute"

class GenderEnum(str, Enum):
    male = "male"
    female = "female"
