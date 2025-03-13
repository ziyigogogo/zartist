from flask import Flask, render_template, jsonify, request
import random
import logging
from texasholdem.game.game import TexasHoldEm
from texasholdem.game.player_state import PlayerState
from texasholdem.game.action_type import ActionType
from texasholdem.game.hand_phase import HandPhase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'your_secret_key'

#
game = None


def init_game(n_players):
    global game
    if not game:
        logger.info(f"Initializing game with player_count: {n_players}")
        game = TexasHoldEm(buyin=500, big_blind=5, small_blind=2, max_players=n_players)
    logger.info(f"Found existing game...return directly!")
    return game


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/init_game', methods=['POST'])
def initialize_game():
    try:
        global game
        data = request.get_json()
        player_count = data.get('player_count', 2)  # Default to 2 if not specified
        logger.info(f"Received request to initialize game with player_count: {player_count}")
        player_count = max(2, min(player_count, 10))
        game = init_game(n_players=player_count)

        return jsonify({'success': True, 'player_count': player_count})
    except Exception as e:
        logger.error(f"Error initializing game: {str(e)}")
        return jsonify({'error': str(e)})


@app.route('/start_hand', methods=['POST'])
def start_hand():
    try:
        global game
        logger.info(f"Starting hand with player_count: {game.max_players}")
        game.start_hand()
        logger.info("Hand started successfully")
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error in start_hand: {str(e)}")
        return jsonify({'error': str(e)})


@app.route('/get_game_state')
def get_game_state():
    try:
        global game

        # Base state with default values for non-running hand
        state = {
            # 游戏基本信息
            'is_hand_running': game.is_hand_running(),
            'is_game_running': game.is_game_running(),
            'current_player': game.current_player,
            'phase': 'Not Started',
            'board': [],
            'dealer_position': game.btn_loc,
            'small_blind_position': game.sb_loc,
            'big_blind_position': game.bb_loc,
            # 场上数值
            'pot': 0,
            'big_blind': game.big_blind,
            'small_blind': game.small_blind,
            # raise相关数值
            'last_raise': game.last_raise,
            'min_raise': game.min_raise(),
            "current_bet": game.player_bet_amount(game.current_player),
            # 初始化空列表
            'available_moves': [],
            'players': []
        }

        for i in range(game.max_players):
            player_info = {
                'id': i,
                'stack': game.players[i].chips,
                'state': str(game.players[i].state),
                'bet': game.player_bet_amount(i),
                'chips_at_stake': 0,
                'is_active': i in list(game.active_iter()),
                'in_pot': i in list(game.in_pot_iter()),
                'hand': []
            }
            state['players'].append(player_info)

        # Update values for running hand
        if game.is_hand_running():
            state.update({
                'phase': str(game.hand_phase),
                'board': [str(card) for card in game.board],
                'pot': get_total_pot(),
                'chips_to_call': game.chips_to_call(game.current_player)
            })

            # Update player information for running hand
            for i in range(game.max_players):
                state['players'][i]['chips_at_stake'] = game.chips_at_stake(i)
                if i == game.current_player:
                    state['players'][i]['hand'] = [str(card) for card in game.get_hand(i)]

            # Get available moves
            moves = game.get_available_moves()
            state['available_moves'] = [str(move).replace('ActionType.', '') for move in moves.action_types]

            if hasattr(moves, 'raise_range'):
                min_raise = moves.raise_range.start
                max_raise = moves.raise_range.stop - 1
                state['raise_range'] = {'min': min_raise, 'max': max_raise}

        return jsonify(state)
    except Exception as e:
        logger.error(f"Error in get_game_state: {str(e)}")
        return jsonify({'error': str(e)})


def get_total_pot():
    """Helper function to calculate the total pot amount from all pots"""
    return sum(pot.get_amount() for pot in game.pots)


@app.route('/take_action', methods=['POST'])
def take_action():
    try:
        global game

        if not game.is_hand_running():
            return jsonify({'error': 'No hand in progress'})

        data = request.get_json()
        print("前端传入的数据: ", data)
        action_type = data.get('action_type')
        amount = data.get('amount')
        try:
            action = ActionType[action_type]
        except (KeyError, TypeError):
            return jsonify({'error': f'Invalid action type: {action_type}'})

        # Execute the action
        if action == ActionType.RAISE and amount:
            try:
                # 确保加注金额不为空且是有效数字
                amount = int(amount)
                # 执行加注动作
                game.take_action(action, total=amount)
                print("加注后last raise: ", game.last_raise)
            except Exception as e:
                logger.error(f"Error processing raise: {type(e)}{str(e)}")
                return jsonify({'error': f'Error processing raise: {str(e)}'})
        else:
            game.take_action(action)

        # Check if hand is over
        hand_over = not game.is_hand_running()
        winners = []
        players_cards = []

        if hand_over:
            pot_amount = get_total_pot()

            # Get cards of all players still in the game using in_pot_iter
            for player_id in game.in_pot_iter():
                player_cards = [str(card) for card in game.get_hand(player_id)]
                players_cards.append({
                    'id': player_id,
                    'cards': player_cards,
                    'state': str(game.players[player_id].state),
                    'chips_at_stake': game.chips_at_stake(player_id)
                })

            # Process winners from hand history
            if game.hand_history and game.hand_history.settle and game.hand_history.settle.pot_winners:
                for pot_id, (amount, best_rank, winners_list) in game.hand_history.settle.pot_winners.items():
                    for player_id in winners_list:
                        # Add winner only if not already in the list
                        if not any(winner['id'] == player_id for winner in winners):
                            winners.append({
                                'id': player_id,
                                'stack': game.players[player_id].chips,
                                'final_state': str(game.players[player_id].state),
                                'pot_id': pot_id,
                                'hand_rank': str(best_rank)
                            })

                # Calculate winnings for each pot
                if winners:
                    win_amount_per_player = pot_amount / len(winners)
                    for winner in winners:
                        winner['won'] = win_amount_per_player

        return jsonify({
            'success': True,
            'hand_over': hand_over,
            'winners': winners if hand_over else None,
            'players_cards': players_cards if hand_over else None,
            'pot': get_total_pot() if hand_over else 0,
            'board': [str(card) for card in game.board] if hand_over else [],
            'final_phase': str(game.hand_phase) if hand_over else None
        })
    except Exception as e:
        print(f"Error in take_action: {str(e)}")
        return jsonify({'error': str(e)})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
