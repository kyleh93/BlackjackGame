from gameObjects import *

auto_config = True
min_bet_size = 50
if auto_config:
    players = [Player('Kyle', 1000), Player('John', 1000), Player('Randy', 1000)]
else:
    name = input('Enter player name: ')
    while True:
        try:
            money = int(input(f'How much is {name} sitting down with (min bet size of {min_bet_size}): '))
            break
        except:
            print("Must enter a number!")
    players = [Player(name, money)]
    add_more = input('Would you like to add more players [Y/N]: ')
    while add_more in 'Yy' and Player.num_of_players <= 6:
        name = input('Enter player name: ')
        while True:
            try:
                money = int(input(f'How much is {name} sitting down with (min bet size of {min_bet_size}): '))
                break
            except:
                print("Must enter a number!")
        players.append(Player(name, money))
        if Player.num_of_players == 6:
            print('Table is full...starting the game')
            break
        add_more = input('Would you like to add more players [Y/N]: ')
still_playing = True

# Game begins
while True:
    while still_playing:
        # initialize the game
        dealer = Dealer()
        deck = Deck()
        deck.shuffle()
        continuing_players = players.copy()

        # display how much money each players has
        for i in range(len(players)):
            print(f'{players[i].name} has ${players[i].money}')
        print('')

        # initial round of betting before the hand
        for i in range(len(players)):
            input_not_valid = True
            while input_not_valid:
                if players[i].money == 0:
                    print(f'{players[i].name} has no money and needs to reload')
                    players[i].reload(min_amount=min_bet_size)
                bet_amount = input(f'{players[i].name}, enter betting amount: ')
                try:
                    bet_amount = int(bet_amount)
                    input_not_valid = False
                    if players[i].money < bet_amount:
                        print(f'{players[i].name} does not have that much money')
                        input_not_valid = True
                except:
                    print('Need to enter a number')
                    input_not_valid = False
            players[i].bet(bet_amount)

        dealer.deal_starting_hand(players, deck)

        # check the starting hands for black jack and pay winning players + display starting hands
        for i in range(len(players)):
            players[i].display_current_hand()
            if players[i].blackjack_check(dealer):
                continuing_players.remove(players[i])
        if len(continuing_players) == 0:
            break

        # show the dealers hand and check for blackjack if necessary
        dealer.display_hand(starting=True)
        if dealer.hand.cards[0].value >= 10 or dealer.hand.cards[0].value == 1:
            if dealer.blackjack_check():
                for i in range(len(players)):
                    players[i].current_bet = 0
                break

        # Players begin playing their hands
        for i in range(len(continuing_players)):
            while True:
                continuing_players[i].display_current_hand()
                option = continuing_players[i].option()
                if option == 'h':
                    bust = continuing_players[i].hit(deck)
                    if bust:
                        continuing_players[i].display_current_hand()
                        print("Bust! You lost the hand")
                        dealer.remove_player_hand(continuing_players[i])
                        break
                if option == 'd':
                    bust = continuing_players[i].double_down(deck)
                    continuing_players[i].display_current_hand()
                    if bust:
                        print("Why would you ever double down with a chance to bust?? You lost that hand")
                        dealer.remove_player_hand(continuing_players[i])
                    break
                if option == 's':
                    continuing_players[i].stand()
                    break
                if option == 'p':
                    current_index = 0
                    continuing_players[i].split(deck)
                    while True:
                        continuing_players[i].display_current_hand(current_index)
                        if continuing_players[i].hands[current_index].cards[0].value == 1:  # if splitting aces, you get one card and done
                            continuing_players[i].display_current_hand(current_index+1)
                            break
                        option = continuing_players[i].option(current_index)
                        if option == 'h':
                            bust = continuing_players[i].hit(deck, current_index)
                            if bust:
                                continuing_players[i].display_current_hand(current_index)
                                # continuing_players[i].current_bet -= continuing_players[i].initial_bet
                                print("Bust!  Lost that hand")
                                dealer.remove_player_hand(continuing_players[i], current_index)
                        if option == 'p':
                            continuing_players[i].split(deck, current_index)
                        if option == 's':
                            continuing_players[i].stand(current_index)
                            current_index += 1
                        if option == 'd':
                            bust = continuing_players[i].double_down(deck, current_index)
                            continuing_players[i].display_current_hand(current_index)
                            if bust:
                                print("Why would you ever double down with a chance to bust?? You lost that hand")
                                dealer.remove_player_hand(continuing_players[i], current_index)
                                # continuing_players[i].current_bet -= continuing_players[i].initial_bet
                                current_index -= 1
                            current_index += 1
                            if current_index == len(continuing_players[i].hands):
                                break
                        if current_index > len(continuing_players[i].hands)-1:
                            break
                    break

        # check if everyone busted.  if so, the dealer does not have to draw cards
        count = 0
        for i in range(len(continuing_players)):
            if len(continuing_players[i].hands) == 0:
                count += 1
        if count == len(continuing_players):
            print("all players busted.")
            break

        # the hands have been played.  Time for the Dealer to draw cards
        dealer_bust = dealer.dealer_turn(deck)

        # Compare the dealers hand score to the scores of the remaining player hands
        for i in range(len(continuing_players)):
            wins = 0
            push = 0
            for j in range(len(continuing_players[i].hands)):
                if type(continuing_players[i].hands[j].score()) is list:
                    current_player_score = max(continuing_players[i].hands[j].score())
                else:
                    current_player_score = continuing_players[i].hands[j].score()
                if dealer_bust or dealer.get_score() < current_player_score:
                    if dealer_bust:
                        wins += 1
                        dealer.payout(continuing_players[i], j)
                    else:
                        wins += 1
                        continuing_players[i].display_current_hand(j)
                        print(f"{continuing_players[i].name} wins that hand")
                        dealer.payout(continuing_players[i], j)
                elif dealer.get_score() > current_player_score:
                    continuing_players[i].display_current_hand(j)
                    print(f"{continuing_players[i].name} lost that hand")
                else:
                    continuing_players[i].display_current_hand(j)
                    dealer.payout(continuing_players[i], blackjack=False, push=True)
                    print("Push!")
            continuing_players[i].current_bet = 0
        break
    play_again = input('The hand is over. Play another hand? [Y/N]')
    if play_again in 'Yy':
        temp_index = 0
        if len(continuing_players) > 0:
            for i in range(len(continuing_players)):
                ind = players.index(continuing_players[i])
                players[ind] = continuing_players[i]
            del continuing_players
            print('\n\n')
    else:
        still_playing = False
        break

