
import sys
import os
import openai
import numpy as np
import json
import time

from LMP import LMP
from meta_planner_lmp import MetaPlannerLMP
from condition_checker_lmp import ConditionCheckerLMP
from mock_env_mobile import MockEnvMobile

# 1. Use the specific OpenAI client details

# NOTE：Replace the following with your actual OpenAI client details


# If you are in China, you may need to set the base URL 
# Example:
openai.api_key = 'sk-tev4P3Q3VA0jaOl7B3qNCe8sCvQZLPRY16J0iVMhPPwhieBI'
openai.api_base = 'https://poloai.top/v1'


# openai.api_key = 'Your OpenAI API Key'
# openai.api_base = 'If You Need'
print(f"--- OpenAI client configured for base URL: {openai.api_base} ---")


# 2. Create a Subtask Executor LMP for the Loco-Manip scenario
class SubtaskExecutorLMP_Loco:
    def __init__(self, fixed_vars: dict, variable_vars: dict, debug=False):
        
        prompt_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'prompts/loco_manip_prompt.txt'))
        
        cfg = {
            'prompt_fname': prompt_path,
            'stop': [],
            'temperature': 0.0,
            'model': os.environ.get("OPENAI_API_MODEL", "gpt-3.5-turbo"),
            'max_tokens': 1024,
            'query_prefix': '\nInstruction: ',
            'query_suffix': '\n',
            'maintain_session': False,
            'include_context': False,
            'load_cache': False,
            'has_return': False,
        }
        
        self._lmp = LMP(
            name="loco_manip_executor",
            cfg=cfg,
            fixed_vars=fixed_vars,
            variable_vars=variable_vars,
            debug=debug,
            env=''
        )

    def _pddl_to_natural_language(self, pddl_goals: list[str]) -> str:
        nl_parts = []
        for goal in pddl_goals:
            goal = goal.strip()
            if goal.startswith('(holding '):
                obj = goal[len('(holding '):-1].replace('_', ' ')
                nl_parts.append(f"pickup the {obj}")
            elif goal.startswith('(in '):
                obj1 = goal[len('(in '):].split(' ')[0].replace('_', ' ')
                obj2 = goal[len('(in '):-1].split(' ')[1].replace('_', ' ')
                nl_parts.append(f"put the {obj1} in the {obj2}")
            elif goal == '(at upstairs)':
                nl_parts.append("go upstairs")
            else:
                nl_parts.append(f"achieve {goal}")
        
        return ", and ".join(nl_parts) if nl_parts else "do nothing"

    def execute_subtask(self, pddl_goals: list[str], observation_objects: list[str]):
        nl_query = self._pddl_to_natural_language(pddl_goals)
        objects_str = json.dumps(observation_objects).replace('"', "'")
        # Construct the query to match the prompt examples exactly (no "Query:")
        query = f"objects = {objects_str}\n# {nl_query}"
        self._lmp(query)


# 3. Create the Master Planner for the Loco-Manip scenario
class MasterPlannerLoco:
    def __init__(self, debug=False):
        self._debug = debug
        self._mock_env = MockEnvMobile()
        
        # Configure Meta Planner
        meta_prompt_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'prompts/meta_planner_loco_prompt.txt'))
        meta_cfg = {
            'prompt_fname': meta_prompt_path,
            'stop': ['#'],
            'temperature': 0.0,
            'model': os.environ.get("OPENAI_API_MODEL", "gpt-3.5-turbo"),
            'max_tokens': 1024,
            'query_prefix': '\n# High-level instruction: ',
            'query_suffix': '\n',
            'include_context': False,
        }
        self._meta_planner_lmp = MetaPlannerLMP(cfg_override=meta_cfg)

        self._condition_checker_lmp = ConditionCheckerLMP(debug=debug)
        
        # Configure Subtask Executor
        fixed_vars_for_executor = {
            'np': np,
            'say': self._mock_env.say,
            'detect_object': self._mock_env.detect_object,
            'detect_loc': self._mock_env.detect_loc,
            'walking': self._mock_env.walking,
            'running': self._mock_env.running,
            'go_upstairs': self._mock_env.go_upstairs,
            'pickup': self._mock_env.pickup,
            'drop': self._mock_env.drop,
            'parse_position': self._mock_env.parse_position
        }
        self._subtask_executor_lmp = SubtaskExecutorLMP_Loco(
            fixed_vars=fixed_vars_for_executor,
            variable_vars={},
            debug=debug
        )

    def run(self, user_instruction: str):
        print(f"\n--- Master Planner [LOCO-MANIP]: Starting task: '{user_instruction}' ---")
        
        plan_data = self._meta_planner_lmp.generate_plan(user_instruction)
        # plan_data['plan'][2]['exit_condition'] = "the robot's hands are empty"

        
        print("\n--- Initial Plan ---")
        print(json.dumps(plan_data, indent=4))
        
        for i, subtask in enumerate(plan_data['plan']):
            print(f"\n--- Subtask {i + 1}/{len(plan_data['plan'])}: '{subtask['sub_task_name']}' ---")

            loop_count = 0
            max_loops = 3 # Safety break
            while True:
                if loop_count >= max_loops:
                    print("--- Max loops reached for subtask. Moving to next. ---")
                    break

                
                if subtask['exit_condition']:
                    observation_description = self._mock_env.get_observation_description()
                    print(f"Observation: {observation_description}")
                    is_done = self._condition_checker_lmp.check_condition(
                        observation_description, 
                        subtask['exit_condition']
                    )
                    if is_done:
                        print(f"--- Exit condition '{subtask['exit_condition']}' met. ---")
                        break
                
                observation_objects = self._mock_env.get_observation_objects()
                self._subtask_executor_lmp.execute_subtask(
                    subtask['pddl'], 
                    observation_objects
                )
                
                loop_count += 1
                time.sleep(1)

            subtask['status'] = 'completed'
        
        print("\n--- Final Plan Status ---")
        print(json.dumps(plan_data, indent=4))
        print("\n--- Final Environment State ---")
        print(f"Robot is at {self._mock_env.robot_location} on floor {self._mock_env.robot_floor}")
        print(f"Robot hands: Left='{self._mock_env.hands['left']}', Right='{self._mock_env.hands['right']}'")
        print(f"Objects in world: {list(self._mock_env.objects.keys())}")


if __name__ == '__main__':
    print("--- Initializing MasterPlanner Live Mock Test for Mobile Manipulation ---")
    
    planner = MasterPlannerLoco(debug=True)
    instruction = '拿起红色的娃娃，走上楼梯，然后把娃娃放进筐子里'
    planner.run(instruction)

    print("\n--- MasterPlanner Live Mock Test Complete ---")
