import pygame
from PIL import Image
import random
import datetime
import math
import sys, os
from recursos.funcoes import calcular_distancia
from PIL import Image

# Inicializa Pygame e som
pygame.init()
pygame.mixer.init()
pygame.mixer.music.load("recursos/musicaFundo.mp3")
pygame.mixer.music.set_volume(0.7)
pygame.mixer.music.play(-1)

som_pulo = pygame.mixer.Sound("recursos/EfeitoPulo.wav")
som_pulo.set_volume(0.7)
som_colisao = pygame.mixer.Sound("recursos/Som_colisao.wav")
som_colisao.set_volume(0.8)

# Tela
tela_largura = 1000
tela_altura = 700
tela = pygame.display.set_mode((tela_largura, tela_altura))
pygame.display.set_caption("The last knight game")

imagemFundo = pygame.image.load("recursos/ImagemFundo.png.gif").convert()
imagemFundo = pygame.transform.scale(imagemFundo, (tela_largura, tela_altura))

#Caregando imagem do barril toxico
barrilToxico = pygame.image.load("recursos/BarrilToxico.png").convert_alpha()
barrilToxico.set_colorkey((246, 246, 246))  # Torna o branco transparente
barrilToxico = pygame.transform.scale(barrilToxico, (130, 130))
# Rect do barril
barril_rect = barrilToxico.get_rect()
     
img = Image.open("recursos/BarrilToxico.png").convert("RGBA")
datas = img.getdata()
nova_img = []
for item in datas:
    # Torna transparente qualquer pixel "quase branco"
    if item[0] > 230 and item[1] > 230 and item[2] > 230:
        nova_img.append((255, 255, 255, 0))
    else:
        nova_img.append(item)
img.putdata(nova_img)
img.save("recursos/BarrilToxico.png")

# Carregando imagem da bomba
bomba_original = pygame.image.load("recursos/ImagemBomba.png").convert_alpha()
bomba_original.set_colorkey((255, 255, 255))  # Torna o branco transparente
bomba_img = pygame.transform.scale(bomba_original, (60, 60))
bomba_rect = bomba_img.get_rect()
bomba_rect.topleft = (
    random.randint(0, tela_largura - bomba_rect.width),
    random.randint(0, tela_altura - bomba_rect.height)
)
bomba_img.set_alpha(255)  # 0 = invisível, 255 = opaco

# Movimento randômico
def move_bomba(rect):
    dx = random.choice([-3, -2, -1, 0, 1, 2, 3])
    dy = random.choice([-3, -2, -1, 0, 1, 2, 3])
    rect.x += dx
    rect.y += dy

    # Mantém dentro da tela
    rect.x = max(0, min(tela_largura - rect.width, rect.x))
    rect.y = 330 

bomba_visivel = False
bomba_timer = 0
bomba_duracao = 1200  # milissegundos que a bomba fica visível
bomba_intervalo = random.randint(4000, 8000)  # intervalo entre aparições
bomba_chao = None  # Para controlar os 2 segundos no chão


#Carregando explosão
explosao_img = pygame.image.load("recursos/explosao.jpg").convert_alpha()
explosao_img = pygame.transform.scale(explosao_img, (80, 80))
explodindo = False
explosao_timer = 0
explosao_duracao = 500  # milissegundos
explosao_pos = (0, 0)
explosao_img.set_colorkey((255, 255, 255))  # Torna transparente


# Extrair frames de GIF
def extrair_frames(gif_path):
    imagem = Image.open(gif_path)
    frames = []
    for i in range(imagem.n_frames):
        imagem.seek(i)
        frame = imagem.convert("RGBA")
        datas = frame.getdata()
        nova_imagem = [(0, 0, 0, 0) if item[:3] == (171, 164, 163) else item for item in datas]
        frame.putdata(nova_imagem)
        modo = frame.mode
        tamanho = frame.size
        dados = frame.tobytes()
        pygame_image = pygame.image.fromstring(dados, tamanho, modo).convert_alpha()
        frames.append(pygame_image)
    return frames

# Carregar imagem do avião e remover fundo
img = Image.open("recursos/aviao.gif").convert("RGBA")
datas = img.getdata()
nova_img = []
for item in datas:
    # Torna transparente qualquer pixel "quase branco"
    if item[0] > 230 and item[1] > 230 and item[2] > 230:
        nova_img.append((255, 255, 255, 0))
    else:
        nova_img.append(item)
img.putdata(nova_img)
img.save("recursos/aviao.gif")

# Carregar imagem do tanque e remover fundo
img = Image.open("recursos/TanqueGuerra.png").convert("RGBA")
datas = img.getdata()
nova_img = []
for item in datas:
    # Torna transparente qualquer pixel "quase branco"
    if item[0] > 230 and item[1] > 230 and item[2] > 230:
        nova_img.append((255, 255, 255, 0))
    else:
        nova_img.append(item)
img.putdata(nova_img)
img.save("recursos/TanqueGuerra_semfundo.png")

# Frames personagem
personagem_frames = extrair_frames("recursos/animacaoPersonagem.png.gif")

class Personagem:
    def __init__(self):
        self.run_frames = personagem_frames
        self.frame_index = 0
        self.frame_contador = 0
        self.frame_velocidade = 5
        self.x, self.y = 80, 330
        self.altura_original = self.run_frames[0].get_height()
        self.largura_original = self.run_frames[0].get_width()
        self.vel_y = 0
        self.vel_pulo = 20
        self.gravidade = 1
        self.pulo = False
        self.abaixado = False

    def atualizar(self):
        self.frame_contador += 1
        if self.frame_contador >= self.frame_velocidade:
            self.frame_index = (self.frame_index + 1) % len(self.run_frames)
            self.frame_contador = 0
        if self.pulo:
            self.y -= self.vel_y
            self.vel_y -= self.gravidade
            if self.y >= 330:
                self.y = 330
                self.pulo = False
                self.vel_y = self.vel_pulo

    def desenhar(self, tela):
        frame = self.run_frames[self.frame_index]
        if self.abaixado and not self.pulo:
            largura = int(self.largura_original * 0.8)
            altura = int(self.altura_original * 0.5)
            frame = pygame.transform.scale(frame, (largura, altura))
            y = self.y + (self.altura_original - altura)
            tela.blit(frame, (self.x, y))
        else:
            tela.blit(frame, (self.x, self.y))

    def get_rect(self):
        if self.abaixado and not self.pulo:
            largura = int(self.largura_original * 0.8)
            altura = int(self.altura_original * 0.5)
            y = self.y + (self.altura_original - altura)
            return pygame.Rect(self.x + 10, y + 10, largura - 20, altura - 20)
        else:
            return pygame.Rect(self.x + 10, self.y + 10, self.largura_original - 20, self.altura_original - 20)

class Obstaculo:
    def __init__(self, imagem_path, largura, altura, y_fixo, colorkey=(255, 255, 255)):
        self.imagem_original = pygame.image.load(imagem_path).convert()
        self.imagem_original.set_colorkey(colorkey)
        self.imagem = pygame.transform.scale(self.imagem_original, (largura, altura))
        self.x = 1000
        self.y = y_fixo
        self.velocidade = 8
        self.rect = self.imagem.get_rect(topleft=(self.x, self.y))
        self.hitbox_offset = pygame.Rect(10, 10, largura - 20, altura - 20)

    def calcular_velocidade_obstaculo(tempo_ms, base=8, aumento_por_segundo=0.03, limite=20):
        tempo_s = tempo_ms / 1000
        nova_vel = base + tempo_s * aumento_por_segundo
        return min(nova_vel, limite)

    def atualizar(self):
        self.x -= self.velocidade
        self.rect.x = self.x

    def desenhar(self, tela):
        if self.velocidade > 12:
            imagem_tint = self.imagem.copy()
            fator_vermelho = min(255, int((self.velocidade - 12) * 30))
            imagem_tint.fill((fator_vermelho, 0, 0), special_flags=pygame.BLEND_RGB_ADD)
            tela.blit(imagem_tint, (self.x, self.y))
        else:
            tela.blit(self.imagem, (self.x, self.y))

    def get_rect(self):
        return pygame.Rect(self.x + self.hitbox_offset.x, self.y + self.hitbox_offset.y,
                           self.hitbox_offset.width, self.hitbox_offset.height)
    
    def salvar_log_partida(nome, pontuacao):
        agora = datetime.datetime.now()
        data = agora.strftime("%d/%m/%Y")
        hora = agora.strftime("%H:%M:%S")
        linha = f"Jogador: {nome} | Pontuação: {pontuacao} | Data: {data} | Hora: {hora}\n"

        with open("log_partidas.txt", "a", encoding="utf-8") as arquivo:
            arquivo.write(linha)
            

class Tanque(Obstaculo):
    def __init__(self):
        super().__init__("recursos/TanqueGuerra.png", 120, 70, y_fixo=420)

class Aviao(Obstaculo):
    def __init__(self):
        super().__init__("recursos/aviao.gif", 140, 90, y_fixo=310)

# Fonte
fonte_titulo = pygame.font.SysFont('arialblack', 50)
fonte_input = pygame.font.SysFont('comicsans', 40)

# Nome
digitando = True
nome = ""
while digitando:
    tela.blit(imagemFundo, (0, 0))
    overlay = pygame.Surface((800, 200))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    tela.blit(overlay, (100, 100))

    titulo1 = fonte_titulo.render("The last knight game", True, (128, 128, 128))
    titulo2 = fonte_titulo.render("Digite seu nome: ", True, ((255, 255, 255)))
    if len(nome) > 20:
        nome = nome[:20]  # Limita o nome a 20 caracteres
    entrada = fonte_input.render(nome + "|", True, (255, 255, 255))

    tela.blit(titulo1, (250, 100))
    tela.blit(titulo2, (120, 100 + titulo1.get_height() + 10))
    tela.blit(entrada, (600, 190))
    pygame.display.update()

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            digitando = False
            pygame.quit()
            exit()
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_RETURN and nome:
                digitando = False
            elif evento.key == pygame.K_BACKSPACE:
                nome = nome[:-1]
            else:
                nome += evento.unicode

# Painel de Boas-vindas
fonte_boasvindas = pygame.font.SysFont('arialblack', 60)
mensagem = fonte_boasvindas.render(f"Bem-vindo, {nome}!", True, (255, 255, 255))
overlay = pygame.Surface((800, 120))
overlay.set_alpha(180)
overlay.fill((0, 0, 0))
tela.blit(imagemFundo, (0, 0))
tela.blit(overlay, (100, 100))
tela.blit(mensagem, (tela_largura // 2 - mensagem.get_width() // 2, 100))
pygame.display.update()
esperando = True
tempo_mensagem = pygame.time.get_ticks()
while esperando:
    if pygame.time.get_ticks() - tempo_mensagem > 2000:
        esperando = False
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            exit()

# Iniciar personagem
personagem = Personagem()
obstaculos = []
tempo_ultimo_obstaculo = pygame.time.get_ticks()
intervalo = random.randint(1500, 2500)

relogio = pygame.time.Clock()
rodando = True
pausado = False
tempo_abaixado = 0
abaixando = False

pontuacao = 0
fonte = pygame.font.SysFont('comicsans', 30)

velocidade_mps = 10
inicio_tempo = pygame.time.get_ticks()

fonte_instrucao = pygame.font.SysFont('arial', 30)
fonte_titulo_instrucao = pygame.font.SysFont('arialblack', 50)

mostrando_instrucoes = True
while mostrando_instrucoes:
    tela.blit(imagemFundo, (0, 0))
    caixa_instrucao = pygame.Surface((900, 350))
    caixa_instrucao.set_alpha(180)
    caixa_instrucao.fill((0, 0, 0))
    tela.blit(caixa_instrucao, (50, 200))

    titulo = fonte_titulo_instrucao.render("Como jogar:", True, (255, 255, 0))
    tela.blit(titulo, (tela_largura // 2 - titulo.get_width() // 2, 210))

    instrucoes = [
        "Pressione ESPAÇO para PULAR os obstáculos.",
        "Use a SETA PARA BAIXO ou tecla S para abaixar.",
        "Evite tanques e aviões no caminho.",
        "Ganhe pontos ao sobreviver mais tempo!",
        "Pressione ESPAÇO para começar."
    ]
    for i, linha in enumerate(instrucoes):
        texto = fonte_instrucao.render(linha, True, (255, 255, 255))
        tela.blit(texto, (100, 270 + i * 40))

    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                mostrando_instrucoes = False

pygame.display.update()



#Loop principal
while rodando:
    relogio.tick(60)
    tempo_atual = pygame.time.get_ticks()
    tela.blit(imagemFundo, (0, 0))

# Desenha o barril tóxico
tempo_pulsar = pygame.time.get_ticks() / 1000
escala = 1 + 0.1 * math.sin(tempo_pulsar * 2 ) #2 = velocidade de pulsação, 0.1 = instensidade
largura_pulsar = int(130 * escala)
altura_pulsar = int(130 * escala)
barril_pulsado = pygame.transform.smoothscale(barrilToxico, (largura_pulsar, altura_pulsar))

# Centraliza o barril na posição original (520, 380)
x_barril = 520 + (130 - largura_pulsar) // 2
y_barril = 380 + (130 - altura_pulsar) // 2
tela.blit(barril_pulsado, (x_barril, y_barril)) 

for evento in pygame.event.get():
    if evento.type == pygame.QUIT:
        rodando = False
    elif evento.type == pygame.KEYDOWN:
        if evento.key == pygame.K_SPACE:
            if not personagem.pulo and not pausado:
                personagem.pulo = True
                personagem.vel_y = personagem.vel_pulo
                som_pulo.play()
        elif evento.key == pygame.K_RETURN:
            pausado = not pausado

if pausado:
    # Desenha overlay escuro
    overlay_pause = pygame.Surface((tela_largura, tela_altura))
    overlay_pause.set_alpha(180)
    overlay_pause.fill((0, 0, 0))
    tela.blit(overlay_pause, (0, 0))

    # Desenha o texto "PAUSE" centralizado
    texto_pause = fonte_titulo.render("PAUSE", True, (255, 255, 255))
    tela.blit(
        texto_pause,
        (tela_largura // 2 - texto_pause.get_width() // 2,
        tela_altura // 2 - texto_pause.get_height() // 2)
    )

    pygame.display.update()
    #continue  # <-- Só pula o restante do loop se estiver pausado

# Atualiza estado de abaixado
teclas = pygame.key.get_pressed()
if teclas[pygame.K_DOWN] or teclas[pygame.K_s]:
    if not abaixando:
        tempo_abaixado = pygame.time.get_ticks()
        abaixando = True
    elif (pygame.time.get_ticks() - tempo_abaixado) <= 1000:
        personagem.abaixado = True
    else:
        personagem.abaixado = False
else:
    personagem.abaixado = False
    abaixando = False

personagem.atualizar()
personagem.desenhar(tela)

# ====== Explosão ======
if explodindo:
    tempo_explosao = tempo_atual - explosao_timer 
    if tempo_atual - explosao_timer < explosao_duracao:
        tela.blit(explosao_img, explosao_pos)
    else:
        explodindo = False
# ====== BOMBA  ======
if not bomba_visivel and tempo_atual - bomba_timer > bomba_intervalo:
    bomba_rect.x = random.randint(20, tela_largura - bomba_rect.width)
    bomba_rect.y = 0
    bomba_visivel = True
    bomba_timer = tempo_atual
    bomba_atingiu_chao_em = None

if bomba_visivel:
    if bomba_rect.y < 420:
        bomba_rect.y += 8
        bomba_rect.x += random.choice([-1, 0, 1])
        bomba_rect.x = max(0, min(tela_largura - bomba_rect.width, bomba_rect.x))
    elif bomba_atingiu_chao_em is None:
        bomba_atingiu_chao_em = tempo_atual

    if bomba_atingiu_chao_em is not None and tempo_atual - bomba_atingiu_chao_em > 2000:
        bomba_visivel = False
        bomba_timer = tempo_atual
        bomba_intervalo = random.randint(4000, 8000)
        # Inicia explosão
        explodindo = True
        explosao_timer = tempo_atual
        explosao_pos = (bomba_rect.x + bomba_rect.width // 2 - 40, bomba_rect.y + bomba_rect.height // 2 - 40)  # centraliza a explosão

    
    tela.blit(bomba_img, bomba_rect.topleft)

# ====== Obstáculos ======
if tempo_atual - tempo_ultimo_obstaculo > intervalo:
    vel = Obstaculo.calcular_velocidade_obstaculo(tempo_atual - inicio_tempo)
    tipo = random.choice([Tanque, Aviao])
    novo_obstaculo = tipo()
    novo_obstaculo.velocidade = vel
    obstaculos.append(novo_obstaculo)
    tempo_ultimo_obstaculo = tempo_atual
    intervalo = random.randint(1500, 2500)

for obstaculo in obstaculos[:]:
    obstaculo.atualizar()
    obstaculo.desenhar(tela)

    if obstaculo.get_rect().colliderect(personagem.get_rect()):                         
        som_colisao.play()
        rodando = False

    if obstaculo.x + obstaculo.rect.width < 0:
        obstaculos.remove(obstaculo)
        pontuacao += 1  

texto_pontuacao = fonte.render(f"Pontuação: {pontuacao}", True, (255, 255, 255))
tela.blit(texto_pontuacao, (10, 10))
tempo_decorrido = tempo_atual - inicio_tempo
distancia_metros = int(tempo_decorrido / 1000 * velocidade_mps)
texto_distancia = fonte.render(f"Distância: {distancia_metros} m", True, (255, 255, 255))
tela.blit(texto_distancia, (10, 40))
msg_pause = pygame.font.SysFont('comicsans', 22).render("• Press Enter to Pause Game.", True, (0, 0, 0))
tela.blit(msg_pause, (texto_pontuacao.get_width() + 20, 14))

#salvar log da partida no histórico
Obstaculo.salvar_log_partida(nome, pontuacao)
pygame.display.update()

jogando_novamente = None
while jogando_novamente is None:
    tela.fill((0, 0, 0))
    fonte_fim = pygame.font.SysFont('arialblack', 60)
    fonte_opcao = pygame.font.SysFont('arial', 36)
    texto_fim = fonte_fim.render("FIM DE JOGO", True, (255, 0, 0))
    texto_pontuacao = fonte_opcao.render(f"Pontuação: {pontuacao}", True, (255, 255, 255))
    texto_distancia = fonte_opcao.render(f"Distância: {distancia_metros} m", True, (255, 255, 255))
    texto_pergunta = fonte_opcao.render("Jogar novamente? (S/N)", True, (255, 255, 0))
    tela.blit(texto_fim, (tela_largura // 2 - texto_fim.get_width() // 2, 180))
    tela.blit(texto_pontuacao, (tela_largura // 2 - texto_pontuacao.get_width() // 2, 280)) 
    tela.blit(texto_distancia, (tela_largura // 2 - texto_distancia.get_width() // 2, 320))
    tela.blit(texto_pergunta, (tela_largura // 2 - texto_pergunta.get_width() // 2, 400))
    pygame.display.update()

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            exit()
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_s:
                jogando_novamente = True
            elif evento.key == pygame.K_n:
                jogando_novamente = False

    if jogando_novamente:
        os.execl(sys.executable, sys.executable, *sys.argv)
    else:
        pygame.quit()
        exit()