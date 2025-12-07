import pygame
import random
pygame.init()

screen_width, screen_height = 1440, 810
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Guoqiang game")

bsize = 256
balls = []
bcenter = (screen_width // 2, screen_height // 2)
scaled_image = pygame.transform.scale(pygame.image.load("pic/whiteball.png"), (bsize, bsize))
image_rect = scaled_image.get_rect(center=bcenter)

ghost_ball = None
scale_speed = 6
min_ghost_size = 30
max_ghost_size = 150

running = True
clock = pygame.time.Clock()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            click_x, click_y = event.pos
            ghost_ball ={
                'pos': (click_x, click_y),
                'current_size': min_ghost_size,
                'scale_dir': 1
            }
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and ghost_ball is not None:
            click_x, click_y = event.pos
            final_size = ghost_ball['current_size']
            final_ball_image = pygame.transform.scale(scaled_image, (final_size, final_size))
            new_ball_rect = final_ball_image.get_rect(center=(click_x, click_y))
            new_ball_speed = [0,0]
            while new_ball_speed == [0,0]:
                new_ball_speed = [random.randint(-30, 30), random.randint(-30, 30)]
            balls.append({
                'image': final_ball_image,
                'rect': new_ball_rect,
                'speed': new_ball_speed
            })
            ghost_ball = None
            
    screen.fill((0, 0, 0))
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
    
    
    for ball in balls:
        ball_rect = ball['rect']
        ball_speed = ball['speed']
        ball_rect.x += ball_speed[0]
        ball_rect.y += ball_speed[1]
        
        # 边界检测和反弹
        if ball_rect.bottom >= screen_height:
            ball_speed[1] = -ball_speed[1]
            ball_rect.bottom = screen_height
        if ball_rect.right >= screen_width:
            ball_speed[0] = -ball_speed[0]
            ball_rect.right = screen_width
        if ball_rect.left <= 0:
            ball_speed[0] = -ball_speed[0]
            ball_rect.left = 0
        if ball_rect.top <= 0:
            ball_speed[1] = -ball_speed[1]
            ball_rect.top = 0
        
        screen.blit(ball['image'], ball_rect)
    
    pygame.display.flip()
    clock.tick(60)
pygame.quit()