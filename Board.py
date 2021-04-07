class Board(object):
    """
    board for game
    """

    def __init__(self, width=8, height=8, n_in_row=5):
        self.width = width
        self.height = height
        self.states = {}  # 记录当前棋盘的状态，键是位置，值是棋子，这里用玩家来表示棋子类型
        self.n_in_row = n_in_row  # 表示几个相同的棋子连成一线算作胜利
        self.available = list(range(self.width * self.height))  # 表示棋盘上所有合法的位置，这里简单的认为空的位置即合法

    def init_board(self):
        if self.width < self.n_in_row or self.height < self.n_in_row:
            raise Exception('board width and height can not less than %d' % self.n_in_row)  # 棋盘不能过小

        for m in self.available:
            self.states[m] = -1  # -1表示当前位置为空

    def move_to_location(self, move):
        h = move // self.width
        w = move % self.width
        return [h, w]

    def location_to_move(self, location):
        if len(location) != 2:
            return -1
        h = location[0]
        w = location[1]
        move = h * self.width + w
        if move not in range(self.width * self.height):
            return -1
        return move

    def update(self, player, move):  # player在move处落子，更新棋盘
        self.states[move] = player
        self.available.remove(move)
