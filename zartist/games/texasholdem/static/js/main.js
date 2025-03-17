document.addEventListener('DOMContentLoaded', () => {

    // action buttons
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
    const minRaiseLabel = document.getElementById('min-raise-label');
    const maxRaiseLabel = document.getElementById('max-raise-label');



    // pot amount
    const potAmount = document.getElementById('pot-amount');

    // Player selection elements
    const playerSelectionScreen = document.getElementById('player-selection-screen');
    const playerCountSelector = document.getElementById('player-count-selector');
    const gameControls = document.querySelector('.game-controls');

    // Hide game controls initially when player selection is shown
    gameControls.classList.add('hidden');

    // Game state variables
    let selectedPlayerCount = 2; // Default to 2 players

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
                playerSelectionScreen.style.display = 'none';
                gameControls.classList.remove('hidden');
                initGameWithPlayerCount(selectedPlayerCount);
            });
        });
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


    function updateGameState() {
        fetch('/get_game_state')
            .then(response => response.json())
            .then(state => {
                if (state.error) {
                    console.error("Error getting game state:", state.error);
                    return;
                }

                // Access data from the new state structure
                const publicInfo = state.public_info;
                const privateInfo = state.private_info;

                // Update pot amount from public info
                potAmount.textContent = publicInfo.pot;

                // Update action using both public and private info
                updateAction(publicInfo, privateInfo);

                // Update board from public info
                updateBoard(publicInfo.board);

                // Update players using both public and private info
                updatePlayers(publicInfo.players, publicInfo, privateInfo);
            });
    }

    // 更新玩家动作按钮的函数
    function updateAction(publicInfo, privateInfo) {
        // 根据可用动作显示按钮
        if (privateInfo.available_moves && privateInfo.available_moves.length > 0) {
            // 调试日志
            console.log('Public Info:', publicInfo);
            console.log('Private Info:', privateInfo);

            // 显示FOLD按钮
            foldBtn.classList.remove('hidden');
            foldBtn.disabled = false;

            // 根据需要跟注的筹码决定显示CHECK还是CALL
            if (privateInfo.chips_to_call > 0) {
                checkBtn.classList.add('hidden');
                callBtn.classList.remove('hidden');
                callBtn.textContent = `Call ($${privateInfo.chips_to_call})`;
                callBtn.disabled = false;
            } else {
                if (privateInfo.available_moves.includes('CHECK')) {
                    checkBtn.classList.remove('hidden');
                } else {
                    checkBtn.classList.add('hidden');
                }
                callBtn.classList.add('hidden');
                checkBtn.disabled = false;
            }

            // 处理RAISE相关控件
            const canRaise = privateInfo.available_moves.includes('RAISE');
            updateRaiseControls(canRaise, publicInfo, privateInfo);

            // 显示ALL IN按钮 - 始终显示，不再检查canAllIn
            allInBtn.classList.remove('hidden');
            // 只有在玩家没有足够筹码时禁用ALL IN按钮
            const currentPlayer = privateInfo.current_player;
            const playerChips = currentPlayer !== null ? publicInfo.players[currentPlayer].stack : 0;
            allInBtn.disabled = playerChips <= 0;
        } else {
            // 隐藏所有动作按钮，但保持ALL IN按钮可见
            foldBtn.classList.add('hidden');
            checkBtn.classList.add('hidden');
            callBtn.classList.add('hidden');
            raiseBtn.classList.add('hidden');
            sliderWrapper.classList.add('hidden');
        }
    }

    // 处理RAISE相关控件的函数
    function updateRaiseControls(canRaise, publicInfo, privateInfo) {
        // 显示或隐藏RAISE按钮和滑条
        if (canRaise) {
            raiseBtn.classList.remove('hidden');
            sliderWrapper.classList.remove('hidden');
        } else {
            raiseBtn.classList.add('hidden');
            sliderWrapper.classList.add('hidden');
            return; // 如果不能加注，直接返回
        }

        // 只有当可以加注且有加注范围时才继续
        if (privateInfo.raise_range) {
            console.log('last_raise:', publicInfo.last_raise);
            console.log('min_raise:', privateInfo.min_raise);
            console.log('current_bet:', privateInfo.current_bet);
            console.log('raise_range:', privateInfo.raise_range.min, privateInfo.raise_range.max);
            console.log('chips_to_call:', privateInfo.chips_to_call);

            const minRaiseTotal = privateInfo.raise_range.min;
            const maxRaise = privateInfo.raise_range.max;

            // 计算加注增量（超出跟注的部分）
            const raiseIncrement = minRaiseTotal - privateInfo.current_bet;

            // 在Raise按钮上显示总金额和增量
            raiseBtn.textContent = `Raise to $${minRaiseTotal}(+$${raiseIncrement})`;

            // 设置滑动条范围
            raiseSlider.min = minRaiseTotal;
            raiseSlider.max = maxRaise;
            raiseSlider.value = minRaiseTotal;

            // 动态设置滑动条标签
            minRaiseLabel.textContent = `Min: $${minRaiseTotal}`;
            maxRaiseLabel.textContent = `Max: $${maxRaise}`;

            // 使用服务器计算的底池比例加注值
            if (privateInfo.pot_raise_values) {
                // 定义底池比例按钮和对应的数据
                const raiseButtons = [
                    { button: raisePotThird, data: privateInfo.pot_raise_values.pot_third, label: '1/3 Pot' },
                    { button: raisePotHalf, data: privateInfo.pot_raise_values.pot_half, label: '1/2 Pot' },
                    { button: raisePotFull, data: privateInfo.pot_raise_values.pot_full, label: '1x Pot' },
                    { button: raisePot2x, data: privateInfo.pot_raise_values.pot_2x, label: '2x Pot' }
                ];

                // 获取玩家筹码和禁用条件
                const currentPlayer = privateInfo.current_player;
                const playerChips = currentPlayer !== null ? publicInfo.players[currentPlayer].stack : 0;

                // 更新每个按钮的状态和文本
                raiseButtons.forEach(item => {
                    if (item.data.valid && item.data.total <= playerChips) {
                        item.button.disabled = false;
                        item.button.textContent = `${item.label} ($${item.data.total})`;
                        item.button.dataset.raiseAmount = item.data.total;
                    } else {
                        item.button.disabled = true;
                        item.button.textContent = `${item.label}`;
                    }
                });

                // 启用滑动条
                raiseSlider.disabled = false;

                // 更新滑动条值变化事件
                raiseSlider.oninput = function () {
                    const value = parseInt(this.value);
                    const increment = value - privateInfo.current_bet;
                    raiseBtn.textContent = `Raise to $${value}(+$${increment})`;
                    raiseBtn.dataset.raiseAmount = value;
                };

                // 设置初始加注金额
                raiseBtn.dataset.raiseAmount = minRaiseTotal;
            }
        }
    }

    function updateBoard(board) {
        for (let i = 1; i <= 5; i++) {
            const cardElement = document.getElementById(`board-${i}`);
            const card = board[i - 1];

            if (card) {
                // 使用服务器提供的已格式化卡片数据
                const cardText = card.text;
                const cardClass = card.color;

                // 检查卡片是否需要翻转动画
                const needsFlipAnimation = cardElement.className === 'card-placeholder' ||
                    !cardElement.classList.contains('flipped');

                // 如果需要翻转动画
                if (needsFlipAnimation) {
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
                    cardFront.innerHTML = cardText;
                    cardElement.appendChild(cardFront);

                    // 延迟翻转，实现逐一翻牌的效果
                    setTimeout(() => {
                        cardElement.classList.add('flipped');
                    }, 300 * (i - 1)); // 每张牌延迟300毫秒
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

    function updatePlayers(players, publicInfo, privateInfo) {
        // 清空玩家容器
        const playersContainer = document.querySelector('.players-container');
        playersContainer.innerHTML = '';

        // u8f93u51fau73a9u5bb6u72b6u6001u4fe1u606f
        console.log('Players state:', players.map(p => ({ id: p.id, state: p.state })));

        // u83b7u53d6u4f4du7f6eu4fe1u606f
        const dealerPosition = publicInfo.dealer_position;
        const smallBlindPosition = publicInfo.small_blind_position;
        const bigBlindPosition = publicInfo.big_blind_position;

        // u8ba1u7b97u6d3bu8dc3u73a9u5bb6u6570u91cf
        const playerCount = players.length; // u4f7fu7528u603bu73a9u5bb6u6570

        // u6dfbu52a0u73a9u5bb6
        players.forEach(player => {
            const playerDiv = document.createElement('div');
            playerDiv.className = `player`;

            const isCurrentPlayer = player.id === parseInt(privateInfo.current_player);
            const isOutPlayer = player.state.includes('OUT');
            if (isCurrentPlayer) playerDiv.classList.add('active');
            if (isOutPlayer) playerDiv.classList.add('out');

            playerDiv.dataset.playerId = player.id;
            playerDiv.classList.add(`player-position-${playerCount}-${player.id}`);

            let handHtml = '';
            // 只有当前玩家才能看到手牌，使用privateInfo中的手牌信息
            if (isCurrentPlayer && privateInfo.hand && privateInfo.hand.length > 0) {
                handHtml = `
                    <div class="player-hand">
                        ${privateInfo.hand.map(card => `
                            <div class="card ${card.color}">
                                ${card.text}
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

            // u6dfbu52a0u73a9u5bb6u4f4du7f6eu5b9au4f4du5bb6
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
                const formattedCard = card.text;
                cardDiv.className = `card ${card.color}`;
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
            const formattedCard = card.text;
            cardDiv.className = `card ${card.color}`;
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
        // 重置牌桌上的卡片
        for (let i = 1; i <= 5; i++) {
            const cardElement = document.getElementById(`board-${i}`);
            // 清空内容并移除翻转状态
            cardElement.textContent = '';
            cardElement.className = 'card-placeholder';
            cardElement.classList.remove('flipped');
        }
    }

    function takeAction(actionType, amount = null) {
        // 构建请求数据
        const data = { action_type: actionType };
        if (amount !== null) {
            data.amount = amount;
        }

        // 发送动作请求
        fetch('/take_action', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
            .then(response => response.json())
            .then(result => {
                if (result.error) {
                    console.error("Error taking action:", result.error);
                    return;
                }

                // 更新游戏状态
                updateGameState();

                // 处理获胜者信息
                if (result.winners) {
                    // 获取所有玩家的手牌
                    const playersCards = result.players_cards;
                    // 获取底池金额
                    const potAmount = result.pot;
                    // 获取公共牌
                    const boardCards = result.board;

                    // 显示获胜动画
                    showVictoryAnimation(result.winners, playersCards, potAmount, boardCards);
                }
            });
    }


    // 按钮事件监听器
    foldBtn.addEventListener('click', () => takeAction('FOLD'));
    checkBtn.addEventListener('click', () => takeAction('CHECK'));
    callBtn.addEventListener('click', () => takeAction('CALL'));

    // RAISE按钮使用dataset中存储的金额
    raiseBtn.addEventListener('click', () => {
        const raiseAmount = parseInt(raiseBtn.dataset.raiseAmount);
        takeAction('RAISE', raiseAmount);
    });

    // 快捷加注按钮使用dataset中存储的金额
    const quickRaiseButtons = [raisePotThird, raisePotHalf, raisePotFull, raisePot2x];
    quickRaiseButtons.forEach(button => {
        button.addEventListener('click', () => {
            if (!button.disabled) {
                const amount = parseInt(button.dataset.raiseAmount);
                raiseSlider.value = amount;
                takeAction('RAISE', amount);
            }
        });
    });

    // All In按钮直接使用最大值
    allInBtn.addEventListener('click', () => {
        takeAction('ALL_IN');
    });

    // 初始化玩家选择界面
    initPlayerSelection();
});
