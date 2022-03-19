import random
import itertools
from abc import ABC, abstractmethod

suits = ["Bastoni", "Denari", "Coppe", "Spade"]
values = {1: 11, 3: 10, 13: 4, 12: 3, 11: 2, 7: 0, 6: 0, 5: 0, 4: 0, 2: 0}


class Card:
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value

    def __repr__(self):
        return self.suit + "_" + str(self.value)


class Deck:
    def __init__(self):
        self.deck = [Card(c[0], c[1]) for c in list(itertools.product(suits, values.keys()))]
        random.shuffle(self.deck)

    def get_cards(self, num_cards: int):
        return [self.deck.pop(0) for _ in range(num_cards)]


class Player(ABC):
    def __init__(self):
        self.cards_in_hand = []
        self.passed_cards = []
        self.cards_won = []
        self.num_points = 0
        self.briscola = None

    @abstractmethod
    def make_move(self, cards_on_table):
        pass

    def reset(self):
        self.cards_in_hand = []
        self.passed_cards = []
        self.cards_won = []
        self.num_points = 0


class RandomPlayer(Player):

    def make_move(self, cards_on_table):
        random_card = random.randint(0, len(self.cards_in_hand) - 1)
        return self.cards_in_hand.pop(random_card)


class GreedyPlayer(Player):

    def __init__(self):
        super().__init__()
        self.cards_in_game = Deck().deck

    def make_move(self, cards_on_table):
        self.cards_in_game = [card for card in self.cards_in_game if
                              card not in cards_on_table and card not in self.cards_in_hand]

        hand_str = [self.num_stronger_cards(card, cards_on_table, self.cards_in_game) for card in self.cards_in_hand]

        return self.cards_in_hand.pop(hand_str.index(min(hand_str)))

    def num_stronger_cards(self, card, cards_on_table, cards_in_game) -> int:
        if not cards_on_table:
            current_briscola = self.briscola.suit
        else:
            current_briscola = cards_on_table[0].suit if self.briscola.suit not in \
                                                         {card.suit for card in cards_on_table} else self.briscola.suit

        stronger_card = 0
        strength_list = list(values.keys())
        for c in cards_in_game:
            if c.suit == current_briscola and strength_list.index(c.value) < strength_list.index(card.value):
                stronger_card += 1
        return stronger_card


class BriscolaGame:
    def __init__(self, player1: Player, player2: Player):
        self.deck = Deck()
        self.player1 = player1
        self.player2 = player2

        self.play_first = self.player1
        self.play_second = self.player2
        self.first_player = self.player1

        self.briscola = None

    def take_cards_from_deck(self, num: int):
        for _ in range(2):
            self.play_first.cards_in_hand.extend(self.deck.get_cards(num))
            if not self.briscola:
                self.briscola = self.deck.get_cards(1)[0]

                self.player1.briscola = self.briscola
                self.player2.briscola = self.briscola

                self.deck.deck.append(self.briscola)
            self.play_second.cards_in_hand.extend(self.deck.get_cards(num))

    def does_first_player_take(self, cards_on_table):
        current_briscola = cards_on_table[0].suit if self.briscola.suit not in [card.suit for card in
                                                                                cards_on_table] else self.briscola.suit

        str_index = 0
        strength_list = list(values.keys())
        for ind, card in enumerate(cards_on_table):
            if card.suit == current_briscola and strength_list.index(card.value) < strength_list.index(
                    cards_on_table[str_index].value):
                str_index = ind

        return str_index == 0 or str_index == 2

    def play(self):

        self.player1.reset()
        self.player2.reset()
        self.take_cards_from_deck(2)

        while True:
            if not self.player1.cards_in_hand:
                if self.player1.num_points == self.player2.num_points:
                    return None

                winner = self.player1 if self.player1.num_points > self.player2.num_points else self.player2
                # self.play_first = winner
                # self.play_second = self.player1 if winner is self.player2 else self.player2
                return winner

            current_round = []

            for i in range(4):
                if i == 0 or i == 2:
                    card = self.play_first.make_move(current_round)
                else:
                    card = self.play_second.make_move(current_round)
                current_round.append(card)

            round_winner = self.play_first if self.does_first_player_take(current_round) else self.play_second
            round_winner.cards_won.extend(current_round)
            for card in current_round:
                round_winner.num_points += values[card.value]

            if round_winner == self.play_second:
                self.play_first, self.play_second = self.play_second, self.play_first

            if self.deck.deck:
                self.take_cards_from_deck(1)


if __name__ == '__main__':

    p1 = RandomPlayer()
    p2 = GreedyPlayer()
    num_games = 100000
    p1_wins, p2_wins, draws = 0, 0, 0
    for _ in range(num_games):
        game = BriscolaGame(p1, p2)
        winner = game.play()
        if winner is None:
            draws += 1
        elif winner is p1:
            p1_wins += 1
        else:
            p2_wins += 1

    print("P1 won: " + str(p1_wins / num_games * 100))
    print("P2 won: " + str(p2_wins / num_games * 100))
    print("Draw: " + str(draws / num_games * 100))
