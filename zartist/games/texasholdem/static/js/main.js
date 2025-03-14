document.addEventListener('DOMContentLoaded', () => {
    const foldBtn = document.getElementById('fold');
    const checkBtn = document.getElementById('check');
    const callBtn = document.getElementById('call');
    const raiseBtn = document.getElementById('raise');
    const allInBtn = document.getElementById('all-in');
    const raiseSlider = document.getElementById('raise-slider');
    const sliderWrapper = document.querySelector('.slider-wrapper');
    const raisePotThird = document.getElementById('raise-pot-third');
    const raisePotHalf = document.getElementById('raise-pot-half');
    const raisePotFull = document.getElementById('raise-pot-full');
    const raisePot2x = document.getElementById('raise-pot-2x');
    const potAmount = document.getElementById('pot-amount');
    const minRaiseLabel = document.getElementById('min-raise-label');
    const maxRaiseLabel = document.getElementById('max-raise-label');

    // Player selection elements
    const playerSelectionScreen = document.getElementById('player-selection-screen');
    const playerCountSelector = document.getElementById('player-count-selector');
    const gameControls = document.querySelector('.game-controls');

    // Hide game controls initially when player selection is shown
    gameControls.classList.add('hidden');

    // Game state variables
    let selectedPlayerCount = 2; // Default to 2 players

    // 辅助函数：将卡片字符串中的花色字母转换为扑克牌符号
    function formatCard(cardStr) {
        if (!cardStr || cardStr.length < 2) return cardStr;

        const rank = cardStr[0];
        const suit = cardStr[1];

        let suitSymbol = suit;
        if (suit === 's') suitSymbol = '\u2660'; // 
        else if (suit === 'h') suitSymbol = '\u2665'; // 
        else if (suit === 'd') suitSymbol = '\u2666'; // 
        else if (suit === 'c') suitSymbol = '\u2663'; // 

        return rank + suitSymbol;
    }

    // 计算有效底池大小的函数
    function calculateEffectivePot(state) {
        // 计算实际底池大小（当前底池 + 所有玩家当前下注）
        let totalBets = 0;
        if (state.players) {
            state.players.forEach(player => {
                if (player.bet) {
                    totalBets += player.bet;
                }
            });
        }

        // 实际底池 = 当前底池 + 所有玩家当前下注
        const realPotSize = parseInt(state.pot) + totalBets;

        // 计算有效底池大小（实际底池 + 需要跟注的筹码）
        const chipsToCall = state.chips_to_call ? parseInt(state.chips_to_call) : 0;
        const effectivePot = realPotSize + chipsToCall;

        return {
            realPotSize,
            chipsToCall,
            effectivePot
        };
    }

    function updateGameState() {
        fetch('/get_game_state')
            .then(response => response.json())
            .then(state => {
                if (state.error) {
                    console.error(state.error);
                    return;
                }

                // 计算有效底池大小
                const { realPotSize } = calculateEffectivePot(state);

                // 更新游戏状态显示 - 使用有效底池大小
                potAmount.textContent = realPotSize || 0;

                // 处理当前玩家的动作按钮
                const isCurrentPlayer = state.current_player !== null &&
                    state.players &&
                    state.players[state.current_player] &&
                    state.players[state.current_player].id === state.current_player;

                // 根据可用动作显示按钮
                if (isCurrentPlayer && state.available_moves) {
                    // 调试日志
                    console.log('State:', state);

                    // 显示FOLD按钮
                    foldBtn.classList.remove('hidden');
                    foldBtn.disabled = false;

                    // 根据需要跟注的筹码决定显示CHECK还是CALL
                    if (state.chips_to_call > 0) {
                        checkBtn.classList.add('hidden');
                        callBtn.classList.remove('hidden');
                        callBtn.textContent = `Call ($${state.chips_to_call})`;
                        callBtn.disabled = false;
                    } else {
                        if (state.available_moves.includes('CHECK')) {
                            checkBtn.classList.remove('hidden');
                        } else {
                            checkBtn.classList.add('hidden');
                        }
                        callBtn.classList.add('hidden');
                        checkBtn.disabled = false;
                    }

                    // 显示RAISE按钮和滑条
                    const canRaise = state.available_moves.includes('RAISE');
                    if (canRaise) {
                        raiseBtn.classList.remove('hidden');
                        sliderWrapper.classList.remove('hidden');
                    } else {
                        raiseBtn.classList.add('hidden');
                        sliderWrapper.classList.add('hidden');
                    }

                    if (canRaise && state.raise_range) {
                        console.log('last_raise:', state.last_raise);
                        console.log('min_raise:', state.min_raise);
                        console.log('current_bet:', state.current_bet);
                        console.log('raise_range:', state.raise_range.min, state.raise_range.max);
                        console.log('chips_to_call:', state.chips_to_call);

                        const potSize = parseInt(state.pot);
                        const chipsToCall = parseInt(state.chips_to_call);

                        // 获取最小和最大加注额(todo: 后续更改跟注规则时改这里)
                        // METHOD1: 至少加上一次RAISE总筹码的的一倍
                        // const minRaiseTotal = Math.max(state.min_raise, Math.min((state.current_bet + state.chips_to_call) * 2, state.raise_range.max));

                        // METHOD2: 至少加上一次RAISE差额
                        const minRaiseTotal = state.raise_range.min;

                        // METHOD3: 至少加上一次RAISE差额的一倍
                        // const minRaiseTotal = state.raise_range.min + state.last_raise;

                        const maxRaise = state.raise_range.max;

                        // 计算加注增量（超出跟注的部分）
                        const raiseIncrement = minRaiseTotal - state.current_bet;

                        // 在Raise按钮上显示总金额和增量
                        raiseBtn.textContent = `Raise to $${minRaiseTotal}(+$${raiseIncrement})`;

                        // 使用公共函数计算有效底池大小
                        const { realPotSize, chipsToCall: chipsToCallValue, effectivePot } = calculateEffectivePot(state);

                        // 计算底池比例值 - 原始值（不包含最小加注限制）
                        const rawPotThirdValue = Math.floor(effectivePot / 3);
                        const rawPotHalfValue = Math.floor(effectivePot / 2);
                        const rawPotFullValue = effectivePot;
                        const rawPot2xValue = Math.floor(effectivePot * 2);

                        // 应用最小加注限制，计算最终加注金额（总下注额）
                        // 确保所有加注都至少达到最小加注额
                        const potThirdRaise = Math.max(minRaiseTotal, chipsToCallValue + rawPotThirdValue);
                        const potHalfRaise = Math.max(minRaiseTotal, chipsToCallValue + rawPotHalfValue);
                        const potFullRaise = Math.max(minRaiseTotal, chipsToCallValue + rawPotFullValue);
                        const pot2xRaise = Math.max(minRaiseTotal, chipsToCallValue + rawPot2xValue);

                        // 设置滑动条范围
                        raiseSlider.min = minRaiseTotal;
                        raiseSlider.max = maxRaise;
                        raiseSlider.value = minRaiseTotal;

                        // 动态设置滑动条标签
                        minRaiseLabel.textContent = `Min: $${minRaiseTotal}`;
                        maxRaiseLabel.textContent = `Max: $${maxRaise}`;

                        // 计算每种加注超出跟注的增量部分
                        const potThirdIncrement = potThirdRaise - chipsToCallValue;
                        const potHalfIncrement = potHalfRaise - chipsToCallValue;
                        const potFullIncrement = potFullRaise - chipsToCallValue;
                        const pot2xIncrement = pot2xRaise - chipsToCallValue;

                        // 更新快捷加注按钮文本 - 显示总金额和增量
                        raisePotThird.textContent = `1/3 Pot to $${potThirdRaise}(+$${potThirdIncrement})`;
                        raisePotHalf.textContent = `1/2 Pot to $${potHalfRaise}(+$${potHalfIncrement})`;
                        raisePotFull.textContent = `1x Pot to $${potFullRaise}(+$${potFullIncrement})`;
                        raisePot2x.textContent = `2x Pot to $${pot2xRaise}(+$${pot2xIncrement})`;
                        allInBtn.textContent = `All In ($${state.players[state.current_player].stack})`;

                        // 存储快捷加注按钮的值
                        raisePotThird.dataset.amount = potThirdRaise;
                        raisePotHalf.dataset.amount = potHalfRaise;
                        raisePotFull.dataset.amount = potFullRaise;
                        raisePot2x.dataset.amount = pot2xRaise;
                        allInBtn.dataset.amount = maxRaise;

                        // 如果玩家筹码不足最小加注，禁用加注按钮
                        const playerChips = state.players[state.current_player].stack;
                        const disableRaise = playerChips < minRaiseTotal;

                        raiseBtn.disabled = disableRaise;
                        raiseSlider.disabled = disableRaise;

                        // 使用总加注额与最小加注额比较来判断底池比例按钮是否应该显示
                        const hideThird = rawPotThirdValue < minRaiseTotal;
                        const hideHalf = rawPotHalfValue < minRaiseTotal;
                        const hideFull = rawPotFullValue < minRaiseTotal;
                        const hide2x = rawPot2xValue < minRaiseTotal;

                        // 显示/隐藏底池比例按钮
                        raisePotThird.classList.toggle('hidden', hideThird);
                        raisePotHalf.classList.toggle('hidden', hideHalf);
                        raisePotFull.classList.toggle('hidden', hideFull);
                        raisePot2x.classList.toggle('hidden', hide2x);

                        // 禁用按钮（如果金额满足显示要求但玩家筹码不足）
                        raisePotThird.disabled = disableRaise || playerChips < potThirdRaise;
                        raisePotHalf.disabled = disableRaise || playerChips < potHalfRaise;
                        raisePotFull.disabled = disableRaise || playerChips < potFullRaise;
                        raisePot2x.disabled = disableRaise || playerChips < pot2xRaise;
                    }

                    // 显示ALL IN按钮 - 始终显示，不再检查canAllIn
                    allInBtn.classList.remove('hidden');
                    // 只有在玩家没有足够筹码时禁用ALL IN按钮
                    const playerChips = state.players[state.current_player].stack;
                    allInBtn.disabled = playerChips <= 0;
                } else {
                    // 隐藏所有动作按钮，但保持ALL IN按钮可见
                    foldBtn.classList.add('hidden');
                    checkBtn.classList.add('hidden');
                    callBtn.classList.add('hidden');
                    raiseBtn.classList.add('hidden');
                    sliderWrapper.classList.add('hidden');
                }

                // 更新牌桌状态
                updateBoard(state.board);
                updatePlayers(state.players, state);
            });
    }

    function updateBoard(board) {
        // 更新公共牌
        for (let i = 1; i <= 5; i++) {
            const cardElement = document.getElementById(`board-${i}`);
            const card = board[i - 1];

            // 检查卡片元素是否已经存在并且有内容
            const existingCard = cardElement.textContent.trim() !== '';
            const hasCardBack = cardElement.querySelector('.card-back');

            if (card) {
                // 格式化卡片显示
                const formattedCard = formatCard(card);
                const cardClass = formattedCard.includes('\u2665') || formattedCard.includes('\u2666') ? 'red' : 'black';

                // 如果是新卡片，创建翻转动画结构
                if (!existingCard && !hasCardBack) {
                    // 清空原有内容
                    cardElement.textContent = '';
                    cardElement.className = 'card';

                    // 创建卡片背面
                    const cardBack = document.createElement('div');
                    cardBack.className = 'card-back';
                    cardElement.appendChild(cardBack);

                    // 创建卡片正面
                    const cardFront = document.createElement('div');
                    cardFront.className = `card-front ${cardClass}`;
                    cardFront.innerHTML = formattedCard;
                    cardElement.appendChild(cardFront);

                    // 延迟翻转，实现逐一翻牌的效果
                    setTimeout(() => {
                        cardElement.classList.add('flipped');
                    }, 300 * (i - 1)); // 每张牌延迟300毫秒
                } else if (existingCard && !cardElement.classList.contains('flipped')) {
                    // 如果卡片已存在但尚未翻转，更新内容并翻转
                    const cardFront = cardElement.querySelector('.card-front') || cardElement;
                    cardFront.innerHTML = formattedCard;
                    cardFront.className = `card-front ${cardClass}`;

                    // 延迟翻转
                    setTimeout(() => {
                        cardElement.classList.add('flipped');
                    }, 300 * (i - 1));
                } else if (!hasCardBack) {
                    // 如果是旧的卡片结构（没有背面），更新为新结构
                    cardElement.textContent = '';
                    cardElement.className = 'card';

                    // 创建卡片背面
                    const cardBack = document.createElement('div');
                    cardBack.className = 'card-back';
                    cardElement.appendChild(cardBack);

                    // 创建卡片正面
                    const cardFront = document.createElement('div');
                    cardFront.className = `card-front ${cardClass}`;
                    cardFront.innerHTML = formattedCard;
                    cardElement.appendChild(cardFront);

                    // 立即翻转，因为这是更新已有卡片
                    cardElement.classList.add('flipped');
                }
            } else {
                // 如果没有卡片，重置为占位符
                cardElement.textContent = '';
                cardElement.className = 'card-placeholder';
                // 移除可能存在的翻转类
                cardElement.classList.remove('flipped');
            }
        }
    }

    function updatePlayers(players, state) {
        // 清空玩家容器
        const playersContainer = document.querySelector('.players-container');
        playersContainer.innerHTML = '';

        // 获取位置信息
        const dealerPosition = state.dealer_position;
        const smallBlindPosition = state.small_blind_position;
        const bigBlindPosition = state.big_blind_position;

        // 过滤出活跃的玩家
        const activePlayers = players.filter(player => player.state !== 'OUT');
        const playerCount = activePlayers.length;

        // 添加玩家
        players.forEach(player => {
            // 如果玩家状态是OUT，不显示
            if (player.state === 'OUT') return;

            const playerDiv = document.createElement('div');
            const isCurrentPlayer = player.id === parseInt(state.current_player);
            playerDiv.className = `player ${isCurrentPlayer ? 'active' : ''}`;
            playerDiv.dataset.playerId = player.id;

            // 使用新的定位逻辑，根据玩家总数和ID来定位
            playerDiv.classList.add(`player-position-${playerCount}-${player.id}`);

            let handHtml = '';
            if (player.hand && player.hand.length > 0) {
                handHtml = `
                    <div class="player-hand">
                        ${player.hand.map(card => `
                            <div class="card ${formatCard(card).includes('\u2665') || formatCard(card).includes('\u2666') ? 'red' : 'black'}">
                                ${formatCard(card)}
                            </div>
                        `).join('')}
                    </div>
                `;
            }

            playerDiv.innerHTML = `
                <div class="player-info">
                    <div class="player-name">Player ${player.id + 1}</div>
                    <div class="player-stack">$${player.stack}</div>
                    <div class="player-bet">Bet: $${player.bet}</div>
                    <div class="player-hand">${handHtml}</div>
                </div>
            `;

            // 添加位置指示器容器
            const indicatorsContainer = document.createElement('div');
            indicatorsContainer.className = 'position-indicators';
            playerDiv.appendChild(indicatorsContainer);

            if (dealerPosition !== null && dealerPosition === player.id) {
                const dealerButton = document.createElement('div');
                dealerButton.className = 'position-indicator dealer-button';
                dealerButton.textContent = 'D';
                indicatorsContainer.appendChild(dealerButton);
            }

            if (smallBlindPosition !== null && smallBlindPosition === player.id) {
                const sbButton = document.createElement('div');
                sbButton.className = 'position-indicator small-blind-button';
                sbButton.textContent = 'SB';
                indicatorsContainer.appendChild(sbButton);
            }

            if (bigBlindPosition !== null && bigBlindPosition === player.id) {
                const bbButton = document.createElement('div');
                bbButton.className = 'position-indicator big-blind-button';
                bbButton.textContent = 'BB';
                indicatorsContainer.appendChild(bbButton);
            }

            playersContainer.appendChild(playerDiv);
        });
    }

    function showVictoryAnimation(winners, playersCards, potAmount, boardCards) {
        // 创建遮罩层
        const overlay = document.createElement('div');
        overlay.className = 'victory-overlay';
        document.body.appendChild(overlay);

        // 点击遮罩层外部区域开始新的一局
        overlay.addEventListener('click', (event) => {
            // 如果点击的是遮罩层本身，而不是内部元素
            if (event.target === overlay) {
                document.body.removeChild(overlay);
                // 直接开始新的一局，而不是显示开始按钮
                fetch('/start_hand', { method: 'POST' })
                    .then(response => response.json())
                    .then(data => {
                        if (data.error) {
                            console.error(data.error);
                            alert(data.error);
                            return;
                        }
                        updateGameState();
                    });
            }
        });

        // 创建胜利动画容器
        const animationContainer = document.createElement('div');
        animationContainer.className = 'victory-animation';
        overlay.appendChild(animationContainer);

        // 添加标题
        const title = document.createElement('h2');
        title.textContent = '手牌结束!';
        title.className = 'victory-title';
        animationContainer.appendChild(title);

        // 创建玩家牌展示区
        const cardsContainer = document.createElement('div');
        cardsContainer.className = 'all-players-cards';
        animationContainer.appendChild(cardsContainer);

        // 展示所有玩家的牌
        playersCards.forEach(player => {
            const playerCardDiv = document.createElement('div');
            playerCardDiv.className = 'player-result';

            // 检查该玩家是否是赢家
            const isWinner = winners.some(w => w.id === player.id);
            if (isWinner) {
                playerCardDiv.classList.add('winner');
            }

            // 添加玩家信息
            const playerInfo = document.createElement('div');
            playerInfo.className = 'player-info';

            // 添加玩家名称
            const playerName = document.createElement('span');
            playerName.className = 'player-name';
            playerName.textContent = `玩家 ${player.id + 1}`;
            playerInfo.appendChild(playerName);

            // 添加赢家标志
            if (isWinner) {
                const winnerBadge = document.createElement('span');
                winnerBadge.className = 'winner-badge';
                winnerBadge.textContent = '赢家!';
                playerInfo.appendChild(winnerBadge);

                // 添加筹码计算
                const winner = winners.find(w => w.id === player.id);
                if (winner) {
                    const initialStack = Math.round(winner.stack - winner.won);
                    const finalStack = Math.round(winner.stack);
                    const wonAmount = Math.round(winner.won);

                    // 添加筹码信息容器
                    const stackDiv = document.createElement('div');
                    stackDiv.className = 'winner-stack';

                    // 添加筹码文本
                    stackDiv.appendChild(document.createTextNode('筹码: '));

                    // 添加初始筹码
                    const initialStackSpan = document.createElement('span');
                    initialStackSpan.className = 'initial-stack';
                    initialStackSpan.textContent = `$${initialStack}`;
                    stackDiv.appendChild(initialStackSpan);

                    // 添加加号
                    stackDiv.appendChild(document.createTextNode(' + '));

                    // 添加赢得的筹码
                    const wonAmountSpan = document.createElement('span');
                    wonAmountSpan.className = 'won-amount';
                    wonAmountSpan.textContent = '$0';
                    stackDiv.appendChild(wonAmountSpan);

                    // 添加等号
                    stackDiv.appendChild(document.createTextNode(' = '));

                    // 添加最终筹码
                    const finalStackSpan = document.createElement('span');
                    finalStackSpan.className = 'final-stack';
                    finalStackSpan.textContent = `$${initialStack}`;
                    stackDiv.appendChild(finalStackSpan);

                    // 将筹码信息添加到玩家信息中
                    playerInfo.appendChild(stackDiv);

                    // 添加数字增长动画
                    // 设置更长的动画时间 - 2秒
                    const animationDuration = 2000; // 2秒
                    const fps = 30;
                    const steps = animationDuration / 1000 * fps;
                    const increment = wonAmount / steps;

                    let currentWonAmount = 0;
                    let currentFinalStack = initialStack;
                    let step = 0;

                    const animateNumbers = () => {
                        currentWonAmount += increment;
                        currentFinalStack = initialStack + currentWonAmount;

                        if (currentWonAmount >= wonAmount || step >= steps) {
                            // 动画结束，显示最终值
                            wonAmountSpan.textContent = '$' + wonAmount;
                            finalStackSpan.textContent = '$' + finalStack;
                        } else {
                            // 更新显示的数值
                            wonAmountSpan.textContent = '$' + Math.round(currentWonAmount);
                            finalStackSpan.textContent = '$' + Math.round(currentFinalStack);

                            step++;
                            requestAnimationFrame(animateNumbers);
                        }
                    };

                    // 开始动画
                    setTimeout(() => {
                        requestAnimationFrame(animateNumbers);
                    }, 500); // 延迟0.5秒开始动画
                }
            }

            playerCardDiv.appendChild(playerInfo);

            // 添加玩家牌
            const cardsDiv = document.createElement('div');
            cardsDiv.className = 'player-cards';
            player.cards.forEach(card => {
                const cardDiv = document.createElement('div');
                const formattedCard = formatCard(card);
                cardDiv.className = `card ${formattedCard.includes('\u2665') || formattedCard.includes('\u2666') ? 'red' : 'black'}`;
                cardDiv.textContent = formattedCard;
                cardsDiv.appendChild(cardDiv);
            });
            playerCardDiv.appendChild(cardsDiv);

            cardsContainer.appendChild(playerCardDiv);
        });

        // 展示公共牌
        const boardContainer = document.createElement('div');
        boardContainer.className = 'board-cards-container';
        animationContainer.appendChild(boardContainer);

        const boardTitle = document.createElement('div');
        boardTitle.className = 'board-title';
        boardTitle.textContent = '公共牌';
        boardContainer.appendChild(boardTitle);

        const boardCardsDiv = document.createElement('div');
        boardCardsDiv.className = 'board-cards';
        boardCards.forEach(card => {
            const cardDiv = document.createElement('div');
            const formattedCard = formatCard(card);
            cardDiv.className = `card ${formattedCard.includes('\u2665') || formattedCard.includes('\u2666') ? 'red' : 'black'}`;
            cardDiv.textContent = formattedCard;
            boardCardsDiv.appendChild(cardDiv);
        });
        boardContainer.appendChild(boardCardsDiv);

        // 创建下一局按钮
        const nextHandBtn = document.createElement('button');
        nextHandBtn.className = 'next-hand-btn';
        nextHandBtn.textContent = '下一局';
        nextHandBtn.style.display = 'block'; // 直接显示按钮
        nextHandBtn.style.fontSize = '20px'; // 增加字体大小
        nextHandBtn.style.padding = '15px 30px'; // 增加按钮大小
        nextHandBtn.style.marginTop = '30px'; // 增加按钮上边距
        animationContainer.appendChild(nextHandBtn);

        // 添加按钮事件
        nextHandBtn.addEventListener('click', () => {
            document.body.removeChild(overlay);
            // 直接开始新的一局，而不是显示开始按钮
            fetch('/start_hand', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        console.error(data.error);
                        alert(data.error);
                        return;
                    }
                    updateGameState();
                });
        });
    }

    function resetBoardCards() {
        // 重置公共牌区域的所有卡片
        for (let i = 1; i <= 5; i++) {
            const cardElement = document.getElementById(`board-${i}`);
            // 清空内容并移除翻转状态
            cardElement.textContent = '';
            cardElement.className = 'card-placeholder';
            cardElement.classList.remove('flipped');
        }
    }

    function takeAction(actionType, amount = null) {
        const requestBody = { action_type: actionType };

        if (actionType === 'RAISE' && amount !== null) {
            requestBody.amount = parseInt(amount);
        }

        fetch('/take_action', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        })
            .then(response => response.json())
            .then(result => {
                if (result.error) {
                    console.error(result.error);
                    return;
                }

                // 处理手牌结束
                if (result.hand_over && result.winners && result.winners.length > 0) {
                    console.log('Hand over! Winners:', result.winners);
                    console.log('Players cards:', result.players_cards);
                    console.log('Pot amount:', result.pot);
                    console.log('Board cards:', result.board);

                    // 显示胜利动画
                    showVictoryAnimation(result.winners, result.players_cards, result.pot, result.board);
                }

                updateGameState();
            });
    }

    // 玩家选择功能
    function initPlayerSelection() {
        // 添加玩家数量选择按钮事件
        const playerButtons = playerCountSelector.querySelectorAll('.player-count-btn');
        playerButtons.forEach(button => {
            button.addEventListener('click', () => {
                // 移除其他按钮的选中状态
                playerButtons.forEach(btn => btn.classList.remove('selected'));
                // 添加当前按钮的选中状态
                button.classList.add('selected');
                // 保存选择的玩家数量
                selectedPlayerCount = parseInt(button.dataset.count);

                // 直接开始游戏，无需点击开始按钮
                // 隐藏玩家选择界面
                playerSelectionScreen.style.display = 'none';
                // 显示游戏控制界面
                gameControls.classList.remove('hidden');
                // 初始化游戏
                initGameWithPlayerCount(selectedPlayerCount);
            });
        });

        // 默认选中2个玩家
        playerButtons[0].classList.add('selected');
    }

    // 根据选择的玩家数量初始化游戏
    function initGameWithPlayerCount(count) {
        // 发送请求到服务器，初始化指定数量的玩家
        fetch('/init_game', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ player_count: count })
        })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.error(data.error);
                    alert(data.error);
                    return;
                }
                // 更新游戏状态
                updateGameState();

                // 开始第一局
                startFirstHand();
            });
    }

    // 开始第一局的函数
    function startFirstHand() {
        // 重置牌桌上的卡片
        resetBoardCards();

        fetch('/start_hand', { method: 'POST' })
            .then(response => response.json())
            .then(result => {
                if (result.error) {
                    console.error(result.error);
                    return;
                }
                updateGameState();
            });
    }

    // 按钮事件监听器
    foldBtn.addEventListener('click', () => takeAction('FOLD'));
    checkBtn.addEventListener('click', () => takeAction('CHECK'));
    callBtn.addEventListener('click', () => takeAction('CALL'));

    // 更新加注滑块改变时的显示金额
    raiseSlider.addEventListener('input', (e) => {
        const raiseAmount = parseInt(e.target.value);
        const currentCallAmount = document.querySelector('.call-btn') ?
            parseInt(document.querySelector('.call-btn').textContent.match(/\$(\d+)/)[1] || 0) : 0;
        const raiseIncrement = raiseAmount - currentCallAmount;
        // 显示总金额和增量
        raiseBtn.textContent = `Raise to $${raiseAmount}(+$${raiseIncrement})`;
    });

    // RAISE按钮直接使用滑块的值
    raiseBtn.addEventListener('click', () => {
        takeAction('RAISE', parseInt(raiseSlider.value));
    });

    // 快捷加注按钮设置滑块值并更新显示
    const quickRaiseButtons = [raisePotThird, raisePotHalf, raisePotFull, raisePot2x];
    quickRaiseButtons.forEach(button => {
        button.addEventListener('click', () => {
            const amount = parseInt(button.dataset.amount);
            raiseSlider.value = amount;
            raiseBtn.textContent = `Raise ($${amount})`;
            takeAction('RAISE', amount); // 
        });
    });

    // All In按钮直接使用最大值
    allInBtn.addEventListener('click', () => {
        takeAction('ALL_IN');
    });

    // 初始化玩家选择界面
    initPlayerSelection();
});
