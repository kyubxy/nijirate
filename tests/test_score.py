import os
from unittest import TestCase
from nijirate.score import ScoreParser, Score, Difficulty

class TestScoreParser(TestCase):
    def testSample(self):
        with open("samplescores", "r", encoding="utf-8", errors="ignore") as f:
            scores = f.read()

        sp = ScoreParser(scores)
        s = sp.parse()
        expScore = Score("だから僕は音楽を辞めた", Difficulty.Basic, 100.8333)
        testScore = s[0]
        self.assertEqual(testScore.getChartName(), expScore.getChartName())
        self.assertEqual(testScore.getDifficulty(), expScore.getDifficulty())
        self.assertEqual(testScore.getAchv(), expScore.getAchv())

