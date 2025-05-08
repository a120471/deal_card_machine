import random


def Fisher_Yates_Shuffle(deck):
    """Fisher-Yates shuffle algorithm."""
    for i in range(len(deck) - 1, 0, -1):
        j = random.randint(0, i)
        deck[i], deck[j] = deck[j], deck[i]


def dou_di_zhu_shuffle(
    card_num=54, player_num=3, bottom_card_num=3
):
    """Shuffle the deck for Dou Di Zhu.

    Returns:
      indices: list of int, which indicates the player id each card belongs to.
    """
    deck = list(range(1, card_num + 1))
    Fisher_Yates_Shuffle(deck)
    # print(deck)
    return [
        player_num if i > card_num - bottom_card_num else i % player_num for i in deck
    ]


def n_player_shuffle(card_num=54, player_num=4):
    """Shuffle the deck for n players.

    Returns:
      indices: list of int, which indicates the player id each card belongs to.
    """
    deck = list(range(1, card_num + 1))
    Fisher_Yates_Shuffle(deck)
    # print(deck)
    return [i % player_num for i in deck]
