from __future__ import annotations

from modes.generate_questions_mode import run_generate_questions
from modes.manage_questions_mode import run_manage_questions
from modes.practice_mode import run_practice
from modes.statistics_viewing_mode import run_statistics_viewing
from modes.test_mode import run_test

MODES: list[str] = [
    "Generate Questions Mode",
    "Statistics Viewing Mode",
    "Manage Questions Mode",
    "Practice Mode",
    "Test Mode",
]


def prompt_mode() -> str | None:
    """Prompt the user to choose a mode and return the chosen mode string."""
    print("\nSelect a mode:")
    for i, mode in enumerate(MODES, start=1):
        print(f"{i}. {mode}")

    while True:
        try:
            mode_user_input = input(
                "Enter the number corresponding to the mode (or type 'exit' to quit): "
            ).strip()
        except EOFError:
            mode_user_input = ""

        if not mode_user_input:
            print("No selection made. Please choose a mode by entering its number.")
            continue

        if mode_user_input.lower() == "exit":
            print("Bye! See you later!")
            return None

        if mode_user_input.isdigit():
            mode_index = int(mode_user_input)
            if 1 <= mode_index <= len(MODES):
                return MODES[mode_index - 1]
        print("Invalid selection. Please enter a valid number or 'exit'.")


def main() -> None:
    """Main loop: repeatedly prompt for mode and dispatch.

    Returning from any mode will re-open the main menu. Use Ctrl+C / EOF to exit.
    """
    while True:
        mode = prompt_mode()
        if mode is None:
            return
        if mode == "Generate Questions Mode":
            run_generate_questions()
        elif mode == "Statistics Viewing Mode":
            run_statistics_viewing()
        elif mode == "Manage Questions Mode":
            run_manage_questions()
        elif mode == "Practice Mode":
            run_practice()
        elif mode == "Test Mode":
            run_test()
        else:
            print("Unknown mode. Returning to main menu.")


if __name__ == "__main__":
    main()
