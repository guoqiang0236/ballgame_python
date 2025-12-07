import pygame
pygame.init()

screen_width, screen_height = 1440, 810
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Guoqiang game Window")

bsize =256
bcenter = (screen_width // 2 , screen_height // 2 )
scaled_image = pygame.transform.scale(pygame.image.load("pic/whiteball.png"), (bsize, bsize))
image_rect = scaled_image.get_rect(center=bcenter)
running =True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.blit(scaled_image, image_rect)
    pygame.display.flip()

pygame.quit()
