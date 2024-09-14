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

    def __str__(self):
        return f"{self.value}{self.unit}"
