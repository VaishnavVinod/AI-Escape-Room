"""Deterministic game rules for Version 2 of the AI Escape Room."""
from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Any

DRAWER_CODE = "2413"
EXIT_CODE = "0412"
KNOWN_OBJECTS = {"desk", "bookshelf", "books", "painting", "drawer", "door", "room", "exit"}


def new_state() -> dict[str, Any]:
    return {
        "drawer_open": False,
        "desk_examined": False,
        "bookshelf_examined": False,
        "painting_examined": False,
        "inventory": [],
        "solved_puzzles": [],
        "escaped": False,
        "actions": [],
    }


@dataclass
class Outcome:
    text: str
    event: str
    success: bool = True


def _record(state: dict[str, Any], action: str, event: str) -> None:
    state["actions"].append({"action": action, "event": event})


def resolve_action(state: dict[str, Any], user_text: str) -> Outcome:
    """Parse a natural-language command and apply only allowed state changes."""
    text = user_text.lower().strip()
    if state["escaped"]:
        return Outcome("You are already outside the library. Start a new game to play again.", "already_escaped", False)
    if not text:
        return Outcome("Try an action such as 'examine the bookshelf' or 'open the drawer with code 2413'.", "empty", False)

    # Requests to disclose the answer or override the game are never actions.
    if any(p in text for p in ("reveal all", "tell me the solution", "show the code", "ignore the rules", "administrator", "admin", "unlock the exit immediately", "pretend i solved")):
        msg = "The library's rules do not change on request. Explore the room and solve its clues to earn the key and exit code."
        _record(state, text, "refused_override")
        return Outcome(msg, "refused_override", False)

    if any(w in text for w in ("restart", "start over", "new game")):
        fresh = new_state()
        state.clear()
        state.update(fresh)
        return Outcome("A fresh story begins. You wake in the locked library. The desk, bookshelf, painting, locked drawer and exit door are here. What will you inspect?", "restart")

    # Find the targeted object from the known room; unknown names cannot mutate state.
    obj = next((name for name in ("bookshelf", "books", "painting", "drawer", "desk", "door", "exit") if name in text), None)
    if obj is None:
        _record(state, text, "unknown_action")
        return Outcome("I cannot identify that object or action in this room. You can inspect the desk, bookshelf, painting, drawer or door.", "unknown_action", False)

    if obj in ("bookshelf", "books") and any(v in text for v in ("examine", "inspect", "look", "read", "check")):
        state["bookshelf_examined"] = True
        if "bookshelf_code" not in state["solved_puzzles"]:
            state["solved_puzzles"].append("bookshelf_code")
        _record(state, text, "bookshelf_clue")
        return Outcome("Four books sit out of order. Their marked numbers, read left to right, are 2, 4, 1, 3. This is the drawer code.", "bookshelf_clue")

    if obj == "desk" and any(v in text for v in ("examine", "inspect", "look", "check")):
        state["desk_examined"] = True
        _record(state, text, "desk_note")
        return Outcome("A note on the desk says: 'The drawer guards a key. The painting guards the way out.'", "desk_note")

    if obj == "painting" and any(v in text for v in ("examine", "inspect", "look", "check", "move", "behind")):
        state["painting_examined"] = True
        if "painting_code" not in state["solved_puzzles"]:
            state["solved_puzzles"].append("painting_code")
        _record(state, text, "painting_clue")
        return Outcome("Behind the painting is a brass plate engraved with 0412. Keep this four-digit exit code.", "painting_clue")

    if obj == "drawer":
        if state["drawer_open"]:
            _record(state, text, "drawer_already_open")
            return Outcome("The drawer is already open and empty except for the brass key you collected.", "drawer_already_open")
        digits = re.findall(r"(?<!\d)\d{4}(?!\d)", text)
        if any(v in text for v in ("open", "unlock", "enter", "try", "use")) and digits:
            if digits[-1] == DRAWER_CODE:
                state["drawer_open"] = True
                if "brass_key" not in state["inventory"]:
                    state["inventory"].append("brass_key")
                if "drawer_code" not in state["solved_puzzles"]:
                    state["solved_puzzles"].append("drawer_code")
                _record(state, text, "drawer_unlocked")
                return Outcome("The code is correct. The drawer opens, and you take the brass key.", "drawer_unlocked")
            _record(state, text, "wrong_drawer_code")
            return Outcome("The drawer stays locked. That four-digit code is incorrect. Look for a clue among the books.", "wrong_drawer_code", False)
        _record(state, text, "drawer_locked")
        return Outcome("The drawer is locked by a four-digit combination. Find the code before trying it.", "drawer_locked", False)

    if obj in ("door", "exit"):
        if "brass_key" not in state["inventory"]:
            _record(state, text, "missing_key")
            return Outcome("The exit has a keyhole and keypad. You need the brass key from the drawer first.", "missing_key", False)
        if not any(v in text for v in ("unlock", "open", "use", "enter", "try", "escape")):
            _record(state, text, "door_observed")
            return Outcome("The exit door needs the brass key and a four-digit code.", "door_observed")
        digits = re.findall(r"(?<!\d)\d{4}(?!\d)", text)
        if not digits:
            _record(state, text, "missing_exit_code")
            return Outcome("You have the key, but the keypad still needs a four-digit code. Inspect the painting.", "missing_exit_code", False)
        if digits[-1] != EXIT_CODE:
            _record(state, text, "wrong_exit_code")
            return Outcome("The key turns, but the keypad flashes red. That exit code is incorrect.", "wrong_exit_code", False)
        state["escaped"] = True
        if "escape" not in state["solved_puzzles"]:
            state["solved_puzzles"].append("escape")
        _record(state, text, "escaped")
        return Outcome("The code is accepted. The door swings open, and cool night air reaches you. You escaped the library!", "escaped")

    _record(state, text, "object_unavailable")
    return Outcome("That action is not available for this object. Try examining it, or use a discovered code on the drawer or door.", "object_unavailable", False)


def state_summary(state: dict[str, Any]) -> str:
    return (f"Inventory: {state['inventory'] or 'empty'}; solved: {state['solved_puzzles'] or 'none'}; "
            f"drawer open: {state['drawer_open']}; escaped: {state['escaped']}.")
