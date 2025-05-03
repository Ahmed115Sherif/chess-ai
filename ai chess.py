import pygame, sys, copy

pygame.init()
S = 80
WIN = pygame.display.set_mode((S*8, S*8))
FONT = pygame.font.SysFont("Segoe UI Symbol", 44)
PIECES = {"r": "♜", "k": "♚", "R": "♖", "K": "♔"}
START = [["", "", "", "", "k", "", "", "r"]] + [[""]*8 for _ in range(6)] + [["R", "", "", "", "K", "", "", ""]]

class Chess:
    def __init__(self, ai=False):
        self.b = copy.deepcopy(START)
        self.t = True  # True = White turn
        self.sel = None
        self.ai = ai

    def draw(self):
        for r in range(8):
            for c in range(8):
                color = (232, 235, 239) if (r + c) % 2 == 0 else (125, 135, 150)
                pygame.draw.rect(WIN, color, (c * S, r * S, S, S))
                p = self.b[r][c]
                if p:
                    WIN.blit(FONT.render(PIECES[p], True, (0, 0, 0)), (c * S + 20, r * S + 15))
        pygame.display.update()

    def king_in_check(self, board, white):
        kr, kc = -1, -1
        for r in range(8):
            for c in range(8):
                if board[r][c] == ('K' if white else 'k'):
                    kr, kc = r, c
        for r in range(8):
            for c in range(8):
                p = board[r][c]
                if p and (p.isupper() != white):
                    if self.valid_move(board, (r, c), (kr, kc), p): return True
        return False

    def valid_move(self, board, s, e, p=None):
        sr, sc = s
        er, ec = e
        if not p:
            p = board[sr][sc]
        t = board[er][ec]
        if p == "" or (t and p.isupper() == t.isupper()): return False
        dr, dc = abs(er - sr), abs(ec - sc)
        if p.lower() == "k":
            return max(dr, dc) == 1
        if p.lower() == "r":
            if sr == er:
                step = 1 if ec > sc else -1
                for c in range(sc + step, ec, step):
                    if board[sr][c] != "": return False
                return True
            elif sc == ec:
                step = 1 if er > sr else -1
                for r in range(sr + step, er, step):
                    if board[r][sc] != "": return False
                return True
        return False

    def move(self, s, e):
        if not self.valid_move(self.b, s, e): return False
        temp = copy.deepcopy(self.b)
        temp[e[0]][e[1]] = temp[s[0]][s[1]]
        temp[s[0]][s[1]] = ""
        if self.king_in_check(temp, self.t): return False
        self.b = temp
        self.t = not self.t
        return True

    def all_moves(self, board, white):
        moves = []
        for r in range(8):
            for c in range(8):
                p = board[r][c]
                if p and (p.isupper() == white):
                    for rr in range(8):
                        for cc in range(8):
                            if self.valid_move(board, (r, c), (rr, cc), p):
                                temp = copy.deepcopy(board)
                                temp[rr][cc], temp[r][c] = p, ""
                                if not self.king_in_check(temp, white):
                                    moves.append(temp)
        return moves

    def evaluate(self, board):
        score = {"K": 100, "R": 5}
        return sum(score.get(p.upper(), 0) * (1 if p.isupper() else -1) for row in board for p in row if p)

    def minimax(self, board, depth, maxing):
        if depth == 0: return self.evaluate(board), board
        moves = self.all_moves(board, maxing)
        best = float('-inf') if maxing else float('inf')
        best_board = board
        for m in moves:
            score, _ = self.minimax(m, depth - 1, not maxing)
            if (maxing and score > best) or (not maxing and score < best):
                best, best_board = score, m
        return best, best_board

    def ai_move(self):
        _, best = self.minimax(self.b, 2, False)
        self.b = best
        self.t = True


def menu():
    pygame.display.set_caption("Select Mode")
    WIN.fill((0, 0, 0))
    font = pygame.font.SysFont(None, 60)
    t1 = font.render("1. Player vs Player", True, (255, 255, 255))
    t2 = font.render("2. Player vs AI", True, (255, 255, 255))
    WIN.blit(t1, (100, 200))
    WIN.blit(t2, (100, 300))
    pygame.display.update()
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN:
                mx, my = e.pos
                if 100 <= mx <= 400 and 200 <= my <= 260: return False  # Player vs Player
                if 100 <= mx <= 400 and 300 <= my <= 360: return True   # Player vs AI


def main():
    ai_mode = menu()
    game = Chess(ai=ai_mode)
    game.t = True  # Start with white player's turn in Player vs Player mode
    while True:
        game.draw()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif e.type == pygame.MOUSEBUTTONDOWN:
                r, c = e.pos[1] // S, e.pos[0] // S
                if game.sel is None:
                    if game.b[r][c] != "" and game.b[r][c].isupper() == game.t:
                        game.sel = (r, c)
                else:
                    game.move(game.sel, (r, c))
                    game.sel = None
                    pygame.time.delay(300)
                    if game.ai and not game.t:
                        game.ai_move()


main()
