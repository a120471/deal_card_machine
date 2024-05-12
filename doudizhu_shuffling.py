import random

k_CARD_NUM = 54
k_NUM_OF_PLAYERS = 3
k_BOTTOM_CARD_NUM = 3


def Fisher_Yates_Shuffle(deck):
    for i in range(len(deck) - 1, 0, -1):
        j = random.randint(0, i)
        deck[i], deck[j] = deck[j], deck[i]


def dou_di_zhu_shuffle():
    """Use Fisher-Yates shuffle algorithm to shuffle the deck for Dou Di Zhu.

    Returns:
      indices: list of int, which indicates the player id each card belongs to.
    """
    deck = list(range(1, k_CARD_NUM + 1))
    Fisher_Yates_Shuffle(deck)
    # print(deck)
    return [
        k_NUM_OF_PLAYERS if i > k_CARD_NUM - k_BOTTOM_CARD_NUM else i % k_NUM_OF_PLAYERS
        for i in deck
    ]
