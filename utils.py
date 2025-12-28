import os
import numpy as np

def load_prompt(file_path):
    """
    Reads a file and returns its stripped content.
    """
    with open(file_path, 'r') as f:
        contents = f.read().strip()
    return contents

class IterableDynamicObservation:
    """acts like a list of DynamicObservation objects, initialized with a function that evaluates to a list"""
    def __init__(self, func):
        assert callable(func), 'func must be callable'
        self.func = func
        self._validate_func_output()

    def _validate_func_output(self):
        evaluated = self.func()
        assert isinstance(evaluated, list), 'func must evaluate to a list'

    def __getitem__(self, index):
        def helper():
            evaluated = self.func()
            item = evaluated[index]
            return item
        return helper

    def __len__(self):
        return len(self.func())

    def __iter__(self):
        for i in range(len(self)):
            yield self.__getitem__(i)

    def __call__(self):
        static_list = self.func()
        return static_list

class DynamicObservation:
    """acts like dict observation but initialized with a function such that it uses the latest info"""
    def __init__(self, func):
        try:
            assert callable(func) and not isinstance(func, dict), 'func must be callable or cannot be a dict'
        except AssertionError as e:
            print(e)
            import pdb; pdb.set_trace()
        self.func = func
    
    def __get__(self, key):
        evaluated = self.func()
        if isinstance(evaluated[key], np.ndarray):
            return evaluated[key].copy()
        return evaluated[key]
    
    def __getattr__(self, key):
        return self.__get__(key)
    
    def __getitem__(self, key):
        return self.__get__(key)

    def __call__(self):
        static_obs = self.func()
        if not isinstance(static_obs, Observation):
            static_obs = Observation(static_obs)
        return static_obs

class Observation(dict):
    def __init__(self, obs_dict):
        super().__init__(obs_dict)
        self.obs_dict = obs_dict
    
    def __getattr__(self, key):
        return self.obs_dict[key]
    
    def __getitem__(self, key):
        return self.obs_dict[key]

    def __getstate__(self):
        return self.obs_dict
    
    def __setstate__(self, state):
        self.obs_dict = state
