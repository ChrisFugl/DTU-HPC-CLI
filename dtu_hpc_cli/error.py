import sys

import rich


def error_and_exit(message: str, code: int = 1):
    panel = rich.panel.Panel(message, border_style="red", title="Error", title_align="left")
    rich.print(panel)
    sys.exit(code)
