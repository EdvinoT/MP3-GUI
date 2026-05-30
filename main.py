import pygame
import os
import sys

# Initialize Pygame core and audio engines
pygame.init()
pygame.mixer.init()

# Window Setup
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Surreal Media Player")
clock = pygame.time.Clock()

# Setup Paths
DIR_PATH = os.path.dirname(os.path.abspath(__file__))
TRACKS_DIR = os.path.join(DIR_PATH, "tracks")

# Load Background Graphic safely
BACKGROUND_PATH = os.path.join(DIR_PATH, "background.png")
background_loaded = False

if os.path.exists(BACKGROUND_PATH):
    try:
        bg_image = pygame.image.load(BACKGROUND_PATH).convert()
        bg_image = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        background_loaded = True
        print("Hardware Engine Status: background.png successfully bound to hardware acceleration.", flush=True)
    except Exception as e:
        print(f"Hardware Error reading image asset: {e}", flush=True)

if not background_loaded:
    print("System Warning: background.png missing or corrupt. Generating solid fallback canvas.", flush=True)
    bg_image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    bg_image.fill((20, 20, 25))

# Font Layer Configuration
try:
    title_font = pygame.font.SysFont("Arial", 32, bold=True)
    sub_font = pygame.font.SysFont("Arial", 14)
    button_font = pygame.font.SysFont("Futura", 16)
except Exception:
    title_font = pygame.font.Font(None, 36)
    sub_font = pygame.font.Font(None, 18)
    button_font = pygame.font.Font(None, 22)

# Colors
COLOR_TEXT_MAIN = (0, 0, 0)      # Deep Black matching your typography requirements
COLOR_TEXT_SUB = (68, 68, 68)    # Muted Charcoal Gray
COLOR_BTN_DEFAULT = (221, 221, 221)
COLOR_BTN_HOVER = (255, 255, 255)
COLOR_BTN_OFF = (255, 170, 170)
COLOR_BTN_OFF_HOVER = (255, 85, 85)

# Interactive Menu Button Bounds
buttons = [
    {"text": "ACCESS SONGS", "rect": pygame.Rect(260, 210, 280, 45), "type": "access"},
    {"text": "MAKE A PLAYLIST", "rect": pygame.Rect(260, 270, 280, 45), "type": "playlist"},
    {"text": "ADD SONG", "rect": pygame.Rect(260, 330, 280, 45), "type": "add"},
    {"text": "TURN OFF", "rect": pygame.Rect(260, 390, 280, 45), "type": "off"},
    {"text": "◀◀", "rect": pygame.Rect(300, 495, 50, 40), "type": "prev"},
    {"text": "▶", "rect": pygame.Rect(375, 495, 50, 40), "type": "play"},
    {"text": "▶▶", "rect": pygame.Rect(450, 495, 50, 40), "type": "next"}
]

# State Engines
track_list = []
current_track_index = 0
is_playing = False
current_subtext = "▪ ONLINE ▪"

def load_local_tracks():
    global track_list
    if not os.path.exists(TRACKS_DIR):
        os.makedirs(TRACKS_DIR)
    track_list = [f for f in os.listdir(TRACKS_DIR) if f.endswith(".mp3")]
    track_list.sort()
    print(f"Audio Tracks Loaded: {len(track_list)} targets inside /tracks folder", flush=True)

load_local_tracks()

def play_current_track():
    global is_playing, current_subtext
    if not track_list: return
    track_name = track_list[current_track_index]
    track_path = os.path.join(TRACKS_DIR, track_name)
    try:
        pygame.mixer.music.load(track_path)
        pygame.mixer.music.play()
        is_playing = True
        buttons[5]["text"] = "❚❚"  # Toggle play button icon string
        clean_name = track_name.replace(".mp3", "")
        current_subtext = f"▪ PLAYING: {clean_name} ▪"
    except Exception as e:
        print(f"Playback execution error: {e}", flush=True)

# Main Window Application Frame Loop
running = True
while running:
    mouse_pos = pygame.mouse.get_pos()
    
    for event in pygame.event.get_events() if hasattr(pygame.event, 'get_events') else pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Left Click
                for btn in buttons:
                    if btn["rect"].collidepoint(mouse_pos):
                        if btn["type"] == "off":
                            running = False
                        elif btn["type"] == "access":
                            print(f"Storage Index Request: {track_list}", flush=True)
                        elif btn["type"] == "playlist":
                            print("Action Triggered: Initialize playlist layout configuration.", flush=True)
                        elif btn["type"] == "add":
                            print("Action Triggered: Run track downloader engine.", flush=True)
                        elif btn["type"] == "play":
                            if not track_list:
                                print("Storage Alert: No tracks inside /tracks folder.", flush=True)
                            elif is_playing:
                                pygame.mixer.music.pause()
                                is_playing = False
                                btn["text"] = "▶"
                            else:
                                if pygame.mixer.music.get_pos() > 0:
                                    pygame.mixer.music.unpause()
                                else:
                                    play_current_track()
                                is_playing = True
                                btn["text"] = "❚❚"
                        elif btn["type"] == "next":
                            if track_list:
                                current_track_index = (current_track_index + 1) % len(track_list)
                                play_current_track()
                        elif btn["type"] == "prev":
                            if track_list:
                                current_track_index = (current_track_index - 1) % len(track_list)
                                play_current_track()

    # 1. Clear background surface with your original file assets
    screen.blit(bg_image, (0, 0))

    # 2. Render Text Typography Elements
    title_surface = title_font.render("I D L E   S Y S T E M", True, COLOR_TEXT_MAIN)
    title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 95))
    screen.blit(title_surface, title_rect)

    sub_surface = sub_font.render(current_subtext.upper(), True, COLOR_TEXT_SUB)
    sub_rect = sub_surface.get_rect(center=(SCREEN_WIDTH // 2, 145))
    screen.blit(sub_surface, sub_rect)

    # 3. Draw & Track Hover Button Transformations
    for btn in buttons:
        is_hovered = btn["rect"].collidepoint(mouse_pos)
        
        # Determine current interactive color state
        if btn["type"] == "off":
            text_color = COLOR_BTN_OFF_HOVER if is_hovered else COLOR_BTN_OFF
        else:
            text_color = COLOR_BTN_HOVER if is_hovered else COLOR_BTN_DEFAULT
            
        btn_surface = button_font.render(btn["text"], True, text_color)
        btn_rect = btn_surface.get_rect(center=btn["rect"].center)
        screen.blit(btn_surface, btn_rect)

    # Refresh Screen Buffer Matrix
    pygame.display.flip()
    clock.tick(60)

pygame.mixer.quit()
pygame.quit()
sys.exit()