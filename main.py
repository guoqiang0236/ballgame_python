import pygame
import random
import math
pygame.init()

screen_width, screen_height = 1440, 810
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Guoqiang game")

bsize = 256
balls = []
float_texts = []
font = pygame.font.Font(None, 32)
bcenter = (screen_width // 2, screen_height // 2)
scaled_image = pygame.transform.scale(pygame.image.load("pic/whiteball.png"), (bsize, bsize))
gameback = pygame.transform.scale(pygame.image.load("pic/gameback.png"), (screen_width, screen_height))

# 加载彩色球图片
cbsize = 64
colorball_images = [None]  # 索引0留空
for i in range(1, 10):
    cimage = pygame.transform.scale(pygame.image.load(f'pic/scoreball/{i}.png'), (cbsize, cbsize))
    colorball_images.append(cimage)

gamearea = {
    'left': 70,
    'top': 180,   
    'right': 1088,
    'bottom': 747
}
image_rect = scaled_image.get_rect(center=bcenter)

ghost_ball = None
scale_speed = 6
min_ghost_size = 30
max_ghost_size = 150

total_score = 0
max_progress = 10000
progress_bar = {
    'x': 40,
    'y': 40,
    'width': 1300,
    'height': 30,
    'border_color': (255, 255, 255),
    'bg_color': (50, 50, 50),
    'fill_color': (0, 255, 128)
}

running = True
clock = pygame.time.Clock()

def check_ball_collision(ball1, ball2):
    """检测两个球是否碰撞"""
    rect1 = ball1['rect']
    rect2 = ball2['rect']
    
    # 计算两个球心的距离
    dx = rect1.centerx - rect2.centerx
    dy = rect1.centery - rect2.centery
    distance = math.sqrt(dx * dx + dy * dy)
    
    # 获取两个球的半径
    radius1 = rect1.width / 2
    radius2 = rect2.width / 2
    
    return distance < (radius1 + radius2)

# 根据分数获取颜色
def get_score_color(score):
    score = max(1, min(9, score))
    ratio = (score - 1) / 8
    if ratio < 0.2:
        r = int(100 + 100 * ratio * 5)
        g = int(150 + 50 * ratio * 5)
        b = 255
    elif ratio < 0.4:
        r = int(200 - 100 * (ratio - 0.2) * 5)
        g = 255
        b = int(255 - 150 * (ratio - 0.2) * 5)
    elif ratio < 0.6:
        r = int(100 + 100 * (ratio - 0.4) * 5)
        g = 255
        b = int(100 - 100 * (ratio - 0.4) * 5)
    elif ratio < 0.8:
        r = 255
        g = int(255 - 100 * (ratio - 0.6) * 5)
        b = int(50 + 50 * (ratio - 0.6) * 5)
    else:
        r = 255
        g = int(150 - 100 * (ratio - 0.8) * 5)
        b = int(100 - 100 * (ratio - 0.8) * 5)
    return (r, g, b)

def draw_progress():
    """绘制进度条"""
    global total_score
    current_progress = min(total_score, max_progress)
    fill_width = (current_progress / max_progress) * progress_bar['width']
    
    # 绘制背景
    pygame.draw.rect(screen, progress_bar['bg_color'], (
        progress_bar['x'],
        progress_bar['y'],
        progress_bar['width'],
        progress_bar['height']
    ))
    
    # 绘制填充
    pygame.draw.rect(screen, progress_bar['fill_color'], (
        progress_bar['x'],
        progress_bar['y'],
        fill_width,
        progress_bar['height']
    ))
    
    # 绘制边框
    pygame.draw.rect(screen, progress_bar['border_color'], (
        progress_bar['x'],
        progress_bar['y'],
        progress_bar['width'],
        progress_bar['height']
    ), 3)
    
    # 绘制分数文字
    score_text = font.render(f"Score: {total_score} / {max_progress}", True, (255, 255, 255))
    screen.blit(score_text, (progress_bar['x'] + 10, progress_bar['y'] + 5))

def handle_ball_collision(ball1, ball2):
    """处理两个球的碰撞反弹"""
    global total_score
    
    rect1 = ball1['rect']
    rect2 = ball2['rect']
    speed1 = ball1['speed']
    speed2 = ball2['speed']
    
    # 计算碰撞方向
    dx = rect2.centerx - rect1.centerx
    dy = rect2.centery - rect1.centery
    distance = math.sqrt(dx * dx + dy * dy)
    
    if distance == 0:
        return
    
    # 归一化碰撞方向
    nx = dx / distance
    ny = dy / distance
    
    # 计算切线方向（垂直于碰撞方向）
    tx = -ny
    ty = nx
    
    # 将速度投影到法线和切线方向
    v1n = speed1[0] * nx + speed1[1] * ny
    v1t = speed1[0] * tx + speed1[1] * ty
    v2n = speed2[0] * nx + speed2[1] * ny
    v2t = speed2[0] * tx + speed2[1] * ty
    
    # 交换法线方向的速度（完全弹性碰撞，质量相等）
    v1n, v2n = v2n, v1n
    
    # 切线方向速度保持不变，重新组合速度向量
    speed1[0] = v1n * nx + v1t * tx
    speed1[1] = v1n * ny + v1t * ty
    speed2[0] = v2n * nx + v2t * tx
    speed2[1] = v2n * ny + v2t * ty
    
    # 分离重叠的球
    radius1 = rect1.width / 2
    radius2 = rect2.width / 2
    overlap = (radius1 + radius2) - distance
    if overlap > 0:
        separation = overlap / 2
        rect1.centerx -= int(separation * nx)
        rect1.centery -= int(separation * ny)
        rect2.centerx += int(separation * nx)
        rect2.centery += int(separation * ny)
    
    # 碰撞得分逻辑
    if ball1['type'] == 0 or ball2['type'] == 0:
        score = ball1['type'] + ball2['type']
        if score != 0:
            # 更新总分
            total_score += score
            
            x1, y1 = rect1.centerx, rect1.centery
            x2, y2 = rect2.centerx, rect2.centery
            text_x = (x1 + x2) // 2
            text_y = (y1 + y2) // 2
            text_color = get_score_color(score)
            text_surface = font.render(f"+{score}", True, text_color)
            shadow_surface = font.render(f"+{score}", True, (0, 0, 0))
            float_texts.append({
                'shadow': shadow_surface,
                'text': text_surface,
                'x': text_x,
                'y': text_y,
                'alpha': 255,
                'life': 60
            })

#加入彩色球
for i in range(1,10):
    img = colorball_images[i]
    # 随机生成游戏区域内的位置
    random_x = random.randint(gamearea['left'] + cbsize//2, gamearea['right'] - cbsize//2)
    random_y = random.randint(gamearea['top'] + cbsize//2, gamearea['bottom'] - cbsize//2)
    ball_rect = img.get_rect(center=(random_x, random_y))
    
    # 随机初始速度
    random_speed = [random.randint(-20, 20), random.randint(-20, 20)]
    while random_speed == [0, 0]:
        random_speed = [random.randint(-20, 20), random.randint(-20, 20)]
    
    balls.append({
        'image': img,   
        'rect': ball_rect,
        'speed': random_speed,
        'type': i
    })

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            click_x, click_y = event.pos
            ghost_ball = {
                'pos': (click_x, click_y),
                'current_size': min_ghost_size,
                'scale_dir': 1
            }
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and ghost_ball is not None:
            click_x, click_y = event.pos
            final_size = ghost_ball['current_size']
            final_ball_image = pygame.transform.scale(scaled_image, (final_size, final_size))
            new_ball_rect = final_ball_image.get_rect(center=(click_x, click_y))
            new_ball_speed = [0, 0]
            while new_ball_speed == [0, 0]:
                new_ball_speed = [random.randint(-30, 30), random.randint(-30, 30)]
            balls.append({
                'image': final_ball_image,
                'rect': new_ball_rect,
                'speed': new_ball_speed,
                'type': 0
            })
            ghost_ball = None

    screen.fill((0, 0, 0))
    screen.blit(gameback, gameback.get_rect())
    
    # 幽灵球逻辑
    if ghost_ball is not None:
        current_size = ghost_ball['current_size'] + ghost_ball['scale_dir'] * scale_speed
        if current_size >= max_ghost_size:
            current_size = max_ghost_size
            ghost_ball['scale_dir'] = -1
        elif current_size <= min_ghost_size:
            current_size = min_ghost_size
            ghost_ball['scale_dir'] = 1
        ghost_ball['current_size'] = current_size
        
        ghost_surface = pygame.transform.scale(scaled_image, (int(current_size), int(current_size)))
        ghost_surface.set_alpha(128)
        ghost_rect = ghost_surface.get_rect(center=ghost_ball['pos'])
        screen.blit(ghost_surface, ghost_rect)  
    
    # 更新球的位置
    for ball in balls:
        ball_rect = ball['rect']
        ball_speed = ball['speed']
        ball_rect.x += ball_speed[0]
        ball_rect.y += ball_speed[1]
        
        # 边界检测和反弹 - 使用游戏区域边界
        if ball_rect.bottom >= gamearea['bottom']:
            ball_speed[1] = -ball_speed[1]
            ball_rect.bottom = gamearea['bottom']
        if ball_rect.right >= gamearea['right']:
            ball_speed[0] = -ball_speed[0]
            ball_rect.right = gamearea['right']
        if ball_rect.left <= gamearea['left']:
            ball_speed[0] = -ball_speed[0]
            ball_rect.left = gamearea['left']
        if ball_rect.top <= gamearea['top']:
            ball_speed[1] = -ball_speed[1]
            ball_rect.top = gamearea['top']
    
    # 检测球与球之间的碰撞
    for i in range(len(balls)):
        for j in range(i + 1, len(balls)):
            if check_ball_collision(balls[i], balls[j]):
                handle_ball_collision(balls[i], balls[j])
    
    # 更新浮动文字
    for text in float_texts[:]:
        text['y'] -= 2
        text['life'] -= 1
        text['alpha'] = max(0, int(255 * (text['life'] / 60)))
        if text['life'] <= 0:
            float_texts.remove(text)
    
    # 绘制所有球
    for ball in balls:
        screen.blit(ball['image'], ball['rect'])
    
    # 绘制浮动文字
    for text in float_texts:
        shadow = text['shadow'].copy()
        shadow.set_alpha(text['alpha'])
        screen.blit(shadow, (text['x'] + 2, text['y'] + 2))
        
        text_surf = text['text'].copy()
        text_surf.set_alpha(text['alpha'])
        screen.blit(text_surf, (text['x'], text['y']))
    
    # 绘制进度条
    draw_progress()
    
    pygame.display.flip()
    clock.tick(60)
pygame.quit()