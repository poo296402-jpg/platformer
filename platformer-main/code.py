
import pygame, sys  
from pygame.locals import * 

pygame.init()  
clock = pygame.time.Clock()  
pygame.display.set_caption("platformer")

WINDOW_SIZE = (600, 400)  
screen = pygame.display.set_mode(WINDOW_SIZE, 0, 32)
display = pygame.Surface(WINDOW_SIZE)
RENDER_SCALE = 2

# Make sure "coocoo.png" is in the same folder as this script
player_image = pygame.image.load("coocoo.png").convert()
player_image.set_colorkey((0, 0, 0))  # Make the black background transparent
player_render = pygame.transform.scale2x(player_image)

dirt_image = pygame.image.load("dirt.png")
grass_image = pygame.image.load("grass.png")
dirt_render = pygame.transform.scale2x(dirt_image)
grass_render = pygame.transform.scale2x(grass_image)

background_image = pygame.image.load("background.jpg").convert()
background_render = pygame.transform.scale(background_image, WINDOW_SIZE)

def check_collision(rect, tiles):
    for tile in tiles:
        if rect.colliderect(tile):
            return True
    return False


def load_map(path):
    with open(path + '.txt', 'r') as map_file:
        return [list(row) for row in map_file.read().splitlines()]


def move(rect, movement, tiles):
    global player_y_momentum

    # Resolve horizontal and vertical movement separately so the player can
    # slide along platforms without passing through them.
    rect.x += movement[0]
    for tile in tiles:
        if rect.colliderect(tile):
            if movement[0] > 0:
                rect.right = tile.left
            elif movement[0] < 0:
                rect.left = tile.right

    rect.y += movement[1]
    for tile in tiles:
        if rect.colliderect(tile):
            if movement[1] > 0:
                rect.bottom = tile.top
            elif movement[1] < 0:
                rect.top = tile.bottom
            player_y_momentum = 0

    return rect

moving_right = False 
moving_left = False  

scroll = [0, 0]

player_location = [50, 50]
player_y_momentum = 0

player_rect = pygame.Rect(50, 50, player_image.get_width(), player_image.get_height())
game_map = load_map('map')

while True:      
    # 1. Clear the screen with a background color
    display.blit(background_render, (0, 0))

    # Center the camera on the player; positions and collisions remain in world units.
    scroll[0] = player_rect.centerx - display.get_width() // (2 * RENDER_SCALE)
    scroll[1] = player_rect.centery - display.get_height() // (2 * RENDER_SCALE)
    

    title_rects = []
    y = 0
    for row in game_map:
        x = 0
        for tile in row:
            if tile == '2':
                display.blit(grass_render, (x * 16 * RENDER_SCALE - scroll[0] * RENDER_SCALE,
                                            y * 16 * RENDER_SCALE - scroll[1] * RENDER_SCALE))
            if tile == '1':
                display.blit(dirt_render, (x * 16 * RENDER_SCALE - scroll[0] * RENDER_SCALE,
                                           y * 16 * RENDER_SCALE - scroll[1] * RENDER_SCALE))
            if tile in ('1', '2'):
                tile_rect = pygame.Rect(x * 16, y * 16, 16, 16)
                title_rects.append(tile_rect)
            x += 1
        y += 1
        
   
    

    player_movement = [0,0]
    if moving_right:
        player_movement[0] += 2
    if moving_left: 
        player_movement[0] -= 2
    player_movement[1] += player_y_momentum
    player_y_momentum += 0.2
    if player_y_momentum > 3:
        player_y_momentum = 3

    player_rect = move(player_rect, player_movement, title_rects)
    
    display.blit(player_render, ((player_rect.x - scroll[0]) * RENDER_SCALE,
                                 (player_rect.y - scroll[1]) * RENDER_SCALE))
                                                                    

    # 3. Draw game elements
    # FIXED: Replaced player_location with player_rect to keep drawing accurate to collisions


          
    # 4. Handle events
    for event in pygame.event.get():         
        if event.type == QUIT:             
            pygame.quit()            
            sys.exit()            
            
        if event.type == KEYDOWN:               
            if event.key == K_RIGHT:                   
                moving_right = True               
            if event.key == K_LEFT:                   
                moving_left = True            
            if event.key == K_UP:
                player_y_momentum = -5  # Adjust jump strength as needed    
        if event.type == KEYUP:               
            if event.key == K_RIGHT:                   
                moving_right = False               
            if event.key == K_LEFT:                   
                moving_left = False                           
                
    # 5. Update display and lock framerate
    screen.blit(display, (0, 0))
    pygame.display.update()     
    clock.tick(60)
