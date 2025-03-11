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
player_count = 2  # Default player count


def init_game():
    global game, player_count
    logger.info(f"Initializing game with player_count: {player_count}")

    if not game:
        # 使用 player_count 作为 max_players 参数
        game = TexasHoldEm(buyin=500, big_blind=5, small_blind=2, max_players=player_count)
        
        # 初始化玩家状态
        for i in range(player_count):
            game.players[i].chips = 500
            game.players[i].state = PlayerState.IN
            logger.info(f"Player {i} set to IN")
    
    return game


@app.route('/')
def index():
    init_game()
    return render_template('index.html')


@app.route('/init_game', methods=['POST'])
def initialize_game():
    try:
        global game, player_count
        data = request.get_json()
        player_count = data.get('player_count', 2)  # Default to 2 if not specified
        logger.info(f"Received request to initialize game with player_count: {player_count}")

        # Ensure player_count is within valid range
        player_count = max(2, min(player_count, 10))
        logger.info(f"Adjusted player_count to: {player_count}")

        # Initialize a new game with the specified number of players
        game = TexasHoldEm(buyin=500, big_blind=5, small_blind=2, max_players=player_count)

        # Activate the specified number of players
        for i in range(game.max_players):
            if i < player_count:
                game.players[i].chips = 500
                game.players[i].state = PlayerState.IN
                logger.info(f"Player {i} set to IN")
            else:
                game.players[i].state = PlayerState.OUT
                logger.info(f"Player {i} set to OUT")

        return jsonify({'success': True, 'player_count': player_count})
    except Exception as e:
        logger.error(f"Error initializing game: {str(e)}")
        return jsonify({'error': str(e)})


@app.route('/start_hand', methods=['POST'])
def start_hand():
    try:
        global game, player_count
        game = init_game()
        logger.info(f"Starting hand with player_count: {player_count}")

        #
        if game.is_hand_running():
            logger.info("Hand is already running, resetting game")
            #
            game = TexasHoldEm(buyin=500, big_blind=5, small_blind=2, max_players=player_count)
            for i in range(game.max_players):
                if i < player_count:
                    game.players[i].chips = 500
                    game.players[i].state = PlayerState.IN
                    logger.info(f"Player {i} set to IN")
                else:
                    game.players[i].state = PlayerState.OUT
                    logger.info(f"Player {i} set to OUT")
        else:
            logger.info("Setting up players for new hand")
            #
            for i in range(game.max_players):
                if i < player_count and game.players[i].chips > 0:
                    game.players[i].state = PlayerState.IN
                    logger.info(f"Player {i} set to IN (has chips)")
                else:
                    game.players[i].state = PlayerState.OUT
                    logger.info(f"Player {i} set to OUT (no chips or beyond player count)")

        #
        active_players = sum(
            1 for i in range(game.max_players) if game.players[i].state not in (PlayerState.OUT, PlayerState.SKIP))
        logger.info(f"Active players count: {active_players}")

        if active_players < 2:
            logger.info("Not enough active players, ensuring at least 2 players")
            #
            for i in range(min(player_count, game.max_players)):
                if i < 2:  # Ensure at least 2 players are active
                    game.players[i].chips = 500 if game.players[i].chips <= 0 else game.players[i].chips
                    game.players[i].state = PlayerState.IN
                    logger.info(f"Forced Player {i} to IN with chips")

            #
            active_players = sum(
                1 for i in range(game.max_players) if game.players[i].state not in (PlayerState.OUT, PlayerState.SKIP))
            logger.info(f"Updated active players count: {active_players}")

            if active_players < 2:
                logger.error("Still not enough active players")
                return jsonify({'error': 'Need at least 2 active players to start a hand'})

        game.start_hand()
        logger.info("Hand started successfully")
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error in start_hand: {str(e)}")
        return jsonify({'error': str(e)})


@app.route('/get_game_state')
def get_game_state():
    try:
        global game, player_count
        game = init_game()
        logger.info(f"Getting game state with player_count: {player_count}")

        # Check if current player is outside our player count range
        if game.current_player is not None and game.current_player >= player_count:
            logger.warning(
                f"Current player {game.current_player} is outside player count {player_count}. Adjusting game state.")
            # Find the first player within our range who is in the game
            for i in range(player_count):
                if game.players[i].state not in (PlayerState.OUT, PlayerState.SKIP):
                    game.current_player = i
                    logger.info(f"Adjusted current player to {i}")
                    break

        # Special handling for dealer and blind positions in 2-player games
        if player_count == 2:
            # In heads-up (2 player) poker, button is SB, other player is BB
            dealer_pos = game.btn_loc if game.btn_loc >= 0 and game.btn_loc < player_count else 0
            sb_pos = dealer_pos  # In heads-up, dealer is small blind
            bb_pos = (dealer_pos + 1) % player_count  # Other player is big blind
            logger.info(f"2-player game: Dealer={dealer_pos}, SB={sb_pos}, BB={bb_pos}")
        else:
            # Standard positions for 3+ players
            dealer_pos = game.btn_loc if game.btn_loc >= 0 and game.btn_loc < player_count else 0
            sb_pos = game.sb_loc if game.sb_loc >= 0 and game.sb_loc < player_count else (dealer_pos + 1) % player_count
            bb_pos = game.bb_loc if game.bb_loc >= 0 and game.bb_loc < player_count else (dealer_pos + 2) % player_count
            logger.info(f"Standard game: Dealer={dealer_pos}, SB={sb_pos}, BB={bb_pos}")

        state = {
            'is_hand_running': game.is_hand_running(),
            'current_player': game.current_player,
            'phase': str(game.hand_phase) if game.is_hand_running() else 'Not Started',
            'board': [str(card) for card in game.board] if game.is_hand_running() else [],
            'dealer_position': dealer_pos,
            'small_blind_position': sb_pos,
            'big_blind_position': bb_pos,
            'player_count': player_count
        }

        #
        pot_amount = 0
        if game.is_hand_running():
            #
            for pot in game.pots:
                pot_amount += pot.get_amount()

            #
            for i in range(min(player_count, game.max_players)):
                if game.players[i].state != PlayerState.OUT:
                    pot_amount += game.player_bet_amount(i)
        state['pot'] = pot_amount

        #
        if game.is_hand_running() and game.current_player is not None and game.current_player < player_count:
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
            logger.info(f"Current player: {game.current_player}")
            logger.info(f"Player state: {game.players[game.current_player].state}")
            logger.info(f"Available moves: {state['available_moves']}")
            logger.info(f"Chips to call: {state['chips_to_call']}")
            logger.info(f"Player chips: {game.players[game.current_player].chips}")
            logger.info(f"Raise option: {game.raise_option}")
            if hasattr(moves, 'raise_range'):
                logger.info(f"Raise range: {state['raise_range']}")

            #
            logger.info(f"Minimum raise: {moves.raise_range.start}")
            logger.info(f"Maximum raise: {moves.raise_range.stop - 1}")

        #
        state['players'] = []
        # Only include players up to player_count
        for i in range(min(player_count, game.max_players)):
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
            logger.info(f"Added player {i} to game state with state {player_info['state']}")

        return jsonify(state)
    except Exception as e:
        logger.error(f"Error in get_game_state: {str(e)}")
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
