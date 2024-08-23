from run import run
from mario_environment import MarioEnvironment
from mario_expert import * #allegedly bad practice go get fucked

import argparse
import logging
import os
from pathlib import Path

upi = "hmah689"
headless = False

run(upi, headless=headless)

# ##copied from run.py
# if upi == "your_upi":
#     raise ValueError("Please set your UPI in the run.py file")

# results_path = f"{Path(__file__).parent.parent}/results/{upi}"
# logging.info(f"Saving data into: {results_path}")

# if not os.path.exists(results_path):
#     os.makedirs(results_path)

# expert = MarioExpert(results_path=results_path, headless=headless)

# #make it clean
# expert.environment.reset()
# vision = expert.environment.game_area()

# print(vision)