from random import shuffle


class Card(object):
    def __init__(self, value, suit, is_visible=True):
        points_lookup = {1: (1, 11), 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10, 11: 10, 12: 10, 13: 10}
        self.value = value
        self.suit = suit
        self.points = points_lookup[value]
        self.is_visible = is_visible

    def get_value(self):
        table = {1: 'Ace', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9', 10: '10',
                 11: 'Jack', 12: 'Queen', 13: 'King'}
        return table[self.value]

    def get_suit(self):
        table = {0: 'Clubs', 1: 'Diamonds', 2: 'Hearts', 3: 'Spades'}
        return table[self.suit]

    def show(self):
        if self.is_visible:
            print(self.get_value(), 'of', self.get_suit(), end='')
        else:
            print('<Face Down Card>', end='')


class Hand(object):
    def __init__(self, cards):
        self.cards = cards
        if len(self.cards) == 2:
            if self.cards[0].value == self.cards[1].value:
                self.is_pair = True
            else:
                self.is_pair = False
        else:
            self.is_pair = False
        self.is_complete = False
        self.a_double = False

    def score(self):
        score = [0, 0]  # initialize the score as a list to deal with aces easier
        for i in range(len(self.cards)):
            if self.cards[i].value == 1:  # if the card is an ace, need to account for 1 or 11 points
                temp = score.copy()
                score[0] = min(temp) + self.cards[i].points[0]
                score[1] = min(temp) + self.cards[i].points[1]
            else:
                score[0] += self.cards[i].points
                score[1] += self.cards[i].points
        if len(set(score)) == 1 or score[1] > 21:
            return score[0]
        else:
            return score

    def split(self):
        hand1 = Hand([self.cards[0]])
        hand2 = Hand([self.cards[1]])
        return [hand1, hand2]

    def show(self, dealer_starting_hand=False):
        for i in range(len(self.cards)):
            self.cards[i].show()
            if i != len(self.cards) - 1:
                print(', ', end='')
            else:
                if not dealer_starting_hand:
                    if type(self.score()) is list:
                        print(f'   <{self.score()[0]} or {self.score()[1]}>')
                    else:
                        print(f'   <{self.score()}>')
                else:
                    print('')


class Deck(object):
    def __init__(self):
        self.cards = []
        for value in range(1, 14):
            for suit in range(4):
                self.cards.append(Card(value, suit))

    def shuffle(self):
        shuffle(self.cards)

    def deal(self):
        return self.cards.pop()


class Player(object):
    num_of_players = 0

    def __init__(self, name, money, hands=[], initial_bet=0, current_bet=0):
        self.name = name
        self.hands = hands
        self.money = money
        self.current_bet = current_bet
        self.initial_bet = initial_bet
        Player.add_player()

    def bet(self, amount):
        self.current_bet = 0
        if amount > self.money:
            print(f'{self.name} needs to reload')
            self.reload()
        else:
            self.money -= amount
            self.current_bet += amount
            self.initial_bet = amount

    def reload(self, min_amount=0):
        input_not_valid = True
        while input_not_valid:
            amount = input(f'{self.name}, total money: {self.money}, money to add: ')
            try:
                amount = int(amount)
                input_not_valid = False
                if amount < min_amount:
                    print(f'You need to add a minimum of {min_amount}')
                    input_not_valid = True
            except:
                print('Need to enter a number')
        self.money += amount

    @classmethod
    def add_player(cls):
        cls.num_of_players += 1

    def display_current_hand(self, hand=0):
        print(f"{self.name}'s current hand: ", end='')
        self.hands[hand].show()

    def blackjack_check(self, dealer):
        if type(self.hands[0].score()) is list:
            if max(self.hands[0].score()) == 21:
                print(f"{self.name} wins! paying out...")
                dealer.payout(self, blackjack=True)
                return True
            else:
                return False
        else:
            return False

    def option(self, index=0):
        choice = ' '
        if self.hands[index].is_pair:
            print(f"{self.name}: [H]it, [S]tand, [D]ouble-down, or S[p]lit")
            while choice not in 'HhSsDdPp':
                choice = input('choice: ').lower()
        elif len(self.hands[index].cards) == 2:
            print(f"{self.name}: [H]it, [S]tand, or [D]ouble-down")
            while choice not in 'HhSsDd':
                choice = input('choice: ').lower()
        else:
            print(f"{self.name}: [H]it, or [S]tand")
            while choice not in 'HhSs':
                choice = input('choice: ').lower()
        return choice

    def hit(self, deck, index=0):
        self.hands[index].cards.append(deck.deal())
        if self.hands[index].cards[0].value == self.hands[index].cards[1].value:
            self.hands[index].is_pair = True
        if type(self.hands[index].score()) is list:
            return False
        else:
            if self.hands[index].score() > 21:
                return True
            else:
                return False

    def double_down(self, deck, index=0):
        if self.money < self.initial_bet:
            self.reload(abs(self.money-self.initial_bet))
        self.current_bet += self.initial_bet
        self.money -= self.initial_bet
        self.hands[index].a_double = True
        return self.hit(deck, index)

    def split(self, deck, index=0):
        if self.money < self.initial_bet:
            self.reload(abs(self.money-self.initial_bet))
        # self.current_bet += self.initial_bet
        self.money -= self.initial_bet
        split_hands = self.hands[index].split()
        self.hands.remove(self.hands[index])
        self.hands.insert(index, split_hands[0])
        self.hands.insert(index+1, split_hands[1])
        self.hit(deck, index)
        self.hit(deck, index+1)

    def stand(self, index=0):
        self.hands[index].is_complete = True


class Dealer(object):
    def __init__(self, hand=[]):
        self.hand = hand

    def deal_starting_hand(self, players, deck):
        temp_list = []
        dealer_hand = []
        for i in range(Player.num_of_players):
            temp_list.append([])
        while len(dealer_hand) < 2:
            for i in range(len(players)):
                temp_list[i].append(deck.deal())
            dealer_hand.append(deck.deal())
        dealer_hand[1].is_visible = False
        self.hand = Hand(dealer_hand)
        for i in range(len(players)):
            temp_hand = Hand(temp_list[i])
            players[i].hands = [temp_hand]

    def blackjack_check(self):
        print('Dealer is checking for blackjack...')
        if type(self.hand.score()) is list:
            if max(self.hand.score()) == 21:
                print('Dealer has blackjack. You LOSE!')
                self.hand.cards[1].is_visible = True
                self.display_hand()
                return True
            else:
                print('Dealer does not have blackjack')
                return False
        else:
            print('Dealer does not have blackjack')
            return False

    @staticmethod
    def remove_player_hand(player, index=0):
        player.hands.remove(player.hands[index])
        # player.current_bet -= player.initial_bet

    def display_hand(self, starting=False):
        if starting:
            print('')
        print("Dealer's hand: ", end='')
        self.hand.show(starting)
        if starting:
            print('')

    @staticmethod
    def payout(player, index=0, blackjack=False, push=False):
        if blackjack:
            player.money += player.current_bet * (5/2)
        elif player.hands[index].a_double:
            if push:
                player.money += player.initial_bet * 2
            else:
                player.money += player.initial_bet * 4
        else:
            if push:
                player.money += player.initial_bet
            else:
                player.money += player.initial_bet * 2

    def dealer_turn(self, deck):
        bust = False
        self.hand.cards[1].is_visible = True
        self.display_hand()
        while self.get_score() < 17:
            self.hand.cards.append(deck.deal())
            self.display_hand()
            if self.get_score() > 21:
                bust = True
                print("Dealer busted, paying out winning players")
                return bust
            else:
                bust = False
        print(f"Dealer stands at {self.get_score()}")
        return bust

    def get_score(self):
        if type(self.hand.score()) is list:
            return max(self.hand.score())
        else:
            return self.hand.score()
