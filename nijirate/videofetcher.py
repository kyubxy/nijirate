from typing import List

from score import Score


class VideoFetcher:
    def __init__(self, scores: List[Score]):
        self.scores = scores

    def kickoff(self, threadcount=4):
        pass