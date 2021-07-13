import pygame
import sys
import random
import math
import matplotlib.pyplot as plt

# ******************** 変数／定数 ********************
# =============== COLOR ===============
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (96, 96, 96)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
# =============== CONDITION ===============
WALL = 0    # 壁
ROAD = 1    # 通路
WAY = 2     # 通った経路
# =============== DIRECTION ===============
DIR_UP = 0      # 上方向
DIR_RIGHT = 1   # 右方向
DIR_DOWN = 2    # 下方向
DIR_LEFT = 3    # 左方向
# =============== GAME ===============
idx = 0
tmr = 0
fps = 30
# =============== PARAMETER ===============
ETA = 0.1           # 学習率
GAMMA = 0.9         # 時間割引率
episode = 0         # スタートからゴールまで行った回数
EPSILON = 0.5       # ε-greedy法の初期値
epsilon = 0
MAX_EPISODE = 100   # 繰り返す回数
max_episode = 0
step_result = 0     # 学習した時のゴールまでのステップ数
step_now = 0        # 現在のステップ数
step_recode = []    # 取得したステップ数を記録
# =============== STATE / ACTION ===============
s = 0       # 現在の状態
a = 0       # 現在の行動(移動方向)
s_next = 0  # 次の状態
a_next = 0  # 次の行動(移動方向)
# =============== MAZE ===============
MAZE_SIZE = 60
MAZE_NUM = 11
SCREEN_SIZE = MAZE_SIZE * MAZE_NUM
maze = []
for y in range(MAZE_NUM):
    maze.append([0]*MAZE_NUM)
# =============== LEARNING ===============
theta_0 = [0.0] * MAZE_NUM**2
pi = [0.0] * MAZE_NUM**2
Q = [0.0] * MAZE_NUM**2
for i in range(MAZE_NUM**2):
    theta_0[i] = [0.0]*4
    pi[i] = [0.0]*4
    Q[i] = [0.0]*4

s_a_history = [[-1, -1]]


# ============================================================
#                           DRAW
# ============================================================

# ******************** 文字の描画 ********************
def draw_text(sc, txt, x, y, siz, col, center):
    fnt = pygame.font.Font(None, siz)
    sur = fnt.render(txt, True, col)

    if center == True:
        x = x - sur.get_width()/2
        y = y - sur.get_width()/2

    sc.blit(sur, [x, y])


# ******************** 迷路全体／説明画面の描画 ********************
def draw_all_maze(sc):
    for y in range(MAZE_NUM):
        for x in range(MAZE_NUM):
            X = x * MAZE_SIZE
            Y = y * MAZE_SIZE

            if maze[y][x] == WALL:  # 壁
                pygame.draw.rect(sc, GRAY, [X, Y, MAZE_SIZE, MAZE_SIZE])
            if maze[y][x] == ROAD:  # 通路
                pygame.draw.rect(sc, WHITE, [X, Y, MAZE_SIZE, MAZE_SIZE])
            if maze[y][x] == WAY:   # 通った経路
                pygame.draw.rect(sc, ORANGE, [X, Y, MAZE_SIZE, MAZE_SIZE])

    # 現在地
    if idx == 7: # 最終経路
        state = s_a_history[step_now][0]
    else:
        state = s_a_history[-1][0]
    x = state % MAZE_NUM
    y = state // MAZE_NUM
    X = x * MAZE_SIZE
    Y = y * MAZE_SIZE
    pygame.draw.rect(sc, RED, [X, Y, MAZE_SIZE, MAZE_SIZE])
    
    # スタート
    x = 1
    y = 1
    X = x * MAZE_SIZE
    Y = y * MAZE_SIZE
    pygame.draw.rect(sc, BLUE, [X, Y, MAZE_SIZE, MAZE_SIZE])
    draw_text(sc, "S", X+MAZE_SIZE/2, Y+MAZE_SIZE/2, MAZE_SIZE, WHITE, True)
    
    # ゴール
    x = MAZE_NUM - 2
    y = MAZE_NUM - 2
    X = x * MAZE_SIZE
    Y = y * MAZE_SIZE
    pygame.draw.rect(sc, BLUE, [X, Y, MAZE_SIZE, MAZE_SIZE])
    draw_text(sc, "G", X+MAZE_SIZE/2, Y+MAZE_SIZE/2, MAZE_SIZE, WHITE, True)



    
    # =============== DRAW TEXT ===============
    # タイトル画面
    if idx == 0:
        draw_text(sc, "SELECT  [1]  or  [2]", SCREEN_SIZE/2, SCREEN_SIZE+150, 40, BLACK, True)
        draw_text(sc, "[1]  :  VIEW  OFF", SCREEN_SIZE/2, SCREEN_SIZE+150, 30, BLACK, True)
        draw_text(sc, "[2]  :  VIEW  ON ", SCREEN_SIZE/2, SCREEN_SIZE+180, 30, BLACK, True)

    # 画像表示なし
    elif idx == 1:
        draw_text(sc, "LEARNING  NOW  ...", SCREEN_SIZE/2, SCREEN_SIZE+ 160, 30, BLACK, True)

    # 画像表示あり 結果表示
    elif 2 <= idx <= 5:
        # エピソード回数
        draw_text(sc, "EPISODE : ", SCREEN_SIZE/2-100, SCREEN_SIZE+30, 40, BLACK, False)
        if 2 <= idx <= 4:
            draw_text(sc, "{:10d}".format(episode), SCREEN_SIZE/2+40, SCREEN_SIZE+30, 40, BLACK, False)
        elif idx == 5:
            draw_text(sc, "{:10d}".format(episode-1), SCREEN_SIZE/2+40, SCREEN_SIZE+30, 40, BLACK, False)
        # ステップ数
        draw_text(sc, "STEP       : ", SCREEN_SIZE/2-100, SCREEN_SIZE+80, 40, BLACK, False)
        draw_text(sc, "{:10d}".format(len(s_a_history)-1), SCREEN_SIZE/2+40, SCREEN_SIZE+80, 40, BLACK, False)

    # 選択画面
    elif idx == 6:
        draw_text(sc, "SELECT  [1]  or  [2]", SCREEN_SIZE/2, SCREEN_SIZE+150, 40, BLACK, True)
        # リスタート
        draw_text(sc, "[1]  RESTART", SCREEN_SIZE/2-200, SCREEN_SIZE+75, 30, BLACK, False)
        # 再学習
        draw_text(sc, "[2]  MORE  LEARNING", SCREEN_SIZE/2-200, SCREEN_SIZE+110, 30, BLACK, False)
        # 学習結果の表示
        draw_text(sc, "[3]  RESULT  VIEW", SCREEN_SIZE/2+30, SCREEN_SIZE+75, 30, BLACK, False)
        # 学習結果(ステップ数)のグラフ化
        draw_text(sc, "[4]  GRAPH", SCREEN_SIZE/2+30, SCREEN_SIZE+110, 30, BLACK, False)

# ============================================================
#                           MAZE
# ============================================================

# ******************** 棒倒し方による迷路の自動生成 ********************
def make_maze():
    XP = [0, 1, 0, -1]
    YP = [-1, 0, 1, 0]

    # ボードの周囲を壁にする
    for x in range(MAZE_NUM):
        maze[0][x] = WALL
        maze[MAZE_NUM-1][x] = WALL
    for y in range(MAZE_NUM-1):
        maze[y][0] = WALL
        maze[y][MAZE_NUM-1] = WALL

    # ボードの中を全て通路にする
    for y in range(1, MAZE_NUM-1):
        for x in range(1, MAZE_NUM-1):
            maze[y][x] = ROAD

    # 棒倒し法
    for y in range(2, MAZE_NUM-2, 2):
        for x in range(2, MAZE_NUM-2, 2):
            maze[y][x] = WALL
    for y in range(2, MAZE_NUM-2, 2):
        for x in range(2, MAZE_NUM-2, 2):
            d = random.randint(0, 3)
            if x > 2:
                d = random.randint(0, 2)
            maze[y+YP[d]][x+XP[d]] = WALL


# ******************** 通った通路の表示をなくす ********************
def delete_way():
    for y in range(MAZE_NUM):
        for x in range(MAZE_NUM):
            if maze[y][x] == WAY:
                maze[y][x] = ROAD


# ============================================================
#                       PARAMETER
# ============================================================

# ******************** パラメーターの初期化 ********************
def init_parameter():
    for i in range(MAZE_NUM**2):
        for j in range(4):
            theta_0[i][j] = 0.0
            pi[i][j] = 0.0
            Q[i][j] = 0.0
            

# ******************** 初期の方策を決定するパラメータtheta_0を設定 ********************
def calc_theta_0():
    
    for i in range(MAZE_NUM**2):
        y = i // MAZE_NUM
        x = i % MAZE_NUM
        
        # 壁以外
        if maze[y][x] == WALL:
            continue

        # 進行方向：↑、→、↓、←

        # 上方向に移動可能
        if maze[y-1][x] != WALL:
            theta_0[i][DIR_UP] = 1.0
        # 右方向に移動可能
        if maze[y][x+1] != WALL:
            theta_0[i][DIR_RIGHT] = 1.0
        # 下方向に移動可能
        if maze[y+1][x] != WALL:
            theta_0[i][DIR_DOWN] = 1.0
        # 左方向に移動可能
        if maze[y][x-1] != WALL:
            theta_0[i][DIR_LEFT] = 1.0


# ******************** 方策パラメータtheta_0をランダム方策piに変換する関数の定義 ********************
def pi_from_theta(theta):
    
    for i in range(MAZE_NUM**2):
        y = i // MAZE_NUM
        x = i % MAZE_NUM
        
        if maze[y][x] == WALL:
            continue

        # 移動可能な方向数をカウント
        direction_count = 0
        for j in range(4):
            if theta[i][j] != WALL:
                direction_count += 1

        # 割合を計算
        for j in range(4):
            pi[i][j] = theta[i][j] / direction_count


# ******************** 初期の行動価値関数Qを設定 ********************
def set_Q():
    for state in range(MAZE_NUM**2):
        for action in range(4):
            Q[state][action] = theta_0[state][action] * random.random()


# ============================================================
#                       ε-GREEDY METHOD
# ============================================================

# ******************** ε-greedy法より行動を求める ********************
def get_action(s, epsilon):

    # 行動を決める
    next_direction = -1
    
    # εの確率でランダムに動く
    if random.random() < epsilon:
        while True:
            next_direction = random.randint(0, 3)
            if pi[s][next_direction] > 0:
                break
            
    # Qの最大値の行動を採用する
    else:
        max_action = max(Q[s])
        next_direction = Q[s].index(max_action)

    # 行動をindexに
    if next_direction == DIR_UP:
        action = 0
    elif next_direction == DIR_RIGHT:
        action = 1
    elif next_direction == DIR_DOWN:
        action = 2
    elif next_direction == DIR_LEFT:
        action = 3
    return action


# ******************** 行動から次の状態を求める ********************
def get_s_next(s, a):
    next_direction = a

    # 行動から次の状態を決める
    if next_direction == DIR_UP:
        s_next = s - MAZE_NUM
    elif next_direction == DIR_RIGHT:
        s_next = s + 1
    elif next_direction == DIR_DOWN:
        s_next = s + MAZE_NUM
    elif next_direction == DIR_LEFT:
        s_next = s - 1

    return s_next




# ============================================================
#                           Q-Learning
# ============================================================

# ******************** Q-Learningによる行動価値関数Qの更新 ********************
def Qlearning(s, a, r, s_next, a_next):
    # ゴールした場合
    if s_next == MAZE_NUM ** 2 -(MAZE_NUM + 2):
        Q[s][a] = Q[s][a] + ETA * (r - Q[s][a])
    else:
        max_action = max(Q[s_next])
        a_next = Q[s_next].index(max_action)
        Q[s][a] = Q[s][a] + ETA * (r + GAMMA * Q[s_next][a_next] - Q[s][a])


# ============================================================
#                           LEARNING
# ============================================================

# ******************** スタートからゴールまで、状態・行動・Qを学習 ********************
def learning_from_start_to_goal(epsilon):
    global s_a_history
    
    s = MAZE_NUM + 1 # スタート地点
    a = a_next = get_action(s, epsilon) # 初期の行動
    s_a_history = [[MAZE_NUM+1, -1]] # エージェントの行動を記録するリスト

    # ε-greedyの値を少しずつ小さくする
    epsilon = epsilon / 2

    # ゴールするまで繰り返す
    while True:
        # 行動の更新
        a = a_next
        # 現在の状態に行動を代入
        s_a_history[-1][1] = a
        # 次の状態を格納
        s_next = get_s_next(s, a)

        # 次の状態を代入。行動はまだ未定のため-1
        s_a_history.append([s_next, -1])

        # ゴールにたどり着いた場合 -> 報酬
        if s_next == MAZE_NUM ** 2 - (MAZE_NUM + 2):
            r = 1 # 報酬
            a_next = -1
        else:
            r = 0
            a_next = get_action(s_next, epsilon)

        # 価値関数を更新
        Qlearning(s, a, r, s_next, a_next)

        # 終了判定
        if s_next == MAZE_NUM ** 2 -(MAZE_NUM + 2): # ゴール地点なら終了
            break
        else:
            s = s_next


# ******************** Q-Learnigで迷路を解く ********************
def learning_Qlearnig():
    global epsilon, episode
    
    while True:
        # ε-greedyの値を少しずつ小さくする
        epsilon = epsilon / 2

        # Q-Learningで迷路を解き、移動した履歴と更新したQを求める
        learning_from_start_to_goal(epsilon)

        # ステップ数を記録
        step_recode.append(len(s_a_history)-1)
        print("エピソード:{:5d}      スタート〜ゴールのステップ数：{:10d}".format(episode, len(s_a_history)-1))
        
        # スタートからゴールまで、指定された回数を繰り返す
        episode = episode + 1
        if episode > max_episode:
            break


# ============================================================
#                           MAIN
# ============================================================

# ******************** メインループ ********************
def main():
    global idx, tmr, episode, max_episode, epsilon
    global step_result, step_now, step_recode
    global s, a, s_next, a_next, s_a_history
    global fps
    
    pygame.init()
    pygame.display.set_caption("Q-Learning")

    screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE + 150))
    clock = pygame.time.Clock()

    tmr = 0
    
    while True:
        tmr = tmr + 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill(WHITE)
        key = pygame.key.get_pressed()
        

        # タイトル
        if idx == 0:
            if tmr == 1:
                episode = 1
                epsilon = EPSILON
                max_episode = MAX_EPISODE

                # 迷路の自動生成(棒倒し法)
                make_maze()
                # パラメーターの設定
                init_parameter()
                calc_theta_0()
                pi_from_theta(theta_0)
                set_Q()
                # 記録したステップ数の初期化
                step_recode = []
                
            elif tmr > 60:
                if key[pygame.K_1] == True:
                    idx = 1
                    tmr = 0
                if key[pygame.K_2] == True:
                    idx = 2
                    tmr = 0


        # 画像表示なし：学習スタート
        elif idx == 1:
            if tmr == 1:
                # 指定された回数分、Q-Learningで迷路を解く
                learning_Qlearnig()
            else:
                idx = 5
                tmr = 0
            

        # 画像表示あり：初期行動の設定
        elif idx == 2:
            s = MAZE_NUM + 1 # スタート地点
            a = a_next = get_action(s, epsilon) # 初期の行動
            s_a_history = [[MAZE_NUM+1, -1]] # エージェントの行動を記録するリスト

            idx = 3
            tmr = 0


        # 画像表示あり：ゴールするまで繰り返す
        elif idx == 3:
            # ε-greedyの値を少しずつ小さくする
            epsilon = epsilon / 2
            
            # 行動の更新
            a = a_next
            # 現在の状態に行動を代入
            s_a_history[-1][1] = a
            # 次の状態を格納
            s_next = get_s_next(s, a)

            # 次の状態を代入。行動はまだ未定のため-1
            s_a_history.append([s_next, -1])

            # 報酬を与え、次の行動を求める
            if s_next == MAZE_NUM ** 2 - (MAZE_NUM + 2): # ゴールにたどり着いた場合
                r = 1 # 報酬
                a_next = -1
            else:
                r = 0
                a_next = get_action(s_next, epsilon)

            # 価値関数を更新
            Qlearning(s, a, r, s_next, a_next)

            # 終了判定
            if s_next == MAZE_NUM ** 2 -(MAZE_NUM + 2): # ゴール地点なら終了
                idx = 4
                tmr = 0
            else:
                s = s_next


        # ゴールした時
        elif idx == 4:    
            if tmr == 1:
                # ステップ数を記録
                step_recode.append(len(s_a_history)-1)
                print("エピソード:{:5d}      スタート〜ゴールのステップ数：{:10d}".format(episode, len(s_a_history)-1))

            episode = episode + 1
            # スタートからゴールを指定された回数を繰り返したら終了
            if episode > max_episode:
                idx = 5
                tmr = 0
            # 再度、スタート地点から開始
            else:
                idx = 2
                tmr = 0


        # 学習完了
        elif idx == 5:
            if tmr == 1:
                print("********** FINISH  LEARNING **********")
                print()
            elif tmr == 180:
                idx = 6
                tmr = 0
                

        # 選択画面
        elif idx == 6:
            if tmr > 60:
                # リスタート(初期状態)
                if key[pygame.K_1] == True:
                    idx = 0
                    tmr = 0
                # さらに学習をする
                if key[pygame.K_2] == True:
                    delete_way()
                    max_episode += MAX_EPISODE
                    idx = 0
                    tmr = 1
                # 学習したルートを表示
                if key[pygame.K_3] == True:
                    step_result = len(s_a_history) - 1
                    step_now = 1
                    fps = MAZE_NUM
                    idx = 7
                    tmr = 0
                # 学習したステップ数のグラフ表示
                if key[pygame.K_4] == True:
                    idx = 8
                    tmr = 0
                
                

        # 最終経路の表示
        elif idx == 7:
            # 現在のステップ数の時の状態(迷路上での位置)を取得
            state = s_a_history[step_now][0]
            # 行列変換
            y = state // MAZE_NUM
            x = state % MAZE_NUM
            # 通過した経路とする
            maze[y][x] = WAY

            # 次のステップへ
            step_now += 1
                
            # ゴールまで移動したら終了
            if step_now == step_result:
                fps = 60
                idx = 6
                tmr = 0
            

        # ステップ数のグラフ表示
        elif idx == 8:
            # x軸方向：エピソード回数
            x = list(range((max_episode+1)//10+1, max_episode+1))
            # y軸方向：ステップ数
            y = step_recode[(max_episode+1)//10:max_episode+1]

            # タイトル／x軸ラベル／y軸ラベル／グリッド
            plt.title("LEARNING  TRANSITION")
            plt.xlabel("EPISODE")
            plt.ylabel("STEP")
            plt.grid(True)

            plt.plot(x, y)
            plt.show()

            idx = 6
            tmr = 0
            
            
        

        # 迷路の描画
        draw_all_maze(screen)
        
        pygame.display.update()
        clock.tick(fps)

if __name__ == '__main__':
    main()
