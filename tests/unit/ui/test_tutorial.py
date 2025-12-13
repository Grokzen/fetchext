import unittest
from unittest.mock import MagicMock, patch
from fetchext.tutorial import get_tutorial_classes, TUTORIAL_STEPS

# Get classes dynamically
TutorialApp, TutorialStep = get_tutorial_classes()

class TestTutorial(unittest.TestCase):
    def test_tutorial_steps_content(self):
        """Verify tutorial steps are defined and have content."""
        self.assertTrue(len(TUTORIAL_STEPS) > 0)
        for step in TUTORIAL_STEPS:
            self.assertIn("title", step)
            self.assertIn("content", step)
            self.assertTrue(len(step["content"]) > 0)

    def test_app_instantiation(self):
        """Verify the app can be instantiated."""
        with patch.object(TutorialApp, 'run'):
            app = TutorialApp()
            self.assertIsNotNone(app)
            self.assertEqual(app.current_step, 0)

    def test_step_navigation_logic(self):
        """Test navigation logic without running the UI."""
        app = TutorialApp()
        
        # Mock UI methods that depend on the screen stack
        app.update_step = MagicMock()
        app.exit = MagicMock()
        
        # Initial state
        self.assertEqual(app.current_step, 0)
        
        # Next step
        app.action_next_step()
        self.assertEqual(app.current_step, 1)
        app.update_step.assert_called()
        
        # Go back
        app.action_prev_step()
        self.assertEqual(app.current_step, 0)
        
        # Try to go back from 0
        app.action_prev_step()
        self.assertEqual(app.current_step, 0)
        
        # Go to end
        app.current_step = len(TUTORIAL_STEPS) - 1
        app.action_next_step()
        app.exit.assert_called()
