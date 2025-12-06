
import unittest
from unittest.mock import MagicMock, patch
from wapi.utils.interactive import WAPIInteractiveShell

class TestInteractiveCoverageFinal(unittest.TestCase):
    @patch('wapi.utils.interactive.get_logger')
    def test_interactive_generic_exception_handling(self, mock_get_logger):
        """
        Test generic Exception handling in interactive loop.
        This targets the 'except Exception as e:' block in WAPIInteractiveShell.run.
        """
        mock_client = MagicMock()
        shell = WAPIInteractiveShell(mock_client)
        
        # Setup mock input to raise Exception once, then StopIteration (to exit)
        mock_input = MagicMock()
        mock_input.side_effect = [
            RuntimeError("Test Error"), 
            StopIteration
        ]
        
        # Execute
        with patch('builtins.print'):
            result = shell.run(_input_mock=mock_input)
        
        # Verify results
        self.assertEqual(result, 1) # StopIteration returns 1
        
        # Verify logger was called with error
        # We expect: logger.error(f"Error in interactive mode: {e}")
        # And then: logger.error("Input stream exhausted...")
        
        # Check for our specific error
        found_error = False
        for call in shell.logger.error.call_args_list:
            if "Error in interactive mode: Test Error" in str(call):
                found_error = True
                break
        
        self.assertTrue(found_error, "Generic exception was not caught/logged as expected")
