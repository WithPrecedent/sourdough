"""
.. module:: test Worker
:synopsis: tests Worker and related classes
:author: Corey Rayburn Yung
:copyright: 2020
:license: Apache-2.0
"""

import sourdough


class NewInstructions(sourdough.base.Instructions):
    pass

class NewWorker(sourdough.manager.Worker):
    pass

def test_step():

    return


if __name__ == '__main__':
    test_step()