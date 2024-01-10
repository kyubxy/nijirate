from enum import Enum
import re


class Difficulty(Enum):
    # not including easy for now
    Basic = 0
    Advanced = 1
    Expert = 1
    Master = 1
    Remaster = 1


class Score:
    def __init__(self, chartname: str, difficulty: Difficulty, achv: float):
        self.chartname = chartname
        self.achv = achv
        self.diff = difficulty

    def getDifficulty(self):
        return self.diff

    def getChartName(self):
        return self.chartname

    def getAchv(self):
        return self.achv

    def getGrade(self) -> str:
        grades = [
            # too lazy to implement the other grades at this stage
            (0, 96, "AAA"),
            (97, 98, "S"),
            (98, 99, "S+"),
            (99, 99.5, "SS"),
            (99.5, 100, "SS+"),
            (100, 100.5, "SSS"),
            (100.5, 101, "SSS+"),
        ]
        for (_min, _max, grade) in grades:
            achv = self.getAchv()
            if achv < 0 or achv > 101:
                return "error:malformed achievement"
            if _min <= achv < _max:
                return grade


class ScoreParser:
    def __init__(self, inputStr: str):
        self.input = inputStr

    def parse(self) -> [Score]:
        # seems to be coping fine without accounting for crlf
        tokens = re.split(r"\t|\n", self.input)[12:]  # ignore the first 12 tokens ie. the headers
        scores = []
        if len(tokens) % 12 != 0:
            raise Exception(f"parse: incorrect number of tokens {len(tokens)}, indivisible by 12")
        while len(tokens) > 0:
            name = tokens.pop(0)  # song
            tokens.pop(0)  # genre
            tokens.pop(0)  # version
            tokens.pop(0)  # chart
            d = tokens.pop(0)  # difficulty
            tokens.pop(0)  # level
            a = tokens.pop(0)  # achievement
            tokens.pop(0)  # rank
            tokens.pop(0)  # fcap
            tokens.pop(0)  # sync
            tokens.pop(1)  # dx *
            tokens.pop(0)  # dx %
            # parse and semantically analyse inputs
            dparse = {
                "BASIC": Difficulty.Basic,
                "ADVANCED": Difficulty.Advanced,
                "EXPERT": Difficulty.Expert,
                "MASTER": Difficulty.Master,
                "Re:MASTER": Difficulty.Remaster,  # fking hate this format
            }
            if d in dparse.keys():
                diff = dparse[d]
            else:
                raise Exception("parse: no such difficulty " + d)
            achv = float(a.partition("%")[0])
            scores.append(Score(name, diff, achv))
        return scores
