import os
import random
import sys
import time
import math
import pygame as pg


WIDTH = 1600  # ゲームウィンドウの幅
HEIGHT = 900  # ゲームウィンドウの高さ
MAIN_DIR = os.path.split(os.path.abspath(__file__))[0]
NUM_OF_BOMBS = 5
SCORE = 0


def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内or画面外を判定し，真理値タプルを返す関数
    引数：こうかとん，または，爆弾SurfaceのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate


class Bird:
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -5),
        pg.K_DOWN: (0, +5),
        pg.K_LEFT: (-5, 0),
        pg.K_RIGHT: (+5, 0),
    }

    def __init__(self, num: int, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 xy：こうかとん画像の位置座標タプル
        """
        self.dire = (+5,0)
        img0 = pg.transform.rotozoom(pg.image.load(f"{MAIN_DIR}/fig/{num}.png"), 0, 2.0)
        img = pg.transform.flip(img0, True, False)  # デフォルトのこうかとん（右向き）
        self.img = img
        self.imgs = {  # 0度から反時計回りに定義
            (0,  0): img,
            (+5, 0): img,  # 右
            (+5, -5): pg.transform.rotozoom(img, 45, 1.0),  # 右上
            (0, -5): pg.transform.rotozoom(img, 90, 1.0),  # 上
            (-5, -5): pg.transform.rotozoom(img0, -45, 1.0),  # 左上
            (-5, 0): img0,  # 左
            (-5, +5): pg.transform.rotozoom(img0, 45, 1.0),  # 左下
            (0, +5): pg.transform.rotozoom(img, -90, 1.0),  # 下
            (+5, +5): pg.transform.rotozoom(img, -45, 1.0),  # 右下
        }
        # self.img = pg.transform.flip(  # 左右反転
        #     pg.transform.rotozoom(  # 2倍に拡大
        #         pg.image.load(f"{MAIN_DIR}/fig/{num}.png"), 
        #         0, 
        #         2.0), 
        #     True, 
        #     False
        # )
        self.rct = self.img.get_rect()
        self.rct.center = xy

    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.img = pg.transform.rotozoom(pg.image.load(f"{MAIN_DIR}/fig/{num}.png"), 0, 2.0)
        screen.blit(self.img, self.rct)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        self.rct.move_ip(sum_mv)
        if check_bound(self.rct) != (True, True):
            self.rct.move_ip(-sum_mv[0], -sum_mv[1])
        self.img = self.imgs[tuple(sum_mv)]
        screen.blit(self.img, self.rct)
        if sum_mv != [0,0]:
            self.dire = tuple(sum_mv)


class Bomb:
    """
    爆弾に関するクラス
    """
#     def __init__(self, color: tuple[int, int, int], rad: int):
#         """
#         引数に基づき爆弾円Surfaceを生成する
#         引数1 color：爆弾円の色タプル
#         引数2 rad：爆弾円の半径
#         """
#         self.img = pg.Surface((2*rad, 2*rad))
#         pg.draw.circle(self.img, color, (rad, rad), rad)
#         self.img.set_colorkey((0, 0, 0))
#         self.rct = self.img.get_rect()
#         self.rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
#         self.vx, self.vy = +5, +5

    def __init__(self):
        """
        爆弾円Surfaceを生成する
        """
        rads = [10,20,30,40,50]
        colors = [(255,0,0),(0,255,0),(0,0,255),(255,255,0),(255,0,255)]
        rad = random.choice(rads)
        self.img = pg.Surface((2*rad, 2*rad))
        pg.draw.circle(self.img, random.choice(colors), (rad, rad), rad)
        self.img.set_colorkey((0, 0, 0))
        self.rct = self.img.get_rect()
        self.rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        self.vx, self.vy = random.randint(-5, 5), random.randint(-5, 5)

    def update(self, screen: pg.Surface):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        yoko, tate = check_bound(self.rct)
        if not yoko:
            self.vx *= -1
        if not tate:
            self.vy *= -1
        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct)


class Beam:
    """
    ビームに関するクラス
    """
    def __init__(self, bird:Bird):
        """
        ビーム画像Surfaceを生成する
        引数2 xy：こうかとん画像の位置座標タプル
        """
        self.vx, self.vy = bird.dire[0],bird.dire[1]
        shi_ta = math.atan2(-self.vy,self.vx)
        self.beam = pg.transform.rotozoom(pg.image.load(f"{MAIN_DIR}/fig/beam.png"), math.degrees(shi_ta), 1.0)
        self.rct = self.beam.get_rect()
        self.rct.centery = bird.rct.centery + bird.rct.height * self.vy / 5
        self.rct.centerx = bird.rct.centerx + bird.rct.width * self.vx / 5

    def update(self, screen: pg.Surface):
        """
        ビームを速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.beam, self.rct)


class Score:
    """
    スコアに関するクラス
    """
    def __init__(self):
        """
        スコア表示生成
        """
        global SCORE
        self.font = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 30)
        color = (0,0,255)
        self.img = self.font.render(f"スコア：{SCORE}", 0, color)
        # self.img.set_colorkey((0, 0, 0))
        self.rct = self.img.get_rect()
        self.rct.center = 70,HEIGHT-100, 

    def update(self,screen: pg.Surface):
        """
        スコアを更新
        """
        color = (0,0,255)
        self.img = self.font.render(f"スコア：{SCORE}", 0, color)
        # self.img.set_colorkey((0, 0, 0))
        screen.blit(self.img, self.rct)


class Explosion:
    """
    爆発に関するクラス
    """
    def __init__(self,bomb:Bomb):
        """
        爆発の生成
        """
        img = pg.image.load(f"{MAIN_DIR}/fig/explosion.gif")
        self.imgs = [img,pg.transform.flip(img,True,False)]
        self.index = 0
        self.img = self.imgs[0]
        self.rct = self.img.get_rect()
        self.rct.center = bomb.rct.center
        self.life = 10

    def update(self,screen: pg.Surface):
        """
        爆発の更新
        """
        self.life -= 1
        if self.life <= 0:
            return True
        if self.index < len(self.imgs):
            self.index += 1
        index = self.index%2
        self.img = self.imgs[index]
        screen.blit(self.img,self.rct)
        return False
        

def main():
    global SCORE
    pg.display.set_caption("たたかえ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))    
    bg_img = pg.image.load(f"{MAIN_DIR}/fig/pg_bg.jpg")
    bird = Bird(3, (900, 400))
    # bomb = Bomb((255, 0, 0), 10) 
    bombs = [Bomb() for _ in range(NUM_OF_BOMBS)]
    beams = list()
    score = Score()
    beams.append(None)
    explosions = list()
    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:#スペースキーが押されたとき
                beams.append(Beam(bird))#ビームインスタンスの生成
        screen.blit(bg_img, [0, 0])
        
        for bomb in bombs:
            if bomb:
                if bird.rct.colliderect(bomb.rct):
                    # ゲームオーバー時に，こうかとん画像を切り替え，1秒間表示させる
                    bird.change_img(8, screen)
                    pg.display.update()
                    time.sleep(1)
                    return
        
        for i,bomb in enumerate(bombs):
            for j,beam in enumerate(beams):
                if beam is not None and beam.rct.colliderect(bomb.rct):
                    bird.change_img(6,screen)
                    pg.display.update()
                    time.sleep(1)
                    explosions.append(Explosion(bomb))
                    beams[j] = None
                    bombs[i] = None
                    SCORE += 1
                    score.update(screen)
        bombs = [bomb for bomb in bombs if bomb is not None]
        beams = [beam for beam in beams if beam is not None]
        explosions = [explosion for explosion in explosions if not explosion.update(screen)]

        for i,beam in enumerate(beams):
            yoko,tate = check_bound(beam.rct)
            if yoko == False or tate == False:
                beams[i] = None
        beams = [beam for beam in beams if beam is not None]

        key_lst = pg.key.get_pressed()
        bird.update(key_lst, screen)
        for bomb in bombs:
            if bomb:
                bomb.update(screen)
        for beam in beams:
            if beam:
                beam.update(screen)
        score.update(screen)
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
