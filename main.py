import pygame
import sys
import os

# ============================================
# CONFIGURAÇÕES (settings)
# ============================================

pygame.init()

# Tela
WIDTH = 980
HEIGHT = 620
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Guardiões da Floresta")

# FPS
FPS = 60

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 20, 60)
GREEN = (0, 200, 0)
BLUE = (0, 120, 255)
YELLOW = (255, 220, 0)
ORANGE = (255, 165, 0)
DARK_RED = (139, 0, 0)

# Fontes
FONT = pygame.font.SysFont("arial", 30)
BIG_FONT = pygame.font.SysFont("arial", 60)
GAME_OVER_FONT = pygame.font.SysFont("arial", 80)

# ============================================
# CAMINHOS DOS ARQUIVOS
# ============================================

# Fundo de tela
MENU_BACKGROUND = "assets/backgrounds/menu.png"
GAME_BACKGROUND = "assets/backgrounds/floresta.png"

# Imagens dos personagens
PLAYER_IMAGE = "assets/player/squirrel.png"
FOX_IMAGE = "assets/enemies/fox.png"
APPLE_IMAGE = "assets/items/apple.png"

# Músicas
MENU_MUSIC = "assets/music/menu.wav"
GAME_MUSIC = "assets/music/game.wav"


# ============================================
# FUNÇÃO PARA CARREGAR IMAGEM COM TRANSPARÊNCIA
# ============================================

def carregar_imagem_com_transparencia(caminho, tamanho=None):
    """
    Carrega uma imagem mantendo a transparência.
    Se a imagem tiver fundo branco, remove.
    """
    try:
        # Carrega a imagem
        imagem = pygame.image.load(caminho)

        # Converte para formato com canal alpha (transparência)
        imagem = imagem.convert_alpha()

        # Redimensiona se necessário
        if tamanho:
            imagem = pygame.transform.scale(imagem, tamanho)

        # Se a imagem tiver fundo branco (verifica o píxel superior esquerdo)
        # Pega a cor do píxel (0,0) - canto superior esquerdo
        cor_fundo = imagem.get_at((0, 0))

        # Se o fundo for branco ou quase branco, remove
        if cor_fundo[0] > 200 and cor_fundo[1] > 200 and cor_fundo[2] > 200:
            # Define a cor de fundo como transparente
            imagem.set_colorkey(cor_fundo)
            print(f"✅ Fundo removido da imagem: {os.path.basename(caminho)}")
        else:
            print(f"✅ Imagem carregada com transparência: {os.path.basename(caminho)}")

        return imagem

    except pygame.error as e:
        print(f"⚠️ Erro ao carregar imagem {caminho}: {e}")
        return None


# ============================================
# CLASSE DO JOGADOR
# ============================================

class Player:
    def __init__(self):
        self.speed = 5
        self.width = 50
        self.height = 50
        self.x = WIDTH // 2
        self.y = HEIGHT // 2

        # Carrega a imagem com transparência
        self.image = carregar_imagem_com_transparencia(
            PLAYER_IMAGE,
            tamanho=(64, 64)
        )

        if self.image is None:
            print("⚠️ Usando círculo como fallback para o jogador")

        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        # Sistema de invencibilidade após colisão
        self.invencivel = False
        self.tempo_invencivel = 0
        self.duracao_invencivel = 60  # 1 segundo (60 FPS)

    def move(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            self.rect.y -= self.speed
        if keys[pygame.K_s]:
            self.rect.y += self.speed
        if keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_d]:
            self.rect.x += self.speed

        # Limites da tela
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

    def ativar_invencibilidade(self):
        """Ativa o modo invencível após uma colisão"""
        self.invencivel = True
        self.tempo_invencivel = self.duracao_invencivel

    def atualizar_invencibilidade(self):
        """Atualiza o tempo de invencibilidade"""
        if self.invencivel:
            self.tempo_invencivel -= 1
            if self.tempo_invencivel <= 0:
                self.invencivel = False

    def draw(self, screen):
        if self.image:
            # Se estiver invencível, pisca a cada 5 frames
            if self.invencivel and (self.tempo_invencivel // 5) % 2 == 0:
                # Desenha com transparência (piscando)
                imagem_temp = self.image.copy()
                imagem_temp.set_alpha(128)  # Semi-transparente
                screen.blit(imagem_temp, self.rect)
            else:
                screen.blit(self.image, self.rect)
        else:
            # Fallback: círculo marrom
            pygame.draw.circle(screen, (139, 69, 19), self.rect.center, 25)


# ============================================
# CLASSE DO INIMIGO (RAPOSA)
# ============================================

class Fox:
    def __init__(self, x=150, y=150):
        self.speed = 3
        self.direction = 1
        self.width = 60
        self.height = 60

        # Carrega a imagem com transparência
        self.image = carregar_imagem_com_transparencia(
            FOX_IMAGE,
            tamanho=(60, 60)
        )

        if self.image is None:
            print("⚠️ Usando retângulo como fallback para a raposa")

        self.rect = pygame.Rect(x, y, self.width, self.height)

    def move(self):
        self.rect.x += self.speed * self.direction
        if self.rect.left <= 0:
            self.direction = 1
        if self.rect.right >= WIDTH:
            self.direction = -1

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, self.rect)
        else:
            pygame.draw.rect(screen, RED, self.rect)


# ============================================
# CLASSE DO MENU
# ============================================

class Menu:
    def __init__(self):
        self.clock = pygame.time.Clock()

        # Música do menu
        if os.path.exists(MENU_MUSIC):
            try:
                pygame.mixer.music.load(MENU_MUSIC)
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play(-1)
                print("🎵 Música do menu carregada!")
            except pygame.error as e:
                print(f"⚠️ Erro ao carregar música do menu: {e}")
        else:
            print("⚠️ Arquivo de música do menu não encontrado:", MENU_MUSIC)

        # Fundo do menu
        if os.path.exists(MENU_BACKGROUND):
            try:
                self.background = pygame.image.load(MENU_BACKGROUND)
                self.background = pygame.transform.scale(self.background, (WIDTH, HEIGHT))
                print("🖼️ Fundo do menu carregado!")
            except pygame.error as e:
                self.background = None
                print(f"⚠️ Erro ao carregar fundo do menu: {e}")
        else:
            self.background = None
            print("⚠️ Arquivo de fundo do menu não encontrado:", MENU_BACKGROUND)

    def draw(self):
        # Desenha o fundo
        if self.background:
            SCREEN.blit(self.background, (0, 0))
        else:
            SCREEN.fill((35, 130, 50))

        # Título
        title = BIG_FONT.render("GUARDIÕES DA FLORESTA", True, GREEN)
        SCREEN.blit(title, (250, 50))

        # Opções do menu
        txt = FONT.render("ENTER - Jogar", True, BLACK)
        SCREEN.blit(txt, (520, 180))

        txt2 = FONT.render("ESC - Sair", True, BLACK)
        SCREEN.blit(txt2, (535, 230))

        # Controles
        controles = FONT.render("CONTROLES", True, YELLOW)
        SCREEN.blit(controles, (200, 400))

        lista = ["W - Cima", "S - Baixo", "A - Esquerda", "D - Direita"]
        y = 440
        for texto in lista:
            render = FONT.render(texto, True, YELLOW)
            SCREEN.blit(render, (200, y))
            y += 34

        pygame.display.flip()

    def run(self):
        while True:
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        pygame.mixer.music.stop()
                        jogo = Game()
                        jogo.run()

                        # Volta a música do menu
                        if os.path.exists(MENU_MUSIC):
                            try:
                                pygame.mixer.music.load(MENU_MUSIC)
                                pygame.mixer.music.play(-1)
                            except pygame.error:
                                pass

                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

            self.draw()


# ============================================
# CLASS DO JOGO
# ============================================

class Game:
    def __init__(self):
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_over = False
        self.mostrar_game_over = False
        self.tempo_game_over = 0
        self.duracao_game_over = 180  # 3 segundos (60 FPS * 3)

        # ===== VIDAS =====
        self.vidas = 5
        self.vidas_maximas = 5
        self.perdeu_vida = False
        self.tempo_perda_vida = 0

        # Cria o jogador
        self.player = Player()

        # Cria os inimigos
        self.enemies = []
        for i in range(3):
            fox = Fox()
            fox.rect.x = 200 + i * 300
            fox.rect.y = 100 + i * 150
            self.enemies.append(fox)

        # Fundo do jogo
        if os.path.exists(GAME_BACKGROUND):
            try:
                self.background = pygame.image.load(GAME_BACKGROUND)
                self.background = pygame.transform.scale(self.background, (WIDTH, HEIGHT))
                print("🖼️ Fundo do jogo carregado!")
            except pygame.error as e:
                self.background = None
                print(f"⚠️ Erro ao carregar fundo do jogo: {e}")
        else:
            self.background = None
            print("⚠️ Arquivo de fundo do jogo não encontrado:", GAME_BACKGROUND)

        # Música do jogo
        if os.path.exists(GAME_MUSIC):
            try:
                pygame.mixer.music.load(GAME_MUSIC)
                pygame.mixer.music.set_volume(0.3)
                pygame.mixer.music.play(-1)
                print("🎵 Música do jogo carregada!")
            except pygame.error as e:
                print(f"⚠️ Erro ao carregar música do jogo: {e}")
        else:
            print("⚠️ Arquivo de música do jogo não encontrado:", GAME_MUSIC)

    def desenhar_vidas(self):
        """Desenha as vidas na tela"""
        # Texto "VIDAS:"
        texto_vidas = FONT.render("VIDAS:", True, WHITE)
        SCREEN.blit(texto_vidas, (20, 20))

        # Desenha os corações
        for i in range(self.vidas_maximas):
            x = 120 + (i * 40)
            y = 25

            if i < self.vidas:
                # Coração cheio (vermelho)
                coracao = FONT.render("❤️", True, RED)
            else:
                # Coração vazio (cinza)
                coracao = FONT.render("🖤", True, (100, 100, 100))

            SCREEN.blit(coracao, (x, y))

    def desenhar_game_over(self):
        """Desenha a tela de Game Over"""
        # Fundo semi-transparente
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)  # Transparência
        overlay.fill(BLACK)
        SCREEN.blit(overlay, (0, 0))

        # Texto GAME OVER
        texto_game_over = GAME_OVER_FONT.render("GAME OVER", True, RED)
        texto_rect = texto_game_over.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        SCREEN.blit(texto_game_over, texto_rect)

        # Texto "Fim de Jogo"
        texto_fim = BIG_FONT.render("FIM DE JOGO!", True, YELLOW)
        texto_fim_rect = texto_fim.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
        SCREEN.blit(texto_fim, texto_fim_rect)

        # Instrução para voltar
        texto_voltar = FONT.render("Pressione ENTER para voltar ao menu", True, WHITE)
        texto_voltar_rect = texto_voltar.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 150))
        SCREEN.blit(texto_voltar, texto_voltar_rect)

    def perder_vida(self):
        """Função chamada quando o jogador perde uma vida"""
        self.vidas -= 1
        self.perdeu_vida = True
        self.tempo_perda_vida = 30  # 0.5 segundo de pausa
        self.player.ativar_invencibilidade()
        print(f"💔 Perdeu uma vida! Vidas restantes: {self.vidas}")

        if self.vidas <= 0:
            self.game_over = True
            self.mostrar_game_over = True
            self.tempo_game_over = self.duracao_game_over
            pygame.mixer.music.stop()
            print("💀 GAME OVER! Fim de jogo!")

    def run(self):
        while self.running:
            self.clock.tick(FPS)

            # Processa eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if self.mostrar_game_over:
                        if event.key == pygame.K_RETURN:
                            # Volta ao menu
                            self.running = False
                            return
                    else:
                        if event.key == pygame.K_ESCAPE:
                            self.running = False
                            pygame.mixer.music.stop()
                            return

            # Se estiver em game over, não atualiza o jogo
            if self.mostrar_game_over:
                # Desenha a tela de game over
                if self.background:
                    SCREEN.blit(self.background, (0, 0))
                else:
                    SCREEN.fill((34, 139, 34))

                self.desenhar_game_over()
                pygame.display.flip()
                continue

            # Atualizações
            self.player.move()
            self.player.atualizar_invencibilidade()

            for fox in self.enemies:
                fox.move()

            # Verifica colisões
            if not self.player.invencivel and not self.game_over:
                for fox in self.enemies:
                    if self.player.rect.colliderect(fox.rect):
                        self.perder_vida()
                        # Reposiciona o jogador no centro após perder vida
                        self.player.rect.center = (WIDTH // 2, HEIGHT // 2)
                        break

            # Desenha o fundo do jogo
            if self.background:
                SCREEN.blit(self.background, (0, 0))
            else:
                SCREEN.fill((34, 139, 34))

            # Desenha os inimigos
            for fox in self.enemies:
                fox.draw(SCREEN)

            # Desenha o jogador
            self.player.draw(SCREEN)

            # Desenha as vidas
            self.desenhar_vidas()

            pygame.display.flip()


# ============================================
# ARQUIVO PRINCIPAL
# ============================================

def main():
    pygame.init()
    print("🎮 Iniciando Guardiões da Floresta...")
    menu = Menu()
    menu.run()


if __name__ == "__main__":
    main()