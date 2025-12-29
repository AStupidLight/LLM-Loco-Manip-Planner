import json
import os
from LMP import LMP

class MetaPlannerLMP:
    def __init__(self, debug=False, cfg_override=None):
        # Configuration for the Meta Planner LMP
        cfg = {
            'prompt_fname': 'master_planner_prompt',
            'stop': ['}"'],
            'temperature': 0.0,
            'model': os.environ.get("OPENAI_API_MODEL", "gpt-5-turbo"),
            'max_tokens': 1024,
            'query_prefix': '',
            'query_suffix': '',
            'maintain_session': False,
            'include_context': False,
            'load_cache': os.environ.get("USE_LLM_CACHE", "True").lower() == "true",
            'has_return': True,
            'return_val_name': 'ret_val' # a dummy return value name
        }
        if cfg_override:
            cfg.update(cfg_override)

        # The meta planner does not need access to external functions,
        # so fixed_vars and variable_vars are empty.
        fixed_vars = {}
        variable_vars = {}

        # Instantiate the base LMP
        self._lmp = LMP(
            name="meta_planner",
            cfg=cfg,
            fixed_vars=fixed_vars,
            variable_vars=variable_vars,
            debug=debug,
            env=''  # All prompts are in the same folder
        )

    def generate_plan(self, user_prompt: str) -> dict:
        """
        Takes a high-level user prompt and returns a structured JSON plan.

        Args:
            user_prompt: The natural language instruction from the user.

        Returns:
            A dictionary representing the structured plan.
        """
        print(f"--- Generating meta-plan for: '{user_prompt}' ---")
        
        # The LMP returns a string, which should be a JSON object
        response_str = self._lmp(user_prompt)

        try:
            # The model might return text before or after the JSON object.
            # We find the first '{' and the last '}' to extract the JSON.
            json_start = response_str.find('{')
            json_end = response_str.rfind('}')
            
            if json_start == -1 or json_end == -1:
                raise json.JSONDecodeError("Could not find JSON object in LLM response.", response_str, 0)

            # The stop token is '}', so we need to add it back.
            json_str = response_str[json_start : json_end + 1]
            
            # Parse the JSON string into a Python dictionary
            plan = json.loads(json_str)
            print("--- Meta-plan generated successfully ---")
            return plan
        except json.JSONDecodeError as e:
            print(f"Error: Could not decode JSON from LLM response.")
            print(f"LLM Response:\n---\n{response_str}\n---")
            raise e

if __name__ == '__main__':
    # This is a simple test to run if the file is executed directly.
    # It requires OPENAI_API_KEY to be set as an environment variable.
    if "OPENAI_API_KEY" not in os.environ:
        print("Error: OPENAI_API_KEY environment variable not set.")
    else:
        # Test Case 1: Simple sequential plan
        print("\n--- Running Test Case 1: Simple Sequential Plan ---")
        meta_planner = MetaPlannerLMP()
        try:
            plan1 = meta_planner.generate_plan("put the apple in the box")
            print("Generated Plan 1:")
            print(json.dumps(plan1, indent=4))
        except Exception as e:
            print(f"Test Case 1 Failed: {e}")

        # Test Case 2: Looping plan
        print("\n--- Running Test Case 2: Looping Plan ---")
        try:
            plan2 = meta_planner.generate_plan("clean up all the blocks")
            print("Generated Plan 2:")
            print(json.dumps(plan2, indent=4))
        except Exception as e:
            print(f"Test Case 2 Failed: {e}")
