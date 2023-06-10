import pygame
from pygame.locals import *

pygame.init()

screen_width = 1366
screen_height = 768

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Breakout')

pygame.mixer.init()  # initialize the mixer module
pygame.mixer.music.load('Rainbow.mp3')  # load the music file
pygame.mixer.music.play(-1)  # play the music, "-1" means loop indefinitely
pygame.mixer.music.set_volume(0.3)

# Load the sound effects
hit_sound = pygame.mixer.Sound('boing.wav')
break_sound = pygame.mixer.Sound('bump.wav')
break_sound.set_volume(0.8)


#define font
font = pygame.font.SysFont('Constantia', 30)

# MIN KODE
bg = pygame.image.load('bg.png').convert()
pygame.joystick.init()

gamepad = pygame.joystick.Joystick(0)
gamepad.init()
rainbow_colors = [(255, 0, 0), (255, 127, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255), (75, 0, 130), (148, 0, 211)]  # RGB color values of the rainbow colors



# ---

#define colours


#block colours
block_red = (242, 85, 96)
block_green = (86, 174, 87)
block_blue = (69, 177, 232)
#paddle colours
paddle_col = (0, 0, 0)
paddle_outline = (0, 0, 0)
#text colour
text_col = (255, 255, 255)

#define game variables
cols = 6
rows = 6
clock = pygame.time.Clock()
fps = 60
live_ball = False
game_over = 0


#function for outputting text onto the screen
def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))


#brick wall class
class wall():
	def __init__(self):
		self.width = screen_width // cols
		self.height = 50
		# Load the images
		block_blue = pygame.image.load('JBA.png')
		block_green = pygame.image.load('JBB.png')
		block_red = pygame.image.load('JBC.png')
        
        # Scale the images
		self.block_images = [pygame.transform.scale(block_blue, (self.width, self.height)), pygame.transform.scale(block_green, (self.width, self.height)), pygame.transform.scale(block_red, (self.width, self.height))]

	def create_wall(self):
		self.blocks = []
		#define an empty list for an individual block
		block_individual = []
		for row in range(rows):
			#reset the block row list
			block_row = []
			#iterate through each column in that row
			for col in range(cols):
				#generate x and y positions for each block and create a rectangle from that
				block_x = col * self.width
				block_y = row * self.height
				rect = pygame.Rect(block_x, block_y, self.width, self.height)
				#assign block strength based on row
				if row < 2:
					strength = 3
				elif row < 4:
					strength = 2
				elif row < 6:
					strength = 1
				#create a list at this point to store the rect and colour data
				block_individual = [rect, strength]
				#append that individual block to the block row
				block_row.append(block_individual)
			#append the row to the full list of blocks
			self.blocks.append(block_row)


	def draw_wall(self):
		for row in self.blocks:
			for block in row:
				#assign a colour based on block strength
				if block[1] == 3:
					block_img = self.block_images[0]
				elif block[1] == 2:
					block_img = self.block_images[1]
				elif block[1] == 1:
					block_img = self.block_images[2]
				# draw the image on the screen at the block's rect
				screen.blit(block_img, block[0])

#paddle class
class paddle():
    def __init__(self):
        self.reset()

    def move(self):
        #reset movement direction
        self.direction = 0
        pygame.event.pump()
        joystick_x = gamepad.get_axis(0)

        if joystick_x < -0.5 and self.rect.left > 0:
            self.rect.x -= self.speed
            self.direction = -1
        elif joystick_x > 0.5 and self.rect.right < screen_width:
            self.rect.x += self.speed
            self.direction = 1

    def draw(self):
        rainbow_height = self.rect.height // len(rainbow_colors)
        for i, color in enumerate(rainbow_colors):
            pygame.draw.rect(screen, color, (self.rect.x, self.rect.y + i*rainbow_height, self.rect.width, rainbow_height))
        pygame.draw.rect(screen, paddle_outline, self.rect, 3)

    def reset(self):
        self.height = 43
        self.width = int(screen_width / cols)
        self.x = int((screen_width / 2) - (self.width / 2))
        self.y = screen_height - (self.height * 2)
        self.speed = 10
        self.rect = Rect(self.x, self.y, self.width, self.height)
        self.direction = 0



#ball class
class game_ball():
	def __init__(self, x, y):
		self.reset(x, y)
		self.image = pygame.image.load('ball2.png')
		self.image = pygame.transform.scale(self.image, (self.ball_rad * 6, self.ball_rad * 6))
		self.angle = 0

	def move(self):

		#collision threshold
		collision_thresh = 5
		self.angle += 2

		#start off with the assumption that the wall has been destroyed completely
		wall_destroyed = 1
		row_count = 0
		for row in wall.blocks:
			item_count = 0
			for item in row:
				#check collision
				if self.rect.colliderect(item[0]):
					break_sound.play()
					#check if collision was from above
					if abs(self.rect.bottom - item[0].top) < collision_thresh and self.speed_y > 0:
						self.speed_y *= -1
					#check if collision was from below
					if abs(self.rect.top - item[0].bottom) < collision_thresh and self.speed_y < 0:
						self.speed_y *= -1						
					#check if collision was from left
					if abs(self.rect.right - item[0].left) < collision_thresh and self.speed_x > 0:
						self.speed_x *= -1
					#check if collision was from right
					if abs(self.rect.left - item[0].right) < collision_thresh and self.speed_x < 0:
						self.speed_x *= -1
					#reduce the block's strength by doing damage to it
					if wall.blocks[row_count][item_count][1] > 1:
						wall.blocks[row_count][item_count][1] -= 1
					else:
						wall.blocks[row_count][item_count][0] = (0, 0, 0, 0)

				#check if block still exists, in whcih case the wall is not destroyed
				if wall.blocks[row_count][item_count][0] != (0, 0, 0, 0):
					wall_destroyed = 0
				#increase item counter
				item_count += 1
			#increase row counter
			row_count += 1
		#after iterating through all the blocks, check if the wall is destroyed
		if wall_destroyed == 1:
			self.game_over = 1



		#check for collision with walls
		if self.rect.left < 0 or self.rect.right > screen_width:
			self.speed_x *= -1

		#check for collision with top and bottom of the screen
		if self.rect.top < 0:
			self.speed_y *= -1
		if self.rect.bottom > screen_height:
			self.game_over = -1


		#look for collission with paddle
		if self.rect.colliderect(player_paddle):
			hit_sound.play()
			#check if colliding from the top
			if abs(self.rect.bottom - player_paddle.rect.top) < collision_thresh and self.speed_y > 0:
				self.speed_y *= -1
				self.speed_x += player_paddle.direction
				if self.speed_x > self.speed_max:
					self.speed_x = self.speed_max
				elif self.speed_x < 0 and self.speed_x < -self.speed_max:
					self.speed_x = -self.speed_max
			else:
				self.speed_x *= -1



		self.rect.x += self.speed_x
		self.rect.y += self.speed_y

		return self.game_over


	def draw(self):
		rotated_image = pygame.transform.rotate(self.image, self.angle)
		new_rect = rotated_image.get_rect(center = self.rect.center)
		screen.blit(rotated_image, new_rect.topleft)

	def reset(self, x, y):
		self.ball_rad = 10
		self.x = x - self.ball_rad
		self.y = y
		self.rect = Rect(self.x, self.y, self.ball_rad * 6, self.ball_rad * 6)
		self.speed_x = 4
		self.speed_y = -4
		self.speed_max = 5
		self.game_over = 0



#create a wall
wall = wall()
wall.create_wall()

#create paddle
player_paddle = paddle()


#create ball
ball = game_ball(player_paddle.x + (player_paddle.width // 2), player_paddle.y - player_paddle.height)

run = True
while run:

	clock.tick(fps)
	
	screen.blit(bg, (0, 0))

	#draw all objects
	wall.draw_wall()
	player_paddle.draw()
	ball.draw()

	if live_ball:
		#draw paddle
		player_paddle.move()
		#draw ball
		game_over = ball.move()
		if game_over != 0:
			live_ball = False


	#print player instructions
	if not live_ball:
		if game_over == 0:
			draw_text('TRYKK FOR Å STARTE', font, text_col, screen_width // 2, screen_height // 2)
		elif game_over == 1:
			draw_text('DU VANT!', font, text_col, 240, screen_height // 2 + 50)
			draw_text('TRYKK FOR Å STARTE', font, text_col, screen_width // 2, screen_height // 2)
		elif game_over == -1:
			draw_text('DU TAPTE!', font, text_col, 240, screen_height // 2 + 50)
			draw_text('TRYKK FOR Å STARTE', font, text_col, screen_width // 2, screen_height // 2)


	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False
		if event.type == pygame.JOYBUTTONDOWN and live_ball == False:
			live_ball = True
			ball.reset(player_paddle.x + (player_paddle.width // 2), player_paddle.y - player_paddle.height)
			player_paddle.reset()
			wall.create_wall()



	pygame.display.update()

pygame.quit()