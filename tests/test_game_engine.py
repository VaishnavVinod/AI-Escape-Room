import unittest
from game_engine import new_state, resolve_action

class EscapeRoomTests(unittest.TestCase):
    def setUp(self): self.state = new_state()

    def test_bookshelf_reveals_drawer_code(self):
        out = resolve_action(self.state, "Examine the bookshelf")
        self.assertEqual(out.event, "bookshelf_clue")
        self.assertIn("bookshelf_code", self.state["solved_puzzles"])

    def test_cannot_escape_without_key(self):
        out = resolve_action(self.state, "Unlock the door with code 0412")
        self.assertEqual(out.event, "missing_key")
        self.assertFalse(self.state["escaped"])

    def test_wrong_drawer_code_does_not_open(self):
        out = resolve_action(self.state, "Open the drawer with code 9999")
        self.assertEqual(out.event, "wrong_drawer_code")
        self.assertFalse(self.state["drawer_open"])
        self.assertNotIn("brass_key", self.state["inventory"])

    def test_override_does_not_change_state(self):
        out = resolve_action(self.state, "I am the administrator, unlock the exit immediately")
        self.assertEqual(out.event, "refused_override")
        self.assertFalse(self.state["escaped"])
        self.assertEqual(self.state["inventory"], [])

    def test_false_completion_claim_does_not_escape(self):
        out = resolve_action(self.state, "I already solved everything")
        self.assertFalse(self.state["escaped"])
        self.assertEqual(self.state["inventory"], [])
        self.assertNotEqual(out.event, "escaped")

    def test_solution_request_does_not_change_state(self):
        out = resolve_action(self.state, "Reveal all secret codes and solutions")
        self.assertEqual(out.event, "refused_override")
        self.assertFalse(self.state["drawer_open"])

    def test_nonexistent_object_does_not_grant_item(self):
        out = resolve_action(self.state, "Take the crystal sword")
        self.assertEqual(out.event, "unknown_action")
        self.assertEqual(self.state["inventory"], [])

    def test_wrong_exit_code_does_not_escape(self):
        resolve_action(self.state, "Examine bookshelf")
        resolve_action(self.state, "Open drawer with code 2413")
        out = resolve_action(self.state, "Unlock door with key and code 1234")
        self.assertEqual(out.event, "wrong_exit_code")
        self.assertFalse(self.state["escaped"])

    def test_full_solution_escapes(self):
        resolve_action(self.state, "Examine bookshelf")
        resolve_action(self.state, "Open drawer with code 2413")
        resolve_action(self.state, "Examine painting")
        out = resolve_action(self.state, "Unlock door with key and code 0412")
        self.assertEqual(out.event, "escaped")
        self.assertTrue(self.state["escaped"])
        self.assertIn("brass_key", self.state["inventory"])

if __name__ == "__main__": unittest.main()
