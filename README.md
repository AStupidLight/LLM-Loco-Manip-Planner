# Loco-Manipulation Standalone LMP

这是一个基于大型语言模型（LLM）的移动操作机器人控制系统的独立实现。项目的设计受到了 [VoxPoser](https://voxposer.github.io/) 和[CodeAsPolicies](https://code-as-policies.github.io/) 的启发，采用分层控制的思想，将高层级的自然语言指令分解为机器人可以执行的具体动作序列。

## 工作流程

1.  **高级指令**: 用户提供一个高层级的自然语言指令 (例如: "拿起红色的娃娃，走上楼梯，然后把它放进筐子里")。
2.  **元规划器 (Meta Planner)**: `meta_planner_lmp.py` 中的元规划器接收该指令，并向 LLM 查询，生成一个结构化的子任务序列（以JSON格式）。每个子任务都包含 PDDL 风格的目标和自然语言描述的退出条件。
3.  **任务执行与条件检查**: 主循环 (`run_test.py`) 遍历每个子任务。
    *   在执行前，`condition_checker_lmp.py` 中的条件检查器会判断当前子任务的退出条件是否已经满足。如果满足，则跳过该子任务。
    *   `LMP.py` 中的子任务执行器将 PDDL 目标转换为具体的 Python 代码，并在模拟环境中执行。
4.  **模拟环境 (Mock Environment)**: `mock_env_mobile.py` 提供一个虚拟的机器人和环境，用于执行生成的代码并反馈结果。

## 文件结构

-   `run_test.py`: 项目的主入口，用于运行一个完整的测试流程。你可以在这里配置你的 API 密钥和要执行的指令。
-   `LMP.py`: 核心的语言模型程序（LMP）引擎，负责构建提示（Prompt）、调用 LLM API 并执行返回的代码。
-   `meta_planner_lmp.py`: 元规划器，负责将用户的高级指令分解为一系列结构化的子任务。
-   `condition_checker_lmp.py`: 条件检查器，使用 LLM 判断一个子任务的退出条件是否在当前环境中得到满足。
-   `mock_env_mobile.py`: 移动机器人的模拟环境。它包含一个可以上下楼、导航、抓取和放置物体的虚拟机器人。
-   `prompts/`: 存放与 LLM 交互时使用的各种提示模板。
-   `requirements.txt`: 项目所需的 Python 依赖库。
-   `LLM_cache.py`: 为 LLM 的 API 调用提供缓存功能，可以避免重复请求，节省时间和成本。

## 模拟环境 (`mock_env_mobile.py`)

为了在没有真实机器人的情况下测试算法，项目实现了一个简单的模拟环境：

-   **世界**: 环境模拟了一个包含两层楼的场景。
-   **机器人**: 机器人拥有自己的坐标和所在楼层，双手可以抓取物品。
-   **物体与位置**: 环境中预定义了多个物体（如 `red doll`, `basket`）和位置（如 `table`, `stairs entrance`）。
-   **动作**: 机器人可以执行 `walking`, `running`, `pickup`, `drop`, `go_upstairs` 等模拟动作。所有动作的执行结果都会通过打印信息显示在控制台中。

## 使用方法

1.  **配置 API 密钥**

    打开 `run_test.py` 文件，找到以下代码行，并填入你的 OpenAI API Key。如果你使用代理，还需要配置 `api_base`。

    ```python
    # NOTE：Replace the following with your actual OpenAI client details
    openai.api_key = 'Your OpenAI API Key'
    openai.api_base = 'If You Need' # e.g., 'https://api.openai.com/v1'
    ```

2.  **安装依赖**

    在项目根目录下打开终端，运行以下命令来安装所需库：

    ```bash
    pip install -r requirements.txt
    ```

3.  **运行测试**

    执行主程序来观看测试流程：

    ```bash
    python run_test.py
    ```

    你将会在终端看到详细的输出，包括元规划器生成的计划、每个子任务的执行过程以及机器人在模拟环境中的状态变化。

4.  **自定义指令**

    你可以修改 `run_test.py` 文件底部的 `instruction` 变量来测试你自己的指令：
    ==注意，你需要针对你的具体任务和API做对应的Prompt Engineering，输出的效果才会比较好==

    ```python
    if __name__ == '__main__':
        # ...
        planner = MasterPlannerLoco(debug=True)
        # 修改这里的指令
        instruction = '拿起红色的娃娃，走上楼梯，然后把娃娃放进筐子里'
        planner.run(instruction)
        # ...
    ```

## 运行结果


```
(voxposer-env) raychen@raychen-MS-Terminator-B760M-D5:~/桌面/test/loco_manip_standalone$ /home/raychen/miniconda3/envs/voxposer-env/bin/python /home/raychen/桌面/test/loco_manip_standalone/run_test.py
--- OpenAI client configured for base URL: https://poloai.top/v1 ---
--- Initializing MasterPlanner Live Mock Test for Mobile Manipulation ---
--- Mobile Mock Environment Initialized ---
Robot starting at (0, 0) on floor 1

--- Master Planner [LOCO-MANIP]: Starting task: '拿起红色的娃娃，走上楼梯，然后把娃娃放进筐子里' ---
--- Generating meta-plan for: '拿起红色的娃娃，走上楼梯，然后把娃娃放进筐子里' ---
*** OpenAI API call took 3.32s ***
--- Meta-plan generated successfully ---

--- Initial Plan ---
{
    "task": "\u62ff\u8d77\u7ea2\u8272\u7684\u5a03\u5a03\uff0c\u8d70\u4e0a\u697c\u68af\uff0c\u7136\u540e\u628a\u5a03\u5a03\u653e\u8fdb\u7b50\u5b50\u91cc",
    "plan": [
        {
            "sub_task_name": "pick up the red doll",
            "pddl": [
                "(holding red_doll)"
            ],
            "status": "pending",
            "exit_condition": "the robot is holding a red doll"
        },
        {
            "sub_task_name": "go upstairs",
            "pddl": [
                "(at upstairs)"
            ],
            "status": "pending",
            "exit_condition": "the robot is on floor 2"
        },
        {
            "sub_task_name": "put everything in the basket",
            "pddl": [
                "(in red_doll basket)"
            ],
            "status": "pending",
            "exit_condition": "the robot's hands are empty"
        }
    ]
}

--- Subtask 1/3: 'pick up the red doll' ---
Observation: The robot is at (0, 0) on floor 1. On this floor, it sees: red toolbox at (2, 2), mug at (5, 6), book at (5, 4), notebook at (20, 21), green bottle at (-5, -5), blue folder at (15, 15), red doll at (1, 1). Its hands are empty.
--- Checking condition: 'the robot is holding a red doll' with observation: 'The robot is at (0, 0) on floor 1. On this floor, ...' ---
*** OpenAI API call took 1.50s ***
--- ConditionCheckerLMP raw response: 'False' ---
--- Condition is FALSE ---
*** OpenAI API call took 2.01s ***
########################################
## "loco_manip_executor" generated code
########################################
Instruction: objects = ['red toolbox', 'mug', 'book', 'notebook', 'green bottle', 'blue folder', 'red doll']
# pickup the red doll

say('Sure - locating the red doll')
doll_pos = detect_object('red doll')
if doll_pos is not None:
    say('Approaching the red doll')
    walking(doll_pos)
    say('Picking up the red doll')
    pickup('red doll')
else:
    say("I can't see the red doll.")


🤖 ROBOT SAYS: Sure - locating the red doll
🤖 ROBOT SAYS: Detecting object: red doll
  > Detected 'red doll' at position (1, 1)
🤖 ROBOT SAYS: Approaching the red doll
🤖 ROBOT SAYS: Walking to (1, 1)...
  > Robot is now at (1, 1)
🤖 ROBOT SAYS: Picking up the red doll
🤖 ROBOT SAYS: Attempting to pick up red doll with right hand.
  > Robot is now holding 'red doll' in right hand.
Observation: The robot is at (1, 1) on floor 1. On this floor, it sees: red toolbox at (2, 2), mug at (5, 6), book at (5, 4), notebook at (20, 21), green bottle at (-5, -5), blue folder at (15, 15). It is holding a red doll in its right hand.
--- Checking condition: 'the robot is holding a red doll' with observation: 'The robot is at (1, 1) on floor 1. On this floor, ...' ---
*** OpenAI API call took 1.66s ***
--- ConditionCheckerLMP raw response: 'True' ---
--- Condition is TRUE ---
--- Exit condition 'the robot is holding a red doll' met. ---

--- Subtask 2/3: 'go upstairs' ---
Observation: The robot is at (1, 1) on floor 1. On this floor, it sees: red toolbox at (2, 2), mug at (5, 6), book at (5, 4), notebook at (20, 21), green bottle at (-5, -5), blue folder at (15, 15). It is holding a red doll in its right hand.
--- Checking condition: 'the robot is on floor 2' with observation: 'The robot is at (1, 1) on floor 1. On this floor, ...' ---
*** OpenAI API call took 1.43s ***
--- ConditionCheckerLMP raw response: 'False' ---
--- Condition is FALSE ---
*** OpenAI API call took 1.66s ***
########################################
## "loco_manip_executor" generated code
########################################
Instruction: objects = ['red toolbox', 'mug', 'book', 'notebook', 'green bottle', 'blue folder']
# go upstairs

say('Ok - going upstairs')
go_upstairs()


🤖 ROBOT SAYS: Ok - going upstairs
🤖 ROBOT SAYS: Going upstairs by 1 floor(s).
  > Robot is now on floor 2 at (30, 5)
Observation: The robot is at (30, 5) on floor 2. On this floor, it sees: red book at (32, 5), basket at (35, 10). It is holding a red doll in its right hand.
--- Checking condition: 'the robot is on floor 2' with observation: 'The robot is at (30, 5) on floor 2. On this floor,...' ---
*** OpenAI API call took 1.95s ***
--- ConditionCheckerLMP raw response: 'True' ---
--- Condition is TRUE ---
--- Exit condition 'the robot is on floor 2' met. ---

--- Subtask 3/3: 'put everything in the basket' ---
Observation: The robot is at (30, 5) on floor 2. On this floor, it sees: red book at (32, 5), basket at (35, 10). It is holding a red doll in its right hand.
--- Checking condition: 'the robot's hands are empty' with observation: 'The robot is at (30, 5) on floor 2. On this floor,...' ---
*** OpenAI API call took 1.51s ***
--- ConditionCheckerLMP raw response: 'False' ---
--- Condition is FALSE ---
*** OpenAI API call took 1.87s ***
########################################
## "loco_manip_executor" generated code
########################################
Instruction: objects = ['red book', 'basket']
# put the red doll in the basket

say('Locating the basket')
basket_pos = detect_object('basket')
if basket_pos is not None:
    say('Approaching the basket')
    walking(basket_pos)
    say('Putting the red doll in the basket')
    drop('red doll')
else:
    say("I can't see the basket.")


🤖 ROBOT SAYS: Locating the basket
🤖 ROBOT SAYS: Detecting object: basket
  > Detected 'basket' at position (35, 10)
🤖 ROBOT SAYS: Approaching the basket
🤖 ROBOT SAYS: Walking to (35, 10)...
  > Robot is now at (35, 10)
🤖 ROBOT SAYS: Putting the red doll in the basket
🤖 ROBOT SAYS: Dropping red doll from my right hand.
  > Dropped 'red doll' at (35, 10).
Observation: The robot is at (35, 10) on floor 2. On this floor, it sees: red book at (32, 5), basket at (35, 10), red doll at (35, 10). Its hands are empty.
--- Checking condition: 'the robot's hands are empty' with observation: 'The robot is at (35, 10) on floor 2. On this floor...' ---
*** OpenAI API call took 1.48s ***
--- ConditionCheckerLMP raw response: 'True' ---
--- Condition is TRUE ---
--- Exit condition 'the robot's hands are empty' met. ---

--- Final Plan Status ---
{
    "task": "\u62ff\u8d77\u7ea2\u8272\u7684\u5a03\u5a03\uff0c\u8d70\u4e0a\u697c\u68af\uff0c\u7136\u540e\u628a\u5a03\u5a03\u653e\u8fdb\u7b50\u5b50\u91cc",
    "plan": [
        {
            "sub_task_name": "pick up the red doll",
            "pddl": [
                "(holding red_doll)"
            ],
            "status": "completed",
            "exit_condition": "the robot is holding a red doll"
        },
        {
            "sub_task_name": "go upstairs",
            "pddl": [
                "(at upstairs)"
            ],
            "status": "completed",
            "exit_condition": "the robot is on floor 2"
        },
        {
            "sub_task_name": "put everything in the basket",
            "pddl": [
                "(in red_doll basket)"
            ],
            "status": "completed",
            "exit_condition": "the robot's hands are empty"
        }
    ]
}

--- Final Environment State ---
Robot is at (35, 10) on floor 2
Robot hands: Left='None', Right='None'
Objects in world: ['red toolbox', 'mug', 'book', 'notebook', 'green bottle', 'red book', 'blue folder', 'basket', 'red doll']

--- MasterPlanner Live Mock Test Complete ---
```