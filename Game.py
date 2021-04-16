from random import shuffle, choice

from Human import Human
from Board import Board
from MCTS import MCTS


def graphic(board, human, ai):
    """
    在终端绘制棋盘，显示棋局的状态
    """
    width = board.width
    height = board.height

    print("Human Player", human.player, "with X".rjust(3))
    print("AI    Player", ai.player, "with O".rjust(3))
    print()
    for x in range(width):
        print("{0:8}".format(x), end='')
    print('\r\n')
    for i in range(height - 1, -1, -1):
        print("{0:4}".format(i), end='')
        for j in range(width):
            loc = i * width + j
            if board.states[loc] == human.player:
                print('X'.center(8), end='')
            elif board.states[loc] == ai.player:
                print('O'.center(8), end='')
            else:
                print('_'.center(8), end='')
        print("\r\n")


class Game(object):
    """
    game server
    """

    def __init__(self, board, kwargs):
        self.board = board
        self.player = [1, 2]  # player1 and player2
        self.n_in_row = int(kwargs.get('n_in_row', 5))
        self.time = float(kwargs.get('max_calc_time', 5))
        self.max_actions = int(kwargs.get('max_actions', 1000))

    def start(self):
        p1, p2 = self.init_player()
        self.board.init_board()

        ai = MCTS(self.board, [p1, p2])
        human = Human(self.board, p2)
        players = {p1: ai, p2: human}
        turn = [p2, p1]
        # shuffle(turn)  # 玩家和电脑的出手顺序随机
        while True:
            p = turn.pop(0)
            turn.append(p)
            player_in_turn = players[p]
            move = player_in_turn.get_action()
            self.board.update(p, move)
            graphic(self.board, human, ai)
            end, winner = self.game_end(ai)
            if end:
                if winner != -1:
                    print("Game end. Winner is", players[winner])
                break

    def init_player(self):
        plist = list(range(len(self.player)))
        index1 = choice(plist)
        plist.remove(index1)
        index2 = choice(plist)

        return self.player[index1], self.player[index2]

    def game_end(self, ai):
        """
        检查游戏是否结束
        """
        win, winner = ai.has_a_winner(self.board)
        if win:
            return True, winner
        elif not len(self.board.available):
            print("Game end. Tie")
            return True, -1
        return False, -1


if __name__ == '__main__':
    b = Board()
    g = Game(b, {"max_calc_time": 5, "max_actions": 10000})
    g.start()
