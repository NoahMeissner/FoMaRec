# 26.06.2025 @Noah Meissner

"""
This file tests if the llms are working correctly
"""

import os
from foodrec.data.kochbar import KochbarLoader


def test_kochbar():
    obj = KochbarLoader()
    data = obj.load_dataset()
    if data is not None:
        print("Correct Loaded")
        return True
    else:
        print("Wrong Loaded")

        return False