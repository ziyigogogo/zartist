document.addEventListener('DOMContentLoaded', () => {
    const startHandBtn = document.getElementById('start-hand');
    const foldBtn = document.getElementById('fold');
    const checkBtn = document.getElementById('check');
    const callBtn = document.getElementById('call');
    const raiseBtn = document.getElementById('raise');
    const allInBtn = document.getElementById('all-in');
    const raiseSlider = document.getElementById('raise-slider');
    const raiseSliderContainer = document.querySelector('.raise-slider-container');
    const raisePotThird = document.getElementById('raise-pot-third');
    const raisePotHalf = document.getElementById('raise-pot-half');
    const raisePotFull = document.getElementById('raise-pot-full');
    const raisePot150 = document.getElementById('raise-pot-150');
    const potAmount = document.getElementById('pot-amount');
    
    // Player selection elements
    const playerSelectionScreen = document.getElementById('player-selection-screen');
    const playerCountSelector = document.getElementById('player-count-selector');
    const startGameBtn = document.getElementById('start-game-btn');
    
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

    function updateGameState() {
        fetch('/get_game_state')
            .then(response => response.json())
            .then(state => {
                if (state.error) {
                    console.error(state.error);
                    return;
                }

                // 更新游戏状态显示
                potAmount.textContent = state.pot;

                // 显示/隐藏开始按钮
                if (state.is_hand_running) {
                    startHandBtn.classList.add('hidden');
                } else {
                    startHandBtn.classList.remove('hidden');
                }
                startHandBtn.disabled = state.is_hand_running;

                // 处理当前玩家的动作按钮
                const isCurrentPlayer = state.current_player !== null && 
                                     state.players && 
                                     state.players[state.current_player] && 
                                     state.players[state.current_player].id === state.current_player;

                // 根据可用动作显示按钮
                if (isCurrentPlayer && state.available_moves) {
                    // 调试日志
                    console.log('Current Player:', state.current_player);
                    console.log('Available moves:', state.available_moves);
                    console.log('Phase:', state.phase);
                    console.log('Chips to call:', state.chips_to_call);
                    
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
                        raiseSliderContainer.classList.remove('hidden');
                    } else {
                        raiseBtn.classList.add('hidden');
                        raiseSliderContainer.classList.add('hidden');
                    }
                    
                    if (canRaise && state.raise_range) {
                        // 获取当前底池大小和需要跟注的筹码
                        const potSize = parseInt(state.pot);
                        const chipsToCall = parseInt(state.chips_to_call);
                        
                        // 计算最小加注额 (至少为跟注额的两倍)
                        const minRaise = Math.max(state.raise_range.min, chipsToCall * 2);
                        // 最大加注额
                        const maxRaise = state.raise_range.max;
                        
                        // 在Raise按钮上显示最小加注金额
                        raiseBtn.textContent = `Raise ($${minRaise})`;
                        
                        // 计算有效底池大小（包括跟注额）
                        const effectivePot = potSize + chipsToCall;
                        
                        // 计算原始的底池比例值（不带最小值限制）
                        const rawPotThirdValue = Math.floor(effectivePot / 3);
                        const rawPotHalfValue = Math.floor(effectivePot / 2);
                        const rawPotFullValue = effectivePot;
                        const rawPot150Value = Math.floor(effectivePot * 1.5);
                        
                        // 应用最小值限制得到最终加注金额
                        const potThirdRaise = Math.max(minRaise, rawPotThirdValue);
                        const potHalfRaise = Math.max(minRaise, rawPotHalfValue);
                        const potFullRaise = Math.max(minRaise, rawPotFullValue);
                        const pot150Raise = Math.max(minRaise, rawPot150Value);
                        
                        // 设置滑动条范围
                        raiseSlider.min = minRaise;
                        raiseSlider.max = maxRaise;
                        raiseSlider.value = minRaise;
                        
                        // 更新显示的加注金额
                        raiseBtn.textContent = `Raise ($${minRaise})`;
                        
                        // 更新快捷加注按钮文本 - 即使按钮隐藏也更新文本
                        raisePotThird.textContent = `1/3 Pot ($${potThirdRaise})`;
                        raisePotHalf.textContent = `1/2 Pot ($${potHalfRaise})`;
                        raisePotFull.textContent = `1x Pot ($${potFullRaise})`;
                        raisePot150.textContent = `1.5x Pot ($${pot150Raise})`;
                        allInBtn.textContent = `All In ($${maxRaise})`;
                        
                        // 存储快捷加注按钮的值
                        raisePotThird.dataset.amount = potThirdRaise;
                        raisePotHalf.dataset.amount = potHalfRaise;
                        raisePotFull.dataset.amount = potFullRaise;
                        raisePot150.dataset.amount = pot150Raise;
                        allInBtn.dataset.amount = maxRaise; // 
                        
                        // 如果玩家筹码不足最小加注，禁用加注按钮
                        const playerChips = state.players[state.current_player].stack;
                        const disableRaise = playerChips < minRaise;
                        
                        raiseBtn.disabled = disableRaise;
                        raiseSlider.disabled = disableRaise;
                        
                        // 显示/隐藏快捷加注按钮，而不仅是禁用
                        // 修复逻辑：当原始计算值小于最小加注额时隐藏按钮
                        // 使用visibility而不是display，这样布局不会变化
                        const hideThird = rawPotThirdValue < minRaise;
                        const hideHalf = rawPotHalfValue < minRaise;
                        const hideFull = rawPotFullValue < minRaise;
                        const hide150 = rawPot150Value < minRaise;
                        
                        if (hideThird) {
                            raisePotThird.classList.add('hidden');
                        } else {
                            raisePotThird.classList.remove('hidden');
                        }
                        
                        if (hideHalf) {
                            raisePotHalf.classList.add('hidden');
                        } else {
                            raisePotHalf.classList.remove('hidden');
                        }
                        
                        if (hideFull) {
                            raisePotFull.classList.add('hidden');
                        } else {
                            raisePotFull.classList.remove('hidden');
                        }
                        
                        if (hide150) {
                            raisePot150.classList.add('hidden');
                        } else {
                            raisePot150.classList.remove('hidden');
                        }
                        
                        // 禁用按钮（如果金额满足显示要求但玩家筹码不足）
                        raisePotThird.disabled = disableRaise || playerChips < potThirdRaise;
                        raisePotHalf.disabled = disableRaise || playerChips < potHalfRaise;
                        raisePotFull.disabled = disableRaise || playerChips < potFullRaise;
                        raisePot150.disabled = disableRaise || playerChips < pot150Raise;
                    }
                    
                    // 显示ALL IN按钮
                    const canAllIn = state.available_moves.includes('ALL_IN');
                    if (canAllIn) {
                        allInBtn.classList.remove('hidden');
                        allInBtn.disabled = false;
                    } else {
                        allInBtn.classList.add('hidden');
                    }
                } else {
                    // 隐藏所有动作按钮
                    foldBtn.classList.add('hidden');
                    checkBtn.classList.add('hidden');
                    callBtn.classList.add('hidden');
                    raiseBtn.classList.add('hidden');
                    raiseSliderContainer.classList.add('hidden');
                    allInBtn.classList.add('hidden');
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
            
            if (card) {
                // 格式化卡片显示
                const formattedCard = formatCard(card);
                cardElement.textContent = formattedCard;
                cardElement.className = 'card';
                if (formattedCard.includes('\u2665') || formattedCard.includes('\u2666')) {
                    cardElement.classList.add('red');
                } else {
                    cardElement.classList.add('black');
                }
            } else {
                cardElement.textContent = '';
                cardElement.className = 'card-placeholder';
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
            playerInfo.innerHTML = `
                <span class="player-name">玩家 ${player.id + 1}</span>
                ${isWinner ? '<span class="winner-badge">赢家!</span>' : ''}
            `;
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
        
        // 创建赢家展示
        const winnersDiv = document.createElement('div');
        winnersDiv.className = 'winners-display';
        animationContainer.appendChild(winnersDiv);
        
        // 展示每个赢家的信息
        winners.forEach(winner => {
            const winnerDiv = document.createElement('div');
            winnerDiv.className = 'winner-info';
            
            // 计算筹码变化
            const initialStack = Math.round(winner.stack - winner.won);
            const finalStack = Math.round(winner.stack);
            const wonAmount = Math.round(winner.won);
            
            winnerDiv.innerHTML = `
                <div class="winner-name">玩家 ${winner.id + 1}</div>
                <div class="winner-stack">筹码: <span class="initial-stack">$${initialStack}</span> + <span class="won-amount">$${wonAmount}</span> = <span class="final-stack">$${finalStack}</span></div>
            `;
            winnersDiv.appendChild(winnerDiv);
        });
        
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

    // 事件处理函数
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
            });
        });
        
        // 默认选中2个玩家
        playerButtons[0].classList.add('selected');
        
        // 开始游戏按钮事件
        startGameBtn.addEventListener('click', () => {
            // 隐藏玩家选择界面
            playerSelectionScreen.style.display = 'none';
            // 初始化游戏
            initGameWithPlayerCount(selectedPlayerCount);
        });
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
        });
    }

    // 按钮事件监听器
    startHandBtn.addEventListener('click', () => {
        fetch('/start_hand', { method: 'POST' })
            .then(response => response.json())
            .then(result => {
                if (result.error) {
                    console.error(result.error);
                    return;
                }
                updateGameState();
            });
    });
    
    foldBtn.addEventListener('click', () => takeAction('FOLD'));
    checkBtn.addEventListener('click', () => takeAction('CHECK'));
    callBtn.addEventListener('click', () => takeAction('CALL'));
    
    // 更新加注滑块改变时的显示金额
    raiseSlider.addEventListener('input', (e) => {
        const raiseAmount = parseInt(e.target.value);
        raiseBtn.textContent = `Raise ($${raiseAmount})`;
    });
    
    // RAISE按钮直接使用滑块的值
    raiseBtn.addEventListener('click', () => {
        takeAction('RAISE', parseInt(raiseSlider.value));
    });
    
    // 快捷加注按钮设置滑块值并更新显示
    const quickRaiseButtons = [raisePotThird, raisePotHalf, raisePotFull, raisePot150];
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
