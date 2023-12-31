#! /usr/bin/python3


import os
from typing import List
from day_17_pyroclastic_flow.jet import Jet


class Solution:
    def __init__(self, filename: str) -> None:
        self.rocks = [
            [30],  # 0b0011110
            [8, 28, 8],  # 0b0001000, 0b0011100, 0b0001000
            [28, 4, 4],  # 0b0011100, 0b0000100, 0b0000100
            [16, 16, 16, 16],  # 0b0010000 x4
            [24, 24],  # 0b0011000 x2
        ]

        # part 1
        self.jet = Jet(self.read_file(filename))
        self.seen = {}
        self.part1 = self.solution(2022)
        print(f"Part 1: {self.part1}")

        # part 2
        self.jet = Jet(self.read_file(filename))
        self.seen = {}
        self.part2 = self.solution(1000000000000)
        print(f"Part 2: {self.part2}")

    def read_file(self, filename: str) -> str:
        with open(
            f"{os.path.dirname(os.path.realpath(__file__))}/{filename}",
            "r",
            encoding="utf-8",
        ) as f:
            text = f.read()
        return text

    def prints_rock(self, rock: List[int]) -> None:
        """
        prints out the rock formation
        """
        for i in rock[::-1]:
            print(format(i, "07b"))

    def prints_chamber(self, chamber: List[int]) -> None:
        """
        prints out the chamber
        """
        for i in chamber[: -len(chamber): -1]:
            line = f'{format(i, "07b")}'
            line = line.replace("1", "#")
            line = line.replace("0", ".")
            line = "|" + line[1: len(line) - 1] + "|"
            print(line)
        print("+-------+")

    def can_rock_move_sideway_then_down(
        self, rock: List[int], jet_dir: str, chamber: List[int], level: int
    ) -> List:
        """
        checks to see if the rock can move sideway according to the jet direction
        if so, move there, if not, stay put
        then checks to see if rock can move down 1 unit
        if so, move there, if not, rock formation will be part of the chamber
        Output: (Settled, Rock, Chamber)
        Settled - True if the rock is at rest, else False
        Rock - rock location
        Chamber - the current chamber status
        """
        next_to_wall = False
        if jet_dir == ">":
            # check if next to wall
            for row in rock:
                if row & 1 != 0:
                    next_to_wall = True
                    break
            else:
                new_position = [i >> 1 for i in rock]
        else:  # if dir == '<'
            # check if next to wall
            for row in rock:
                if row & 64 != 0:
                    next_to_wall = True
                    break
            else:
                new_position = [i << 1 for i in rock]

        if not next_to_wall:
            # check to see if the sideway new position is valid
            for i in range(level, level + len(rock)):
                if new_position[i - level] & chamber[i] != 0:
                    break
            else:
                # valid, so get to new position
                rock = new_position

        # check to see if can move down 1 unit
        settled = False
        for i in range(level - 1, level - 1 + len(rock)):
            if rock[i - level + 1] & chamber[i] != 0:
                # can't move down anymore, be part of the chamber
                settled = True
                break

        if settled:
            for i in range(level, level + len(rock)):
                if rock[i - level] & chamber[i] == 1:
                    raise Exception
                chamber[i] = rock[i - level] | chamber[i]
            while chamber[-1] == 0:
                chamber.pop()

        return [settled, rock, chamber]

    def solution(self, num: int) -> int:
        """
        simulate the rock drops until a cycle is found, then do the math
        """
        result = 0
        chamber = [511]  # 0b1111111
        heights = []

        for i in range(num):
            rock = self.rocks[i % len(self.rocks)]
            chamber += [0 for _ in range(len(rock) + 3)]
            position = len(chamber) - len(rock)
            while True:
                jet_dir = self.jet.current
                settled, rock, chamber = self.can_rock_move_sideway_then_down(
                    rock, jet_dir, chamber, position
                )
                position -= 1
                if settled:
                    break

            heights.append(len(chamber))
            # index = (which rocks, which jet, chamber[-1] state)
            chamber_index = 0
            for a, b in enumerate(chamber[-8::]):
                chamber_index = chamber_index | b << (a * 8)
            index = (
                i % len(self.rocks),
                (self.jet.current_id - 1) % len(self.jet.order),
                chamber_index,
            )
            if index in self.seen:
                # cycle found
                break
            self.seen[index] = i
        else:
            # if there is not cycle, it will sim the whole thing and spit out the answer
            result = len(chamber) - 1

        base_index = self.seen[index]
        base_height = heights[base_index - 1] - 1
        cycle_height = heights[i] - heights[base_index]
        num_of_cycle = (num - 1 - base_index) // (i - base_index)
        remainder = (num - 1 - base_index) % (i - base_index)
        remainder_height = heights[remainder + base_index] - heights[base_index - 1]
        result = base_height + (cycle_height * num_of_cycle) + remainder_height

        return result


if __name__ == "__main__":
    Solution("input")
