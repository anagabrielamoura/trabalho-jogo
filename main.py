import pygame
import sys
import os
import random

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
GOLD = (255, 215, 0)

# Fontes
FONT = pygame.font.SysFont("arial", 30)
BIG_FONT = pygame.font.SysFont("arial", 60)
GAME_OVER_FONT = pygame.font.SysFont("arial", 80)
VICTORY_FONT = pygame.font.SysFont("arial", 72)

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
        imagem = pygame.image.load(caminho)
        imagem = imagem.convert_alpha()

        if tamanho:
            imagem = pygame.transform.scale(imagem, tamanho)

        cor_fundo = imagem.get_at((0, 0))

        if cor_fundo[0] > 200 and cor_fundo[1] > 200 and cor_fundo[2] > 200:
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

        self.image = carregar_imagem_com_transparencia(
            PLAYER_IMAGE,
            tamanho=(64, 64)
        )

        if self.image is None:
            print("⚠️ Usando círculo como fallback para o jogador")

        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        # Sistema de invencibilidade
        self.invencivel = False
        self.tempo_invencivel = 0
        self.duracao_invencivel = 60

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
        self.invencivel = True
        self.tempo_invencivel = self.duracao_invencivel

    def atualizar_invencibilidade(self):
        if self.invencivel:
            self.tempo_invencivel -= 1
            if self.tempo_invencivel <= 0:
                self.invencivel = False

    def draw(self, screen):
        if self.image:
            if self.invencivel and (self.tempo_invencivel // 5) % 2 == 0:
                imagem_temp = self.image.copy()
                imagem_temp.set_alpha(128)
                screen.blit(imagem_temp, self.rect)
            else:
                screen.blit(self.image, self.rect)
        else:
            pygame.draw.circle(screen, (139, 69, 19), self.rect.center, 25)


# ============================================
# CLASSE DO INIMIGO (RAPOSA)
# ============================================

class Fox:
    def __init__(self, x=None, y=None):
        self.speed = random.randint(2, 4)  # Velocidade aleatória
        self.direction = 1
        self.width = 60
        self.height = 60

        self.image = carregar_imagem_com_transparencia(
            FOX_IMAGE,
            tamanho=(60, 60)
        )

        if self.image is None:
            print("⚠️ Usando retângulo como fallback para a raposa")

        # Posição aleatória, mas evitando o centro
        if x is None:
            self.rect = pygame.Rect(
                random.randint(100, WIDTH - 100),
                random.randint(100, HEIGHT - 100),
                self.width,
                self.height
            )
        else:
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
# CLASSE DA MAÇÃ (ITEM DE VITÓRIA)
# ============================================

class Apple:
    def __init__(self, x, y):
        self.width = 30
        self.height = 30

        self.image = carregar_imagem_com_transparencia(
            APPLE_IMAGE,
            tamanho=(30, 30)
        )

        if self.image is None:
            print("⚠️ Usando círculo como fallback para a maçã")

        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.coletada = False

    def draw(self, screen):
        if not self.coletada:
            if self.image:
                screen.blit(self.image, self.rect)
            else:
                pygame.draw.circle(screen, (255, 0, 0), self.rect.center, 15)


# ============================================
# CLASSE DO MENU (CONTROLES VOLTARAM PARA ESQUERDA)
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

        # ===== TÍTULO CENTRALIZADO =====
        title = BIG_FONT.render("GUARDIÕES DA FLORESTA", True, GREEN)
        title_rect = title.get_rect(center=(WIDTH//2, 80))
        SCREEN.blit(title, title_rect)

        # ===== FRASE DE REGRAS CENTRALIZADA =====
        regras = FONT.render("Colete 3 maçãs para vencer! Desvie das raposas!", True, WHITE)
        regras_rect = regras.get_rect(center=(WIDTH//2, 150))
        SCREEN.blit(regras, regras_rect)

        # ===== OPÇÕES DO MENU CENTRALIZADAS =====
        txt = FONT.render("ENTER - Jogar", True, BLACK)
        txt_rect = txt.get_rect(center=(WIDTH//2, 220))
        SCREEN.blit(txt, txt_rect)

        txt2 = FONT.render("ESC - Sair", True, BLACK)
        txt2_rect = txt2.get_rect(center=(WIDTH//2, 270))
        SCREEN.blit(txt2, txt2_rect)

        # ===== CONTROLES VOLTARAM PARA ESQUERDA E SUBIRAM =====
        # Título "CONTROLES" na esquerda
        controles = FONT.render("CONTROLES", True, YELLOW)
        SCREEN.blit(controles, (150, 320))  # ← Voltei para x=40 e subi para y=350

        # Lista de controles na esquerda
        lista = ["W - Cima", "S - Baixo", "A - Esquerda", "D - Direita"]
        y = 350  # ← Subi de 440 para 390
        for texto in lista:
            render = FONT.render(texto, True, YELLOW)
            SCREEN.blit(render, (150, y))  # ← Voltei para x=40
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
# CLASSE DO JOGO (ATUALIZADA COM SISTEMA DE VITÓRIA)
# ============================================

class Game:
    def __init__(self):
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_over = False
        self.vitoria = False
        self.mostrar_game_over = False
        self.mostrar_vitoria = False
        self.tempo_tela_final = 0
        self.duracao_tela_final = 180  # 3 segundos

        # ===== SISTEMA DE VIDAS =====
        self.vidas = 5
        self.vidas_maximas = 5

        # ===== SISTEMA DE MAÇÃS (VITÓRIA) =====
        self.macas = 0
        self.macas_necessarias = 3
        self.raposas_desviadas = 0
        self.raposas_necessarias = 5  # Precisa desviar de 5 raposas

        # Cria o jogador
        self.player = Player()

        # Cria os inimigos (5 raposas)
        self.enemies = []
        for i in range(5):
            fox = Fox()
            # Garante que não fiquem sobrepostos
            tentativas = 0
            while tentativas < 10:
                fox = Fox()
                sobreposto = False
                for f in self.enemies:
                    if fox.rect.colliderect(f.rect):
                        sobreposto = True
                        break
                if not sobreposto:
                    break
                tentativas += 1
            self.enemies.append(fox)

        # Cria as maçãs (3 maçãs escondidas)
        self.apples = []
        posicoes_ocupadas = [e.rect for e in self.enemies]

        for i in range(3):
            tentativas = 0
            while tentativas < 20:
                x = random.randint(50, WIDTH - 50)
                y = random.randint(50, HEIGHT - 50)
                novo_rect = pygame.Rect(x, y, 30, 30)

                # Verifica se não está sobreposto a nada
                sobreposto = False
                for rect in posicoes_ocupadas:
                    if novo_rect.colliderect(rect):
                        sobreposto = True
                        break

                if not sobreposto:
                    self.apples.append(Apple(x, y))
                    posicoes_ocupadas.append(novo_rect)
                    break
                tentativas += 1

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
        texto_vidas = FONT.render("VIDAS:", True, WHITE)
        SCREEN.blit(texto_vidas, (20, 20))

        for i in range(self.vidas_maximas):
            x = 120 + (i * 40)
            y = 25

            if i < self.vidas:
                coracao = FONT.render("❤️", True, RED)
            else:
                coracao = FONT.render("🖤", True, (100, 100, 100))

            SCREEN.blit(coracao, (x, y))

    def desenhar_macas(self):
        """Desenha as maçãs coletadas na tela"""
        texto_macas = FONT.render("MAÇÃS:", True, WHITE)
        SCREEN.blit(texto_macas, (20, 70))

        # Mostra as maçãs coletadas
        for i in range(self.macas_necessarias):
            x = 120 + (i * 40)
            y = 75

            if i < self.macas:
                # Maçã coletada (dourada)
                maca_texto = FONT.render("🍎", True, RED)
            else:
                # Maçã não coletada (contorno)
                maca_texto = FONT.render("⬜", True, (100, 100, 100))

            SCREEN.blit(maca_texto, (x, y))

        # Mostra o progresso (raposas desviadas)
        texto_progresso = FONT.render(f"RAPOSAS DESVIADAS: {self.raposas_desviadas}/{self.raposas_necessarias}", True,
                                      WHITE)
        SCREEN.blit(texto_progresso, (20, 120))

    def desenhar_tela_final(self, vitoria=False):
        """Desenha a tela de fim de jogo (vitória ou derrota)"""
        # Fundo semi-transparente
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        SCREEN.blit(overlay, (0, 0))

        if vitoria:
            # Tela de VITÓRIA
            texto_vitoria = VICTORY_FONT.render("🏆 VITÓRIA! 🏆", True, GOLD)
            texto_rect = texto_vitoria.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
            SCREEN.blit(texto_vitoria, texto_rect)

            texto_parabens = BIG_FONT.render("VOCÊ VENCEU!", True, GREEN)
            texto_parabens_rect = texto_parabens.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
            SCREEN.blit(texto_parabens, texto_parabens_rect)

            texto_macas = FONT.render(f"🍎 {self.macas} maçãs coletadas!", True, YELLOW)
            texto_macas_rect = texto_macas.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 120))
            SCREEN.blit(texto_macas, texto_macas_rect)
        else:
            # Tela de GAME OVER
            texto_game_over = GAME_OVER_FONT.render("GAME OVER", True, RED)
            texto_rect = texto_game_over.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
            SCREEN.blit(texto_game_over, texto_rect)

            texto_fim = BIG_FONT.render("FIM DE JOGO!", True, YELLOW)
            texto_fim_rect = texto_fim.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
            SCREEN.blit(texto_fim, texto_fim_rect)

        # Instrução para voltar
        texto_voltar = FONT.render("Pressione ENTER para voltar ao menu", True, WHITE)
        texto_voltar_rect = texto_voltar.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 180))
        SCREEN.blit(texto_voltar, texto_voltar_rect)

    def coletar_maca(self):
        """Coleta uma maçã e verifica vitória"""
        self.macas += 1
        print(f"🍎 Coletou uma maçã! ({self.macas}/{self.macas_necessarias})")

        # Toca um som de coleta (opcional)
        # pygame.mixer.Sound.play(som_coleta)

        if self.macas >= self.macas_necessarias:
            self.vitoria = True
            self.mostrar_vitoria = True
            self.tempo_tela_final = self.duracao_tela_final
            pygame.mixer.music.stop()
            print("🏆 VITÓRIA! Jogador coletou todas as maçãs!")

    def desviar_raposa(self):
        """Contabiliza raposa desviada e gera nova maçã"""
        self.raposas_desviadas += 1
        print(f"🦊 Raposa desviada! ({self.raposas_desviadas}/{self.raposas_necessarias})")

        # A cada raposa desviada, uma maçã aparece (se ainda não tiver todas)
        if self.raposas_desviadas <= self.raposas_necessarias:
            # Cria uma nova maçã em posição aleatória
            tentativas = 0
            while tentativas < 20:
                x = random.randint(50, WIDTH - 50)
                y = random.randint(50, HEIGHT - 50)
                novo_rect = pygame.Rect(x, y, 30, 30)

                # Verifica se não está sobreposto
                sobreposto = False
                for enemy in self.enemies:
                    if novo_rect.colliderect(enemy.rect):
                        sobreposto = True
                        break
                for apple in self.apples:
                    if novo_rect.colliderect(apple.rect) and not apple.coletada:
                        sobreposto = True
                        break
                if novo_rect.colliderect(self.player.rect):
                    sobreposto = True

                if not sobreposto:
                    self.apples.append(Apple(x, y))
                    break
                tentativas += 1

    def perder_vida(self):
        """Função chamada quando o jogador perde uma vida"""
        self.vidas -= 1
        self.player.ativar_invencibilidade()
        print(f"💔 Perdeu uma vida! Vidas restantes: {self.vidas}")

        # Reposiciona o jogador no centro
        self.player.rect.center = (WIDTH // 2, HEIGHT // 2)

        # Remove uma raposa (ela foi "desviada")
        if self.enemies:
            raposa_removida = self.enemies.pop(random.randint(0, len(self.enemies) - 1))
            self.desviar_raposa()
            print(f"🦊 Raposa desviada ao perder vida! Restam: {len(self.enemies)}")

        if self.vidas <= 0:
            self.game_over = True
            self.mostrar_game_over = True
            self.tempo_tela_final = self.duracao_tela_final
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
                    if self.mostrar_game_over or self.mostrar_vitoria:
                        if event.key == pygame.K_RETURN:
                            self.running = False
                            return
                    else:
                        if event.key == pygame.K_ESCAPE:
                            self.running = False
                            pygame.mixer.music.stop()
                            return

            # Se estiver em tela final, não atualiza o jogo
            if self.mostrar_game_over or self.mostrar_vitoria:
                if self.background:
                    SCREEN.blit(self.background, (0, 0))
                else:
                    SCREEN.fill((34, 139, 34))

                self.desenhar_tela_final(self.vitoria)
                pygame.display.flip()
                continue

            # Atualizações
            self.player.move()
            self.player.atualizar_invencibilidade()

            for fox in self.enemies:
                fox.move()

            # Verifica colisão com raposas
            if not self.player.invencivel and not self.game_over:
                for fox in self.enemies[:]:
                    if self.player.rect.colliderect(fox.rect):
                        self.perder_vida()
                        break

            # Verifica coleta de maçãs
            for apple in self.apples[:]:
                if not apple.coletada and self.player.rect.colliderect(apple.rect):
                    apple.coletada = True
                    self.coletar_maca()
                    self.apples.remove(apple)

            # Desenha o fundo do jogo
            if self.background:
                SCREEN.blit(self.background, (0, 0))
            else:
                SCREEN.fill((34, 139, 34))

            # Desenha as maçãs
            for apple in self.apples:
                apple.draw(SCREEN)

            # Desenha os inimigos
            for fox in self.enemies:
                fox.draw(SCREEN)

            # Desenha o jogador
            self.player.draw(SCREEN)

            # Desenha as vidas e maçãs
            self.desenhar_vidas()
            self.desenhar_macas()

            pygame.display.flip()


# ============================================
# ARQUIVO PRINCIPAL
# ============================================

def main():
    pygame.init()
    print("🎮 Iniciando Guardiões da Floresta...")
    print("🍎 Colete 3 maçãs para vencer!")
    print("🦊 Desvie de 5 raposas!")
    menu = Menu()
    menu.run()


if __name__ == "__main__":
    main()