from enum import Enum, IntEnum

ICU_BEDS = 1000


class EventType(str, Enum):
    pcr = "pcr"
    death = "death"
    confirmed_case = "confirmed_case"
    icu_beds_completeness = "icu_beds_completeness"
