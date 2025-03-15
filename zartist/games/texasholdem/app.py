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
            "current_bet": game.player_bet_amount(game.current_player) if game.current_player is not None else 0,
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
            # Calculate pot values
            pot_data = calculate_effective_pot()
            real_pot_size = pot_data['real_pot_size']
            chips_to_call = pot_data['chips_to_call']
            effective_pot = pot_data['effective_pot']

            # Format board cards with proper symbols and colors
            formatted_board = [format_card(str(card)) for card in game.board]

            state.update({
                'phase': str(game.hand_phase),
                'board': formatted_board,
                'pot': real_pot_size,  # Use calculated real pot size
                'chips_to_call': chips_to_call
            })

            # Update player information for running hand
            for i in range(game.max_players):
                state['players'][i]['chips_at_stake'] = game.chips_at_stake(i)
                if i == game.current_player:
                    # Format player hand cards with proper symbols and colors
                    state['players'][i]['hand'] = [format_card(str(card)) for card in game.get_hand(i)]

            # Get available moves
            moves = game.get_available_moves()
            state['available_moves'] = [str(move).replace('ActionType.', '') for move in moves.action_types]

            if hasattr(moves, 'raise_range'):
                min_raise = moves.raise_range.start
                max_raise = moves.raise_range.stop - 1
                state['raise_range'] = {'min': min_raise, 'max': max_raise}

                # Calculate pot-based raise values if RAISE is available
                if 'RAISE' in state['available_moves'] and game.current_player is not None:
                    # Calculate pot-based raise values
                    raw_pot_third_value = effective_pot // 3
                    raw_pot_half_value = effective_pot // 2
                    raw_pot_full_value = effective_pot
                    raw_pot_2x_value = effective_pot * 2

                    # Apply minimum raise restriction
                    pot_third_raise = max(min_raise, chips_to_call + raw_pot_third_value)
                    pot_half_raise = max(min_raise, chips_to_call + raw_pot_half_value)
                    pot_full_raise = max(min_raise, chips_to_call + raw_pot_full_value)
                    pot_2x_raise = max(min_raise, chips_to_call + raw_pot_2x_value)

                    # Calculate increments (amount above call)
                    pot_third_increment = pot_third_raise - chips_to_call
                    pot_half_increment = pot_half_raise - chips_to_call
                    pot_full_increment = pot_full_raise - chips_to_call
                    pot_2x_increment = pot_2x_raise - chips_to_call

                    # Add pot-based raise calculations to state
                    state['pot_raise_values'] = {
                        'pot_third': {
                            'total': pot_third_raise,
                            'increment': pot_third_increment,
                            'raw_value': raw_pot_third_value,
                            'valid': raw_pot_third_value >= min_raise - chips_to_call
                        },
                        'pot_half': {
                            'total': pot_half_raise,
                            'increment': pot_half_increment,
                            'raw_value': raw_pot_half_value,
                            'valid': raw_pot_half_value >= min_raise - chips_to_call
                        },
                        'pot_full': {
                            'total': pot_full_raise,
                            'increment': pot_full_increment,
                            'raw_value': raw_pot_full_value,
                            'valid': raw_pot_full_value >= min_raise - chips_to_call
                        },
                        'pot_2x': {
                            'total': pot_2x_raise,
                            'increment': pot_2x_increment,
                            'raw_value': raw_pot_2x_value,
                            'valid': raw_pot_2x_value >= min_raise - chips_to_call
                        }
                    }

        return jsonify(state)
    except Exception as e:
        logger.error(f"Error in get_game_state: {str(e)}")
        return jsonify({'error': str(e)})


def get_total_pot():
    """Helper function to calculate the total pot amount from all pots"""
    return sum(pot.get_amount() for pot in game.pots)


def format_card(card_str):
    """Format card string to display proper suit symbols and determine color"""
    if not card_str or len(card_str) < 2:
        return {'text': card_str, 'color': 'black'}

    rank = card_str[0]
    suit = card_str[1]

    suit_symbol = suit
    color = 'black'

    if suit == 's':
        suit_symbol = '\u2660'  # ♠
    elif suit == 'h':
        suit_symbol = '\u2665'  # ♥
        color = 'red'
    elif suit == 'd':
        suit_symbol = '\u2666'  # ♦
        color = 'red'
    elif suit == 'c':
        suit_symbol = '\u2663'  # ♣

    return {'text': rank + suit_symbol, 'color': color}


def calculate_effective_pot():
    """Calculate real pot size and effective pot for betting calculations"""
    # Calculate total bets from all players
    total_bets = 0
    for i in range(game.max_players):
        if game.players[i].state != PlayerState.OUT:
            total_bets += game.player_bet_amount(i)

    # Real pot size = current pot + all player bets
    real_pot_size = get_total_pot() + total_bets

    # Calculate chips to call for current player
    chips_to_call = 0
    if game.current_player is not None and game.is_hand_running():
        chips_to_call = game.chips_to_call(game.current_player)

    # Effective pot = real pot size + chips to call
    effective_pot = real_pot_size + chips_to_call

    return {'real_pot_size': real_pot_size, 'chips_to_call': chips_to_call, 'effective_pot': effective_pot}


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
                player_cards = [format_card(str(card)) for card in game.get_hand(player_id)]
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
                        winner = {
                            'id': player_id,
                            'stack': game.players[player_id].chips,
                            'won': amount / len(winners_list)
                        }
                        winners.append(winner)

                # If there are multiple winners for the same player, combine them
                winners_by_id = {}
                for winner in winners:
                    if winner['id'] in winners_by_id:
                        winners_by_id[winner['id']]['won'] += winner['won']
                    else:
                        winners_by_id[winner['id']] = winner
                winners = list(winners_by_id.values())

                # Calculate win amount per player for animation
                total_win_amount = sum(winner['won'] for winner in winners)
                win_amount_per_player = total_win_amount / len(winners) if winners else 0
                for winner in winners:
                    winner['won'] = win_amount_per_player

        # Format board cards for victory animation
        formatted_board = [format_card(str(card)) for card in game.board] if hand_over else []

        return jsonify({
            'success': True,
            'hand_over': hand_over,
            'winners': winners if hand_over else None,
            'players_cards': players_cards if hand_over else None,
            'pot': get_total_pot() if hand_over else 0,
            'board': formatted_board if hand_over else [],
            'final_phase': str(game.hand_phase) if hand_over else None
        })
    except Exception as e:
        print(f"Error in take_action: {str(e)}")
        return jsonify({'error': str(e)})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
