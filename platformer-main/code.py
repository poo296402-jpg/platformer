import pygame, sys  
from pygame.locals import * 
pygame.mixer.pre_init(44100,-16, 2, 512)
pygame.init()  
pygame.mixer.set_num_channels(64)
clock = pygame.time.Clock()  
pygame.display.set_caption("platformer")

WINDOW_SIZE = (1200,600)  
screen = pygame.display.set_mode(WINDOW_SIZE, 0, 32)
display = pygame.Surface((1200,600 ))
#text_surface = test_font.render('Fafas Adventure', False, 'Green')
RENDER_SCALE = 2 # Scale factor for rendering
PLAYER_SIZE = (50, 50)  # Visual sprite size

# Make sure "FAFA.png" is in the same folder as this script
# Load with alpha so the black background around the sprite is transparent,
# while the black eye pixels remain visible.

fafa_image = pygame.image.load("fafa2.png").convert_alpha()
player_rect = fafa_image.get_rect()

dirt_image = pygame.image.load("dirt.png")
grass_image = pygame.image.load("grass.png")
TILE_SIZE =grass_image.get_width()
dirt_render = pygame.transform.scale2x(dirt_image)
grass_render = pygame.transform.scale2x(grass_image)
jump_sound = pygame.mixer.Sound('grass-jump.wav')
grass_sound = pygame.mixer.Sound('grass-walking.wav')

grass_sound.set_volume(1)
jump_sound.set_volume(0.1)
pygame.mixer.music.set_volume(0.3)

pygame.mixer.music.load('Pufino-Chillout(freetouse.com).wav')
pygame.mixer.music.play(-1)
 
def make_looping_layer(image_path):
    image = pygame.image.load(image_path).convert_alpha()
    image = pygame.transform.scale(image, WINDOW_SIZE)
    mirrored_image = pygame.transform.flip(image, True, False)
    looping_image = pygame.Surface(
        (image.get_width() * 2, image.get_height()), pygame.SRCALPHA
    )
    looping_image.blit(image, (0, 0))
    looping_image.blit(mirrored_image, (image.get_width(), 0))
    return looping_image


background_render = make_looping_layer("layer1.jpeg")

def check_collision(rect, tiles):
    for tile in tiles:
        if rect.colliderect(tile):
            return True
    return False


def load_map(path):
    with open(path + '.txt', 'r') as map_file:
        return [list(row) for row in map_file.read().splitlines()]


global animation_frames
animation_frames = {}

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
        for _ in range(frame):
            animation_frame_data.append(animation_frame_id)
        n += 1
    return animation_frame_data

def change_action(action_var, frame, new_value):
    if action_var != new_value:
        action_var = new_value
        frame = 0
    return action_var, frame


animation_database = {}
animation_database['FafaWalking'] = load_animation('Fafa/FafaWalking', [4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4])
animation_database['FafaIdle'] = load_animation('Fafa/FafaIdle', [5])

player_action = 'FafaIdle'
player_frame = 0
player_flip = False

grass_sound_timer = 0

background_objects = [
    (0.12, make_looping_layer("layer3.png")),
    (0.3, make_looping_layer("layer2.png")),
]

def collision_test(rect, tiles):
    collision_list = []
    for tile in tiles:
        if rect.colliderect(tile):
            collision_list.append(tile)
    return collision_list


def move(rect, movement, tiles):
    global player_y_momentum
    # Resolve horizontal and vertical movement separately so the player can
    # slide along platforms without passing through them.
    collision_types = {'top': False, 'bottom': False, 'right': False, 'left': False}
    rect.x += movement[0]
    collision_list = collision_test(rect, tiles)
    for tile in collision_list:
        if movement[0] > 0:
            rect.right = tile.left
            collision_types['right'] = True
        elif movement[0] < 0:
            rect.left = tile.right
            collision_types['left'] = True

    rect.y += movement[1]
    collision_list = collision_test(rect, tiles)
    for tile in collision_list:  
        if movement[1] > 0:
            rect.bottom = tile.top
            collision_types['bottom'] = True
        elif movement[1] < 0:
            rect.top = tile.bottom
            collision_types['top'] = True
    return rect, collision_types


moving_right = False 
moving_left = False  

scroll = [0, 0]

player_location = [50, 50]
player_y_momentum = 0
air_timer = 0

player_rect = pygame.Rect(
    50, 50,
    PLAYER_SIZE[0]//1.5,
    PLAYER_SIZE[1]//1.5
)

game_map = load_map('map')

while True:
    if grass_sound_timer > 0:
         grass_sound_timer -= 1 
    
    # 1. Clear the screen with a background color
    # Center the camera on the player; positions and collisions remain in world units.
    scroll[0] = player_rect.centerx - display.get_width() // (2 * RENDER_SCALE)
    scroll[1] = player_rect.centery - display.get_height() // (2 * RENDER_SCALE)

    background_offset = -int(scroll[0] * RENDER_SCALE * 0.05) % background_render.get_width()
    for x in range(background_offset - background_render.get_width(),
                   display.get_width(), background_render.get_width()):
        display.blit(background_render, (x, 0))

    for speed, background_image in background_objects:
        offset_x = -int(scroll[0] * RENDER_SCALE * speed) % background_image.get_width()
        for x in range(offset_x - background_image.get_width(),
                       display.get_width(), background_image.get_width()):
            display.blit(background_image, (x, 0))

    title_rects = []
    y = 0
    for row in game_map:
        x = 0
        for tile in row:
            if tile == '2':
                display.blit(grass_render, (x * TILE_SIZE * RENDER_SCALE - scroll[0] * RENDER_SCALE,
                                            y * TILE_SIZE * RENDER_SCALE - scroll[1] * RENDER_SCALE))
            if tile == '1':
                display.blit(dirt_render, (x * TILE_SIZE * RENDER_SCALE - scroll[0] * RENDER_SCALE,
                                           y * TILE_SIZE * RENDER_SCALE - scroll[1] * RENDER_SCALE))
            if tile in ('1', '2'):
                tile_rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                title_rects.append(tile_rect)
            x += 1
        y += 1

    player_movement = [0, 0]
   
    if moving_right:
        player_movement[0] += 2
    if moving_left:
        player_movement[0] -= 2
    player_movement[1] += player_y_momentum
    player_y_momentum += 0.2
    if player_y_momentum > 3:
        player_y_momentum = 3

    if player_movement[0] > 0:
        player_action, player_frame = change_action(player_action, player_frame, 'FafaWalking')
        player_flip = False
    elif player_movement[0] < 0:
        player_action, player_frame = change_action(player_action, player_frame, 'FafaWalking')
        player_flip = True
    else:
        player_action, player_frame = change_action(player_action, player_frame, 'FafaIdle')

    player_rect, collision_types = move(player_rect, player_movement, title_rects)
   
    if collision_types['bottom'] == True:
        player_y_momentum = 0
        air_timer = 0
        if player_movement[0] != 0:
            if grass_sound_timer == 0:
                grass_sound_timer = 20
                grass_sound.play()
    else:
        air_timer += 1 
 
    player_frame += 1
    if player_frame >= len(animation_database[player_action]):
        player_frame = 0
    player_img_id = animation_database[player_action][player_frame]
    player_img = animation_frames[player_img_id]
    display.blit(pygame.transform.flip(player_img, player_flip, False),
                 ((player_rect.x - scroll[0]) * RENDER_SCALE,
                  (player_rect.y - scroll[1]) * RENDER_SCALE ))

    # 4. Handle events
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()    
        if event.type == KEYDOWN: 
            if event.key == K_w:
                pygame.mixer.music.fadeout(2000)
            if event.key == K_e:
                pygame.mixer.music.play(-1)
            if event.key == K_RIGHT:
                moving_right = True
            if event.key == K_LEFT:
                moving_left = True
            if event.key == K_UP:
                if air_timer < 6:
                    jump_sound.play()
                    player_y_momentum = -5
        if event.type == KEYUP:
            if event.key == K_RIGHT:
                moving_right = False
            if event.key == K_LEFT:
                moving_left = False
    
    # 5. Update display and lock framerate
    surf = pygame.transform.scale(display, WINDOW_SIZE)
    screen.blit(surf, (0, 0))
    pygame.display.update()
    clock.tick(60)
