# AI Escape Room: Design and Version Comparison

## Objective and design

The Last Library is a short natural-language escape-room game. The player wakes in a locked library and must inspect a bookshelf, open a combination drawer, retrieve a key, inspect a painting and unlock the exit. The solution is intentionally fixed: the bookshelf reveals drawer code **2413**, the drawer contains a brass key, and the painting reveals exit code **0412**.

The project uses Python and Streamlit for the interface, with Google's Gemini API as an optional language model. The application can also run without a key, which makes local setup and demonstrations possible without exposing credentials. The `.env.example` file documents configuration, and `.gitignore` excludes `.env`.

## Version 1: freeform Game Master

Version 1 sends the setting, intended puzzle path and recent conversation to Gemini. The model responds directly to player messages, so ordinary natural-language play feels flexible. The chat transcript preserves conversational context during a session.

This design leaves important facts under model control. Even with clear instructions, a model can forget an item, invent a clue, reveal a code early or decide that the player has escaped without meeting the conditions. Prompt wording reduces these risks but cannot guarantee consistent state transitions. The version is therefore useful as a baseline rather than a reliable game engine.

## Version 2: state and rules in Python

Version 2 maintains a dictionary containing puzzle flags, inventory, solved puzzles, action history and escape status. A Python action resolver recognizes known room objects and validates puzzle codes. The drawer cannot open unless the four-digit code matches; the door cannot open unless the key is in inventory and the exit code is correct. Unknown objects, wrong codes, false claims and attempts to override the rules return refusal messages without changing the relevant state.

The model is used only after the rule engine has produced an authoritative outcome. It may restyle that outcome, but the result is never interpreted as a new game action. If Gemini is unavailable or errors, the deterministic outcome text is shown. This separation makes the game more predictable while retaining natural-language interaction.

## Test plan and results

The test suite covers nine checks across normal clue discovery, missing key, wrong drawer code, false completion claim, administrator override, secret-code extraction, nonexistent object, wrong exit code and the complete solution. All nine checks passed with `python -m unittest discover -s tests -v`. The critical invariant is that a rejected action does not grant an item, solve a puzzle or set `escaped` to true. A successful route verifies that the intended sequence reaches the escaped state.

Version 1 should be explored with the same adversarial prompts to observe that its answers may vary. Version 2 should be tested against the fixed outcomes listed in the README and by inspecting its structured state panel. The implementation includes unit tests for these checks; run them with `python -m unittest discover -s tests -v`.

## Limitations and reflection

Version 1's main weakness is that prompts are not an enforcement mechanism. Version 2 improves reliability by making Python the authority, but its keyword parser can miss synonyms or ambiguous phrasing. A production-quality extension could map player text to a strict action schema, validate that schema in Python, persist saved games and add multilingual and accessibility support. The game is intentionally small so that its puzzle rules and state transitions are easy to explain in a portfolio review.
