import copy
import time
from math import log, sqrt
from random import choice


class MCTS(object):
    """
    AI player, use Monte Carlo Tree Search with UCB
    """

    def __init__(self, board, play_turn, n_in_row=5, time=5, max_actions=1000):

        self.board = board
        self.play_turn = play_turn  # 出手顺序
        self.calculation_time = float(time)  # 最大运算时间
        self.max_actions = max_actions  # 每次模拟对局最多进行的步数
        self.n_in_row = n_in_row

        self.player = play_turn[0]  # 轮到电脑出手，所以出手顺序中第一个总是电脑
        self.confident = 1.96  # UCB中的常数
        self.plays = {}  # 记录着法参与模拟的次数，键形如(player, move)，即（玩家，落子）
        self.wins = {}  # 记录着法获胜的次数
        self.max_depth = 1

    def get_action(self):  # return move

        if len(self.board.available) == 1:
            return self.board.available[0]  # 棋盘只剩最后一个落子位置，直接返回

        # 每次计算下一步时都要清空plays和wins表，因为经过AI和玩家的2步棋之后，整个棋盘的局面发生了变化，原来的记录已经不适用了——
        # 原先普通的一步现在可能是致胜的一步，如果不清空，会影响现在的结果，导致这一步可能没那么“致胜”了
        self.plays = {}
        self.wins = {}
        simulations = 0
        begin = time.time()
        while time.time() - begin < self.calculation_time:
            board_copy = copy.deepcopy(self.board)  # 模拟会修改board的参数，所以必须进行深拷贝，与原board进行隔离
            play_turn_copy = copy.deepcopy(self.play_turn)  # 每次模拟都必须按照固定的顺序进行，所以进行深拷贝防止顺序被修改
            self.run_simulation(board_copy, play_turn_copy)  # 进行MCTS
            simulations += 1

        print("total simulations=", simulations)

        move, percent_wins = self.select_one_move()  # 选择最佳着法
        location = self.board.move_to_location(move)
        print('Maximum depth searched:', self.max_depth)

        print("AI move: %d,%d the percent_wins:%f \n" % (location[0], location[1], percent_wins))

        return move

    def run_simulation(self, board, play_turn):
        """
        MCTS main process
        """

        plays = self.plays
        wins = self.wins
        available = board.available

        player = self.get_player(play_turn)  # 获取当前出手的玩家
        visited_states = set()  # 记录当前路径上的全部着法
        winner = -1
        expand = True

        # Simulation
        for t in range(1, self.max_actions + 1):
            # Selection
            # 如果所有着法都有统计信息，则获取UCB最大的着法
            if all(plays.get((player, move)) for move in available):
                log_total = log(
                    sum(plays[(player, move)] for move in available))
                value, move = max(
                    ((wins[(player, move)] / plays[(player, move)]) +
                     sqrt(self.confident * log_total / plays[(player, move)]), move)
                    for move in available)
            else:
                # 否则随机选择一个着法
                move = choice(available)

            board.update(player, move)

            # Expand
            # 每次模拟最多扩展一次，每次扩展只增加一个着法
            if expand and (player, move) not in plays:
                expand = False
                plays[(player, move)] = 0
                wins[(player, move)] = 0
                if t > self.max_depth:
                    self.max_depth = t

            visited_states.add((player, move))

            is_full = not len(available)
            win, winner = self.has_a_winner(board)
            if is_full or win:  # 游戏结束，没有落子位置或有玩家获胜
                break

            player = self.get_player(play_turn)

        # Back-propagation
        for player, move in visited_states:
            if (player, move) not in plays:
                continue
            plays[(player, move)] += 1  # 当前路径上所有着法的模拟次数加1
            if player == winner:
                wins[(player, move)] += 1  # 获胜玩家的所有着法的胜利次数加1

    def get_player(self, players):
        p = players.pop(0)
        players.append(p)
        return p

    def select_one_move(self):
        percent_wins, move = max(
            (self.wins.get((self.player, move), 0) /
             self.plays.get((self.player, move), 1),
             move)
            for move in self.board.available)  # 选择胜率最高的着法

        return move, percent_wins

    def has_a_winner(self, board):
        """
        检查是否有玩家获胜
        """
        moved = list(set(range(board.width * board.height)) - set(board.available))
        if len(moved) < self.n_in_row + 2:
            return False, -1

        width = board.width
        height = board.height
        states = board.states
        n = self.n_in_row
        for m in moved:
            h = m // width
            w = m % width
            player = states[m]

            if (w in range(width - n + 1) and
                    len(set(states[i] for i in range(m, m + n))) == 1):  # 横向连成一线
                return True, player

            if (h in range(height - n + 1) and
                    len(set(states[i] for i in range(m, m + n * width, width))) == 1):  # 竖向连成一线
                return True, player

            if (w in range(width - n + 1) and h in range(height - n + 1) and
                    len(set(states[i] for i in range(m, m + n * (width + 1), width + 1))) == 1):  # 右斜向上连成一线
                return True, player

            if (w in range(n - 1, width) and h in range(height - n + 1) and
                    len(set(states[i] for i in range(m, m + n * (width - 1), width - 1))) == 1):  # 左斜向下连成一线
                return True, player

        return False, -1

    def __str__(self):
        return "AI"
