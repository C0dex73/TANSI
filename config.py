"""This file contains the architecture of the current network"""


configList = [
    ("A", 2, "B"),
    ("C", 1, "A"),
    ("B", 2, "C"),
    ("B", 3, "E"),
    ("E", 3, "C"),
    ("E", 1, "F"),
    ("F", 5, "C"),
    ("C", 4, "D"),
    ("B", 1, "D"),
    ("F", 6, "D"),
    ("E", 3, "D"),
    ("F", 2, "G"),
    ("D", 5, "G")
]
"""current network architecture represented as a list of tuples (thoses are links)"""