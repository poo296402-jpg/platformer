import pygame
from sys import exit

pygame.init()
screen = pygame.display.set_mode((600,400))
pygame.display.set_caption('Fafas adventure')
clock = pygame.time.Clock()
test_font = pygame.font.Font('Pixeltype.ttf', 50)

sky_surface = pygame.image.load('Sky.png')
ground_surface = pygame.image.load('ground.png')
text_surface = test_font.render('Fafas Adventure', False, 'Green')

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    screen.blit(sky_surface,(0,0))
    screen.blit(ground_surface,(0,300))
    screen.blit(text_surface,(150,50))

    pygame.display.update()
    clock.tick(60)






def load_animation(path, frame_durations):
    global animation_frames
    animation_name = path.split('/')[-1]
    animation_frame_data =[]
    n=0
    for frame in frame_durations:
        animation_frame_id = animation_name + '_' + str(n)
        img_loc = path + '/' + animation_frame_id + '.png' 
        animation_image = pygame.image.load(img_loc).convert_alpha()
        animation_frames[animation_frame_id] = animation_image.copy()
        for i in range(frame):
            animation_frame_data.append(animation_frame_id)
        n += 1
    return animation_frame_data

animation_database = {}
animation_database['idle'] = load_animation('player/idle', [7, 7])