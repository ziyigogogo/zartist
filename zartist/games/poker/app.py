from flask import Flask, render_template, jsonify, request
import random
from texasholdem.game.game import TexasHoldEm
from texasholdem.game.player_state import PlayerState
from texasholdem.game.action_type import ActionType
from texasholdem.game.hand_phase import HandPhase

app = Flask(__name__)
app.secret_key = 'your_secret_key'

#
game = None


def init_game():
    global game
    if game is None:
        game = TexasHoldEm(buyin=500, big_blind=5, small_blind=2, max_players=6)
        for i in range(2):
            game.players[i].chips = 500
            game.players[i].state = PlayerState.IN
        for i in range(2, game.max_players):
            if game.players[i].state == PlayerState.OUT:
                game.players[i].chips = 500
                game.players[i].state = PlayerState.IN
    return game


@app.route('/')
def index():
    init_game()
    return render_template('index.html')


@app.route('/start_hand', methods=['POST'])
def start_hand():
    try:
        global game
        game = init_game()

        # 
        if game.is_hand_running():
            # 
            game = TexasHoldEm(buyin=500, big_blind=5, small_blind=2, max_players=6)
            for i in range(game.max_players):
                if i < 2 or random.random() < 0.5:
                    game.players[i].chips = 500
                    game.players[i].state = PlayerState.IN
        else:
            # 
            for i in range(game.max_players):
                if game.players[i].chips > 0:  
                    game.players[i].state = PlayerState.IN
                else:
                    game.players[i].state = PlayerState.OUT

        # 
        active_players = sum(
            1 for i in range(game.max_players) if game.players[i].state not in (PlayerState.OUT, PlayerState.SKIP))

        if active_players < 2:
            # 
            for i in range(min(2, game.max_players)):
                game.players[i].chips = 500 if game.players[i].chips <= 0 else game.players[i].chips
                game.players[i].state = PlayerState.IN
            
            # 
            active_players = sum(
                1 for i in range(game.max_players) if game.players[i].state not in (PlayerState.OUT, PlayerState.SKIP))
            
            if active_players < 2:
                return jsonify({'error': 'Need at least 2 active players to start a hand'})

        game.start_hand()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/get_game_state')
def get_game_state():
    try:
        global game
        game = init_game()

        state = {
            'is_hand_running': game.is_hand_running(),
            'current_player': game.current_player,
            'phase': str(game.hand_phase) if game.is_hand_running() else 'Not Started',
            'board': [str(card) for card in game.board] if game.is_hand_running() else [],
            'dealer_position': game.btn_loc if game.btn_loc >= 0 else 0,
            'small_blind_position': game.sb_loc if game.sb_loc >= 0 else (game.btn_loc + 1) % game.max_players if game.btn_loc >= 0 else 1,
            'big_blind_position': game.bb_loc if game.bb_loc >= 0 else (game.btn_loc + 2) % game.max_players if game.btn_loc >= 0 else 2
        }

        # 
        pot_amount = 0
        if game.is_hand_running():
            # 
            for pot in game.pots:
                pot_amount += pot.get_amount()
            
            # 
            for i in range(game.max_players):
                if game.players[i].state != PlayerState.OUT:
                    pot_amount += game.player_bet_amount(i)
        state['pot'] = pot_amount

        # 
        if game.is_hand_running() and game.current_player is not None:
            # 
            moves = game.get_available_moves()

            # 
            available_moves = [str(move).replace('ActionType.', '') for move in moves.action_types]
            if ActionType.ALL_IN not in moves.action_types:
                available_moves.append('ALL_IN')

            state['available_moves'] = available_moves
            state['chips_to_call'] = game.chips_to_call(game.current_player)

            # 
            if hasattr(moves, 'raise_range'):
                state['raise_range'] = {'min': moves.raise_range.start, 'max': moves.raise_range.stop - 1}

            # 
            print(f"Current player: {game.current_player}")
            print(f"Player state: {game.players[game.current_player].state}")
            print(f"Available moves: {state['available_moves']}")
            print(f"Chips to call: {state['chips_to_call']}")
            print(f"Player chips: {game.players[game.current_player].chips}")
            print(f"Raise option: {game.raise_option}")
            if hasattr(moves, 'raise_range'):
                print(f"Raise range: {state['raise_range']}")

            # 
            print(f"Minimum raise: {moves.raise_range.start}")
            print(f"Maximum raise: {moves.raise_range.stop - 1}")

        # 
        state['players'] = []
        for i in range(game.max_players):
            player_info = {
                'id': i,
                'stack': game.players[i].chips,
                'state': str(game.players[i].state),
                'bet': game.player_bet_amount(i),
                'hand': []
            }

            # 
            if i == game.current_player and game.is_hand_running():
                player_info['hand'] = [str(card) for card in game.get_hand(i)]

            state['players'].append(player_info)

        return jsonify(state)
    except Exception as e:
        print(f"Error in get_game_state: {str(e)}")
        return jsonify({'error': str(e)})


@app.route('/take_action', methods=['POST'])
def take_action():
    try:
        global game
        game = init_game()

        if not game.is_hand_running():
            return jsonify({'error': 'No hand in progress'})

        data = request.get_json()
        action_type = data.get('action_type')
        amount = data.get('amount')

        # 
        try:
            action = ActionType[action_type]
        except (KeyError, TypeError):
            return jsonify({'error': f'Invalid action type: {action_type}'})

        # 
        moves = game.get_available_moves()
        if action not in moves.action_types and action != ActionType.ALL_IN:
            return jsonify({'error': f'Invalid action {action_type} for current player'})

        # 
        if action == ActionType.RAISE and amount is not None:
            if hasattr(moves, 'raise_range'):
                if amount < moves.raise_range.start or amount >= moves.raise_range.stop:
                    return jsonify({
                        'error':
                            f'Invalid raise amount. Must be between {moves.raise_range.start} and {moves.raise_range.stop - 1}'
                    })

        # 
        if action == ActionType.RAISE and amount is not None:
            game.take_action(action, amount)
        else:
            game.take_action(action)

        # 
        hand_over = not game.is_hand_running()
        winners = []
        players_cards = []
        pot_amount = 0

        if hand_over:
            # 
            for pot in game.pots:
                pot_amount += pot.get_amount()

            # 
            for i in range(game.max_players):
                if i < len(game.players) and game.players[i].state != PlayerState.OUT:
                    player_cards = [str(card) for card in game.get_hand(i)]
                    players_cards.append({'id': i, 'cards': player_cards, 'state': str(game.players[i].state)})

            # 
            if game.hand_history and game.hand_history.settle and game.hand_history.settle.pot_winners:
                # 
                for pot_id, (amount, best_rank, winners_list) in game.hand_history.settle.pot_winners.items():
                    # 
                    for player_id in winners_list:
                        # 
                        winner_exists = False
                        for winner in winners:
                            if winner['id'] == player_id:
                                winner_exists = True
                                break

                        # 
                        if not winner_exists:
                            winners.append({'id': player_id, 'stack': game.players[player_id].chips})

            # 
            if winners:
                win_amount_per_player = pot_amount / len(winners)
                # 
                for winner in winners:
                    winner['won'] = win_amount_per_player

        return jsonify({
            'success': True,
            'hand_over': hand_over,
            'winners': winners if hand_over else None,
            'players_cards': players_cards if hand_over else None,
            'pot': pot_amount if hand_over else 0,
            'board': [str(card) for card in game.board] if hand_over else []
        })
    except Exception as e:
        print(f"Error in take_action: {str(e)}")
        return jsonify({'error': str(e)})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
