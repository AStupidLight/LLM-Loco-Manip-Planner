
import numpy as np
from typing import Dict, Any, Tuple, Optional

class MockEnvMobile:
    """
    A mock environment for a mobile manipulation robot.
    Simulates the robot's location, what it's holding, and the location of objects.
    """
    def __init__(self):
        self.robot_location: Tuple[int, int] = (0, 0)
        self.robot_floor: int = 1
        
        # All known locations in the world
        self.locations: Dict[str, Any] = {
            'charging station': {'pos': (0, 5), 'floor': 1},
            'lab door': {'pos': (10, 0), 'floor': 1},
            'reception desk': {'pos': (20, 20), 'floor': 1},
            'stairs entrance': {'pos': (30, 0), 'floor': 1},
            'table': {'pos': (5, 5), 'floor': 1},
            'upstairs_landing': {'pos': (30, 5), 'floor': 2},
        }
        
        # All objects in the world
        self.objects: Dict[str, Any] = {
            'red toolbox': {'pos': (2, 2), 'floor': 1},
            'mug': {'pos': (5, 6), 'floor': 1},
            'book': {'pos': (5, 4), 'floor': 1},
            'notebook': {'pos': (20, 21), 'floor': 1},
            'green bottle': {'pos': (-5, -5), 'floor': 1},
            'red book': {'pos': (32, 5), 'floor': 2},
            'blue folder': {'pos': (15, 15), 'floor': 1},
            'red doll': {'pos': (1, 1), 'floor': 1},
            'basket': {'pos': (35, 10), 'floor': 2}
        }
        
        # What the robot is holding
        self.hands: Dict[str, Optional[str]] = {
            'left': None,
            'right': None
        }

        print("--- Mobile Mock Environment Initialized ---")
        print(f"Robot starting at {self.robot_location} on floor {self.robot_floor}")

    def get_observation_description(self) -> str:
        """Returns a natural language description of the current scene."""
        desc = f"The robot is at {self.robot_location} on floor {self.robot_floor}. "
        
        scene_objects = [f"{name} at {obj['pos']}" for name, obj in self.objects.items() if obj['floor'] == self.robot_floor]
        if scene_objects:
            desc += "On this floor, it sees: " + ", ".join(scene_objects) + ". "
        else:
            desc += "It sees no objects on this floor. "

        if self.hands['left'] and self.hands['right']:
            desc += f"It is holding a {self.hands['left']} in its left hand and a {self.hands['right']} in its right hand."
        elif self.hands['left']:
            desc += f"It is holding a {self.hands['left']} in its left hand."
        elif self.hands['right']:
        	desc += f"It is holding a {self.hands['right']} in its right hand."
        else:
            desc += "Its hands are empty."
            
        return desc

    def get_observation_objects(self) -> list[str]:
        """Returns a list of object names on the current floor."""
        return [name for name, obj in self.objects.items() if obj['floor'] == self.robot_floor]


    def _get_object_or_loc(self, name: str) -> Optional[Dict]:
        if name in self.objects:
            return self.objects[name]
        if name in self.locations:
            return self.locations[name]
        # Allow for compound names
        for k in self.objects:
            if name in k:
                return self.objects[k]
        for k in self.locations:
            if name in k:
                return self.locations[k]
        return None

    # --- Mock API Implementations ---

    def say(self, message: str):
        """Simulates the robot speaking."""
        print(f"🤖 ROBOT SAYS: {message}")

    def detect_object(self, object_name: str) -> Tuple[int, int]:
        """Simulates detecting an object and returning its position."""
        self.say(f"Detecting object: {object_name}")
        info = self._get_object_or_loc(object_name)
        if info and info['floor'] == self.robot_floor:
            print(f"  > Detected '{object_name}' at position {info['pos']}")
            return info['pos']
        print(f"  > Could not detect '{object_name}' on the current floor.")
        return (0, 0) # Default position if not found

    def detect_loc(self, location_name: str) -> Tuple[int, int]:
        """Simulates detecting a location and returning its position."""
        self.say(f"Detecting location: {location_name}")
        info = self._get_object_or_loc(location_name)
        if info:
            print(f"  > Detected '{location_name}' at position {info['pos']}")
            return info['pos']
        print(f"  > Could not detect '{location_name}'.")
        return (0, 0)

    def walking(self, position: Tuple[int, int]):
        """Simulates walking to a position."""
        self.say(f"Walking to {position}...")
        self.robot_location = position
        print(f"  > Robot is now at {self.robot_location}")

    def running(self, position: Tuple[int, int]):
        """Simulates running to a position."""
        self.say(f"Running to {position}...")
        self.robot_location = position
        print(f"  > Robot is now at {self.robot_location}")

    def go_upstairs(self, stairs_pos: Optional[Tuple[int, int]] = None, floors: int = 1):
        """Simulates going upstairs."""
        self.say(f"Going upstairs by {floors} floor(s).")
        self.robot_floor += floors
        self.robot_location = self.locations['upstairs_landing']['pos']
        print(f"  > Robot is now on floor {self.robot_floor} at {self.robot_location}")

    def pickup(self, object_name: str, hand: str = 'right'):
        """Simulates picking up an object."""
        self.say(f"Attempting to pick up {object_name} with {hand} hand.")
        info = self._get_object_or_loc(object_name)
        if not info:
            self.say(f"I can't find {object_name} to pick it up.")
            return

        # Check if robot is close to the object
        dist = np.linalg.norm(np.array(self.robot_location) - np.array(info['pos']))
        if dist > 3.0: # Assume a 3-unit radius for pickup
            self.say(f"I'm too far from {object_name} to pick it up. I should walk closer first.")
            return

        if self.hands[hand] is not None:
            self.say(f"My {hand} hand is already holding {self.hands[hand]}.")
            return
            
        if object_name in self.objects:
            self.hands[hand] = object_name
            del self.objects[object_name]
            print(f"  > Robot is now holding '{object_name}' in {hand} hand.")
        else:
            self.say(f"Object '{object_name}' does not exist in the environment to be picked up.")

    def drop(self, item: Optional[str] = None, hand: str = None):
        """Simulates dropping an object."""
        if item is None and hand is None:
            # Drop everything
            self.say("Dropping all items.")
            for h, obj in self.hands.items():
                if obj is not None:
                    self.objects[obj] = {'pos': self.robot_location, 'floor': self.robot_floor}
                    self.hands[h] = None
                    print(f"  > Dropped '{obj}' at {self.robot_location}.")
            return

        if hand:
            obj_in_hand = self.hands.get(hand)
            if obj_in_hand:
                self.say(f"Dropping {obj_in_hand} from my {hand} hand.")
                self.objects[obj_in_hand] = {'pos': self.robot_location, 'floor': self.robot_floor}
                self.hands[hand] = None
                print(f"  > Dropped '{obj_in_hand}' at {self.robot_location}.")
            else:
                self.say(f"My {hand} hand is empty.")
        elif item:
            for h, obj in self.hands.items():
                if obj == item:
                    self.say(f"Dropping {item} from my {h} hand.")
                    self.objects[item] = {'pos': self.robot_location, 'floor': self.robot_floor}
                    self.hands[h] = None
                    print(f"  > Dropped '{item}' at {self.robot_location}.")
                    return
            self.say(f"I am not holding {item}.")

    def parse_position(self, description: str) -> Tuple[int, int]:
        """Simulates parsing a descriptive position."""
        self.say(f"Parsing position: '{description}'")
        if 'in front of the table' in description:
            pos = self.locations['table']['pos']
            new_pos = (pos[0], pos[1] - 2) # Mock position in front
            print(f"  > Interpreted position as {new_pos}")
            return new_pos
        return self.robot_location
