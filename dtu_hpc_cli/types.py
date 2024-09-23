import re
from enum import StrEnum

import typer


class MemoryUnit(StrEnum):
    B = "B"
    KB = "KB"
    MB = "MB"
    GB = "GB"
    TB = "TB"


class Memory:
    expected_format_msg = (
        "Expected format: [value][unit]\n"
        + "[value] is a positive integer\n"
        + "[unit] is one of: B, KB, MB, GB, TB.\n"
        + "[unit] is case insensitive."
    )

    def __init__(self, value: int, unit: MemoryUnit):
        self.value = value
        self.unit = unit

    @classmethod
    def parse(cls, memory: str) -> "Memory":
        memory = memory.upper()

        if len(memory) == 0:
            raise typer.BadParameter("Got empty string.")

        if not memory[0].isdigit():
            raise typer.BadParameter(f"Missing a value.\n{cls.expected_format_msg}")

        unit_start = 0
        while unit_start < len(memory) and memory[unit_start].isdigit():
            unit_start += 1

        if unit_start == len(memory):
            raise typer.BadParameter(f"Missing a unit.\n{cls.expected_format_msg}")

        value = int(memory[:unit_start])
        unit = memory[unit_start:]

        match unit:
            case MemoryUnit.B.value:
                return cls(value, MemoryUnit.B)
            case MemoryUnit.KB.value:
                return cls(value, MemoryUnit.KB)
            case MemoryUnit.MB.value:
                return cls(value, MemoryUnit.MB)
            case MemoryUnit.GB.value:
                return cls(value, MemoryUnit.GB)
            case MemoryUnit.TB.value:
                return cls(value, MemoryUnit.TB)
            case _:
                raise typer.BadParameter(f"Unit '{unit}' is not supported.\n{cls.expected_format_msg}")

    def __repr__(self):
        return f"Memory(value={self.value}, unit={self.unit})"

    def __str__(self):
        return f"{self.value}{self.unit}"


class Time:
    pattern = re.compile(r"(\d+d)?(\d+h)?(\d+m)?")

    expected_format_msg = (
        "Expected format: [days]d[hours]h[minutes]m\n" + "All parts are optional.\n" + "Example: 1d2h3m"
    )

    def __init__(self, days: int, hours: int, minutes: int):
        self.days = days
        self.hours = hours
        self.minutes = minutes

    @classmethod
    def parse(cls, time: str):
        if len(time) == 0:
            raise typer.BadParameter("Got empty string.")

        match = cls.pattern.fullmatch(time)

        if match is None:
            raise typer.BadParameter(f"Invalid format.\n{cls.expected_format_msg}")

        days = match.group(1)
        hours = match.group(2)
        minutes = match.group(3)

        if days is None:
            days = 0
        else:
            days = int(days[:-1])

        if hours is None:
            hours = 0
        else:
            hours = int(hours[:-1])

        if minutes is None:
            minutes = 0
        else:
            minutes = int(minutes[:-1])

        if minutes > 59:
            raise typer.BadParameter("Minutes must be less than 60.")

        if hours > 23:
            raise typer.BadParameter("Hours must be less than 24.")

        return cls(days, hours, minutes)

    def is_zero(self) -> bool:
        return self.days == 0 and self.hours == 0 and self.minutes == 0

    def total_hours(self) -> int:
        return self.days * 24 + self.hours

    def __repr__(self):
        return f"Time(days={self.days}, hours={self.hours}, minutes={self.minutes})"

    def __str__(self):
        return f"{self.days}d{self.hours:02d}h{self.minutes:02d}m"

    def __add__(self, other: "Time"):
        days = self.days + other.days
        hours = self.hours + other.hours
        minutes = self.minutes + other.minutes

        if minutes >= 60:
            minutes -= 60
            hours += 1

        if hours >= 24:
            hours -= 24
            days += 1

        return Time(days, hours, minutes)

    def __sub__(self, other: "Time"):
        if self < other:
            return Time(0, 0, 0)

        days = self.days - other.days
        hours = self.hours - other.hours
        minutes = self.minutes - other.minutes

        if minutes < 0:
            minutes += 60
            hours -= 1

        if hours < 0:
            hours += 24
            days -= 1

        return Time(days, hours, minutes)

    def __lt__(self, other: "Time"):
        return (
            self.days < other.days
            or (self.days == other.days and self.hours < other.hours)
            or (self.days == other.days and self.hours == other.hours and self.minutes < other.minutes)
        )

    def __gt__(self, other: "Time"):
        return (
            self.days > other.days
            or (self.days == other.days and self.hours > other.hours)
            or (self.days == other.days and self.hours == other.hours and self.minutes > other.minutes)
        )

    def __eq__(self, other: "Time"):
        if not isinstance(other, Time):
            return False
        return self.days == other.days and self.hours == other.hours and self.minutes == other.minutes
