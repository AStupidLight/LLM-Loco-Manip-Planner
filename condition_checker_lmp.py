
import os
from LMP import LMP

class ConditionCheckerLMP:
    def __init__(self, debug=False):
        # Configuration for the Condition Checker LMP
        cfg = {
            'prompt_fname': 'condition_checker_prompt',
            'stop': [], # Removed stop to allow full response
            'temperature': 0.0,
            'model': os.environ.get("OPENAI_API_MODEL", "gpt-3.5-turbo"),
            'max_tokens': 10, # Increased max_tokens
            'query_prefix': 'Observation:\n{observation_description}\n\nCondition:\n{condition_string}\n\nIs the condition true?\n',
            'query_suffix': '',
            'maintain_session': False,
            'include_context': False,
            'load_cache': False,
            'has_return': True,
            'return_val_name': 'ret_val' # Dummy, as we'll parse the output ourselves
        }

        fixed_vars = {}
        variable_vars = {}

        self._lmp = LMP(
            name="condition_checker",
            cfg=cfg,
            fixed_vars=fixed_vars,
            variable_vars=variable_vars,
            debug=debug,
            env='' # All prompts are in the same folder
        )

    def check_condition(self, observation_description: str, condition_string: str) -> bool:
        """
        Evaluates a condition based on the provided observation description using an LMP.

        Args:
            observation_description: A textual description of the current environment observation.
            condition_string: The condition to evaluate (e.g., "no more blocks to pick up").

        Returns:
            True if the condition is met, False otherwise.
        """
        print(f"--- Checking condition: '{condition_string}' with observation: '{observation_description[:50]}...' ---")
        
        # Format the query for the LMP
        query = self._lmp._cfg['query_prefix'].format(
            observation_description=observation_description,
            condition_string=condition_string
        )

        response_str = self._lmp(query,is_condition_checker=True)
        print(f"--- ConditionCheckerLMP raw response: '{response_str.strip()}' ---")
        
        # Robustly parse the response
        lower_response = response_str.strip().lower()
        if lower_response == 'true':
            print("--- Condition is TRUE ---")
            return True
        elif lower_response == 'false':
            print("--- Condition is FALSE ---")
            return False
        else:
            print(f"Warning: ConditionCheckerLMP returned unexpected response: '{response_str}'. Assuming False.")
            return False

if __name__ == '__main__':
    # Test cases for ConditionCheckerLMP
    if "OPENAI_API_KEY" not in os.environ:
        print("Error: OPENAI_API_KEY environment variable not set.")
    else:
        checker = ConditionCheckerLMP()

        # Test 1: Condition is expected to be True
        print("\n--- Running Test Case 1: True Condition ---")
        obs1 = "The room contains only a red ball and a green cylinder. There are no blocks visible."
        cond1 = "no more blocks to pick up"
        result1 = checker.check_condition(obs1, cond1)
        print(f"Result for Test 1: {result1}")
        assert result1 is True, "Test 1 Failed: Expected True"

        # Test 2: Condition is expected to be False
        print("\n--- Running Test Case 2: False Condition ---")
        obs2 = "The room contains a red block and a blue ball. A yellow block is also on the table."
        cond2 = "no more blocks to pick up"
        result2 = checker.check_condition(obs2, cond2)
        print(f"Result for Test 2: {result2}")
        assert result2 is False, "Test 2 Failed: Expected False"

        # Test 3: Holding an object
        print("\n--- Running Test Case 3: Holding condition True ---")
        obs3 = "The robot is currently holding a red apple."
        cond3 = "holding apple"
        result3 = checker.check_condition(obs3, cond3)
        print(f"Result for Test 3: {result3}")
        assert result3 is True, "Test 3 Failed: Expected True"
        
        # Test 4: Not holding an object
        print("\n--- Running Test Case 4: Holding condition False ---")
        obs4 = "The robot is currently holding a red apple."
        cond4 = "holding banana"
        result4 = checker.check_condition(obs4, cond4)
        print(f"Result for Test 4: {result4}")
        assert result4 is False, "Test 4 Failed: Expected False"

        print("\nAll ConditionCheckerLMP tests passed (assuming LLM gives expected output for dummy key).")
