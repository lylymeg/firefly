import pygame
import random
import math
import sys

pygame.init()

# Dimensions de la fenêtre
WIDTH, HEIGHT = 950, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cozy Terrarium & Fireflies Simulator")
clock = pygame.time.Clock()

# Couleurs (Thème Nuit Cosy & Nature Lumineuse)
BG_COLOR = (14, 18, 30)
TABLE_COLOR = (26, 24, 38)
GLASS_OUTLINE = (165, 215, 235)
CORK_COLOR = (168, 118, 78)
CORK_DARK = (132, 88, 56)
SOIL_DARK = (46, 34, 32)
SOIL_LIGHT = (68, 48, 42)
MOSS_GREEN = (62, 152, 92)
MOSS_LIGHT = (102, 198, 124)
FIREFLY_GLOW = (255, 232, 115)
MIST_BLUE = (155, 225, 255)
TEXT_COLOR = (242, 246, 255)
GRAY = (132, 144, 168)

# Polices
font_medium = pygame.font.SysFont("Arial", 20, bold=True)
font_small = pygame.font.SysFont("Arial", 14)

class Firefly:
    def __init__(self, bounds):
        self.bounds = bounds  # (left, top, right, bottom)
        self.x = random.uniform(bounds[0] + 25, bounds[2] - 25)
        self.y = random.uniform(bounds[1] + 35, bounds[3] - 45)
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(0.5, 1.1)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.pulse_phase = random.uniform(0, math.pi * 2)
        self.pulse_speed = random.uniform(0.05, 0.09)

    def update(self, mouse_pos):
        self.pulse_phase += self.pulse_speed
        # Légère dérive aléatoire organique
        self.vx += random.uniform(-0.06, 0.06)
        self.vy += random.uniform(-0.06, 0.06)

        # Attraction douce vers le curseur s'il est proche du bocal
        if mouse_pos[1] > 80:
            dx = mouse_pos[0] - self.x
            dy = mouse_pos[1] - self.y
            dist = math.hypot(dx, dy)
            if 15 < dist < 160:
                self.vx += (dx / dist) * 0.035
                self.vy += (dy / dist) * 0.035

        # Limiter la vitesse
        speed = math.hypot(self.vx, self.vy)
        if speed > 1.4:
            self.vx = (self.vx / speed) * 1.4
            self.vy = (self.vy / speed) * 1.4

        self.x += self.vx
        self.y += self.vy

        # Rester à l'intérieur des parois du bocal
        left, top, right, bottom = self.bounds
        if self.x < left + 20:
            self.x = left + 20
            self.vx = abs(self.vx)
        elif self.x > right - 20:
            self.x = right - 20
            self.vx = -abs(self.vx)

        if self.y < top + 25:
            self.y = top + 25
            self.vy = abs(self.vy)
        elif self.y > bottom - 20:
            self.y = bottom - 20
            self.vy = -abs(self.vy)

    def draw(self, surface):
        glow_factor = 0.5 + 0.5 * math.sin(self.pulse_phase)
        halo_radius = int(9 + glow_factor * 7)
        alpha = int(45 + glow_factor * 75)

        halo_surf = pygame.Surface((halo_radius * 2, halo_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(halo_surf, (*FIREFLY_GLOW, alpha), (halo_radius, halo_radius), halo_radius)
        surface.blit(halo_surf, (int(self.x) - halo_radius, int(self.y) - halo_radius))

        pygame.draw.circle(surface, (255, 252, 210), (int(self.x), int(self.y)), 2)

class MistDrop:
    def __init__(self, x, y, floor_y):
        self.x = float(x)
        self.y = float(y)
        self.vx = random.uniform(-0.8, 0.8)
        self.vy = random.uniform(0.8, 2.2)
        self.floor_y = floor_y
        self.life = random.randint(55, 95)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.97
        self.life -= 1
        if self.y >= self.floor_y:
            self.y = self.floor_y
            self.vy = 0

    def draw(self, surface):
        pygame.draw.circle(surface, MIST_BLUE, (int(self.x), int(self.y)), 2)

class FernPlant:
    def __init__(self, x, base_y, height, color):
        self.x = x
        self.base_y = base_y
        self.height = height
        self.color = color
        self.sway_phase = random.uniform(0, math.pi * 2)
        self.sparkle_timer = 0

    def update(self):
        self.sway_phase += 0.035
        if self.sparkle_timer > 0:
            self.sparkle_timer -= 1

    def draw(self, surface):
        sway = math.sin(self.sway_phase) * 5
        tip_x = self.x + sway
        tip_y = self.base_y - self.height

        # Tige principale courbée
        pygame.draw.line(surface, self.color, (self.x, self.base_y), (int(tip_x), int(tip_y)), 3)

        # Petites feuilles le long de la tige
        steps = 5
        for i in range(1, steps + 1):
            t = i / (steps + 1)
            lx = self.x + sway * t
            ly = self.base_y - self.height * t
            leaf_len = (1.1 - t * 0.5) * 11
            pygame.draw.ellipse(surface, self.color, (int(lx - leaf_len), int(ly - 3), int(leaf_len), 6))
            pygame.draw.ellipse(surface, self.color, (int(lx), int(ly - 3), int(leaf_len), 6))

        # Petit éclat lorsqu'elle vient d'être arrosée
        if self.sparkle_timer > 0:
            pygame.draw.circle(surface, (220, 255, 240), (int(tip_x), int(tip_y - 6)), 3)

# Géométrie du terrarium (bocal central)
jar_w, jar_h = 340, 390
jar_left = WIDTH // 2 - jar_w // 2
jar_right = WIDTH // 2 + jar_w // 2
jar_top = 135
jar_bottom = jar_top + jar_h
soil_top = jar_bottom - 88
air_bounds = (jar_left, jar_top + 25, jar_right, soil_top)

# Éléments de l'écosystème
fireflies = [Firefly(air_bounds) for _ in range(14)]
mist_drops = []
ferns = [
    FernPlant(WIDTH // 2 - 85, soil_top + 4, 82, MOSS_GREEN),
    FernPlant(WIDTH // 2 - 20, soil_top + 2, 108, MOSS_LIGHT),
    FernPlant(WIDTH // 2 + 55, soil_top + 5, 74, MOSS_GREEN),
    FernPlant(WIDTH // 2 + 105, soil_top + 6, 56, MOSS_LIGHT),
]

# Petits galets et champignons décoratifs
pebbles = [
    (WIDTH // 2 - 115, soil_top + 8, 16, 9, (115, 125, 140)),
    (WIDTH // 2 + 22, soil_top + 9, 20, 10, (135, 145, 160)),
    (WIDTH // 2 + 80, soil_top + 10, 14, 8, (105, 115, 130)),
]

running = True
while running:
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and mouse_pos[1] > 80:
                # Vaporiser de la brume fraîche dans le bocal
                spawn_x = max(jar_left + 35, min(jar_right - 35, mouse_pos[0]))
                spawn_y = max(jar_top + 35, min(soil_top - 30, mouse_pos[1]))
                for _ in range(16):
                    mist_drops.append(MistDrop(spawn_x + random.randint(-28, 28), spawn_y + random.randint(-12, 12), soil_top))
                for fern in ferns:
                    fern.sparkle_timer = 35

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                if len(fireflies) < 30:
                    fireflies.append(Firefly(air_bounds))
            elif event.key == pygame.K_r:
                fireflies = [Firefly(air_bounds) for _ in range(14)]
                mist_drops = []

    # Mises à jour
    for ff in fireflies:
        ff.update(mouse_pos)

    for fern in ferns:
        fern.update()

    for drop in mist_drops[:]:
        drop.update()
        if drop.life <= 0:
            mist_drops.remove(drop)

    # --- RENDU GRAPHIQUE ---
    screen.fill(BG_COLOR)

    # Table en bois sombre en bas
    pygame.draw.rect(screen, TABLE_COLOR, (0, jar_bottom - 12, WIDTH, HEIGHT - (jar_bottom - 12)))
    pygame.draw.line(screen, (52, 48, 72), (0, jar_bottom - 12), (WIDTH, jar_bottom - 12), 2)

    # Fond intérieur du bocal (verre teinté doux)
    jar_rect = pygame.Rect(jar_left, jar_top, jar_w, jar_h)
    pygame.draw.rect(screen, (20, 28, 44), jar_rect, border_radius=55)

    # Couches de terre et de mousse au fond du bocal
    soil_rect = pygame.Rect(jar_left + 6, soil_top, jar_w - 12, jar_bottom - soil_top - 6)
    pygame.draw.rect(screen, SOIL_DARK, soil_rect, border_bottom_left_radius=48, border_bottom_right_radius=48)
    pygame.draw.rect(screen, SOIL_LIGHT, (jar_left + 8, soil_top, jar_w - 16, 26), border_radius=10)
    pygame.draw.rect(screen, MOSS_GREEN, (jar_left + 12, soil_top - 4, jar_w - 24, 14), border_radius=8)

    # Galets et petits champignons lumineux
    for px, py, pw, ph, pcol in pebbles:
        pygame.draw.ellipse(screen, pcol, (px, py, pw, ph))

    for mx, my in [(WIDTH // 2 - 48, soil_top), (WIDTH // 2 - 36, soil_top + 2)]:
        pygame.draw.rect(screen, (235, 230, 225), (mx - 2, my - 10, 4, 10))
        pygame.draw.ellipse(screen, (255, 145, 185), (mx - 7, my - 15, 14, 8))

    # Fougères ondulantes
    for fern in ferns:
        fern.draw(screen)

    # Gouttelettes de brume
    for drop in mist_drops:
        drop.draw(screen)

    # Lucioles dorées
    for ff in fireflies:
        ff.draw(screen)

    # Paroi en verre & reflets lumineux
    pygame.draw.rect(screen, GLASS_OUTLINE, jar_rect, 3, border_radius=55)
    pygame.draw.line(screen, (220, 245, 255), (jar_left + 22, jar_top + 55), (jar_left + 22, jar_bottom - 65), 3)
    pygame.draw.line(screen, (180, 220, 240), (jar_left + 32, jar_top + 70), (jar_left + 32, jar_top + 145), 2)

    # Bouchon en liège sur le dessus du bocal
    cork_w = 170
    cork_x = WIDTH // 2 - cork_w // 2
    pygame.draw.rect(screen, CORK_DARK, (cork_x + 8, jar_top - 12, cork_w - 16, 22), border_radius=6)
    pygame.draw.rect(screen, CORK_COLOR, (cork_x, jar_top - 26, cork_w, 20), border_radius=8)

    # --- HUD ET INSTRUCTIONS ---
    title_txt = font_medium.render("COZY TERRARIUM — MINI-ÉCOSYSTÈME & LUCIOLES", True, TEXT_COLOR)
    screen.blit(title_txt, (WIDTH // 2 - title_txt.get_width() // 2, 12))

    stats_txt = font_small.render(f"Lucioles : {len(fireflies)} | Gouttelettes : {len(mist_drops)}", True, FIREFLY_GLOW)
    screen.blit(stats_txt, (40, 42))

    inst_txt = font_small.render("CLIC GAUCHE : Brumiser les plantes | F : Ajouter une luciole | SOURIS : Attirer | R : Reset", True, GRAY)
    screen.blit(inst_txt, (WIDTH - inst_txt.get_width() - 40, 42))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()