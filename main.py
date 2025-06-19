import pygame
import random
import datetime
import math
import speech_recognition as sr
import pyttsx3
from PIL import Image
from recursos.definicao import calcular_distancia

# Inicialização
pygame.init()
pygame.font.init()
pygame.mixer.init()

# Sons
pygame.mixer.music.load("recursos/musicaFundo.mp3")
pygame.mixer.music.set_volume(0.6)
pygame.mixer.music.play(-1)

som_pulo = pygame.mixer.Sound("recursos/EfeitoPulo.wav")
som_pulo.set_volume(0.7)
som_colisao = pygame.mixer.Sound("recursos/somColisao.wav")
som_colisao.set_volume(0.8)

# Tela
LARGURA = 1000
ALTURA = 700
tela = pygame.display.set_mode((LARGURA, ALTURA))
fonte = pygame.font.SysFont("arial", 36)
pygame.display.set_caption("The Last Knight Game")
pontuacao = 0

# Fontes
fonte_titulo = pygame.font.SysFont('arial', 50)
fonte_input = pygame.font.SysFont('comicsans', 40)
fonte_pontuacao = pygame.font.SysFont("arial", 36)

engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 0.9)

# Função para extrair frames do gif
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

def ouvir_comando():
    reconhecedor = sr.Recognizer()
    with sr.Microphone() as source:
        print("Diga 'iniciar' para começar o jogo...")
        audio = reconhecedor.listen(source, phrase_time_limit=3)
        try:
            comando = reconhecedor.recognize_google(audio, language="pt-BR")
            print(f"Você disse: {comando}")
            return comando.lower()
        except sr.UnknownValueError:
            print("Não entendi o que você disse.")
            return ""
        except sr.RequestError:
            print("Erro ao acessar o serviço de reconhecimento.")
            return ""

def salvar_log(pontuacao, nome):
    agora = datetime.datetime.now()
    data = agora.strftime("%Y-%m-%d")
    hora = agora.strftime("%H:%M:%S")
    with open("log_dat.txt", "a") as arquivo:
        arquivo.write(f"Pontuação: {pontuacao} | Jogador: {nome} | Data: {data} | Hora: {hora}\n")

def tela_fim_jogo(tela, fonte, pontuacao, salvar_log_fn, nome):
    salvar_log_fn(pontuacao, nome)

    # Lê os registros do log
    try:
        with open("log_dat.txt", "r") as arquivo:
            linhas = arquivo.readlines()
    except FileNotFoundError:
        linhas = []

    ultimos_logs = linhas[-5:] if linhas else []

    # Encontra o/a recordista
    recorde = 0
    recordista = "N/A"
    for linha in linhas:
        if "Pontuação:" in linha:
            try:
                partes = linha.split("|")
                pontos = int(partes[0].split(":")[1].strip())
                jogador = partes[1].split(":")[1].strip()
                if pontos > recorde:
                    recorde = pontos
                    recordista = jogador
            except:
                continue

    largura_tela, altura_tela = tela.get_size()
    tela.blit(fundoGameOver, (0, 0))

    texto_fim = fonte.render("Fim de jogo!", True, (255, 0, 0))
    texto_pontuacao = fonte.render(f"Sua pontuação: {pontuacao}", True, (255, 255, 255))
    texto_reiniciar = fonte.render("Pressione ESC para sair", True, (255, 0, 0))

    tela.blit(texto_fim, (largura_tela // 2 - texto_fim.get_width() // 2, 60))
    tela.blit(texto_pontuacao, (largura_tela // 2 - texto_pontuacao.get_width() // 2, 110))
    tela.blit(texto_reiniciar, (largura_tela // 2 - texto_reiniciar.get_width() // 2, 160))

    # Exibe os últimos 5 registros
    y_offset = 220
    tela.blit(fonte.render("Últimos registros:", True, (255, 255, 255)), (50, y_offset))
    fonte_menor = pygame.font.SysFont("arial", 28)
    for i, log in enumerate(ultimos_logs):
        texto = fonte_menor.render(log.strip(), True, (180, 180, 180))
        tela.blit(texto, (50, y_offset + 40 + i * 40))

    # Exibe o recordista
    texto_recorde = fonte.render(f"Recorde: {recorde} - {recordista}", True, (34, 139, 34))  # Verde floresta
    tela.blit(texto_recorde, (50, y_offset + 360))

    pygame.display.update()

    esperando_resposta = True
    while esperando_resposta:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    esperando_resposta = False
                elif evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()

# Recursos
fundo = pygame.transform.scale(pygame.image.load("recursos/ImagemFundo.png.gif"), (LARGURA, ALTURA))
personagem_frames = extrair_frames("recursos/animacaoPersonagem.png.gif")
tanque_img = pygame.image.load("recursos/TanqueGuerra.png").convert_alpha()
aviao_img = pygame.image.load("recursos/aviao.gif").convert_alpha()
fundoGameOver = pygame.image.load("recursos/ImagemGameOver.png").convert_alpha()
fundoGameOver = pygame.transform.scale(fundoGameOver, (LARGURA, 1050))

# Entrada de nome
nome = ""
digitando = True
clock = pygame.time.Clock()
while digitando:
    clock.tick(60)
    tela.blit(fundo, (0, 0))
    overlay = pygame.Surface((800, 200))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    tela.blit(overlay, (100, 100))

    tela.blit(fonte_titulo.render("The Last Knight Game", True, (128, 128, 128)), (250, 100))
    tela.blit(fonte_titulo.render("Digite seu nome:", True, (255, 255, 255)), (120, 160))
    texto_nome = fonte_input.render(nome + "|", True, (255, 255, 255))
    tela.blit(texto_nome, (440, 160))
    pygame.display.update()

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            exit()
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_RETURN and nome:
                digitando = False
                engine.say(f"Bem-vindo ao jogo, {nome}!")
                engine.runAndWait()
            elif evento.key == pygame.K_SPACE:
                nome = nome[:-1]
            else:
                nome += evento.unicode

 # Tela de Boas-vindas com botão
botao_largura = 300
botao_altura = 60
botao_x = LARGURA // 2 - botao_largura // 2
botao_y = 500
fonte_explicacao = pygame.font.SysFont('arial', 28)
fonte_botao = pygame.font.SysFont('arialblack', 36)
fonte_boasvindas = pygame.font.SysFont('arial', 40)

esperando = True
ultimo_voz = pygame.time.get_ticks()

while esperando:
    tela.blit(fundo, (0, 0))
    overlay = pygame.Surface((900, 500))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 0))
    tela.blit(overlay, (50, 100))

    titulo = fonte_boasvindas.render(f"Bem-vindo, {nome}!", True, (255, 255, 255))
    tela.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 120))

    explicacoes = [
        "Você deve pular (tecla ESPAÇO)",
        "para evitar obstáculos como tanques e aviões.",
        "Diga 'iniciar' ou clique no botão para começar.",
        "Bombas aparecerão aleatoriamente, mas ela serve apenas para efeito, ignore-as.",
    ]
    for i, linha in enumerate(explicacoes):
        texto = fonte_explicacao.render(linha, True, (200, 200, 200))
        tela.blit(texto, (LARGURA // 2 - texto.get_width() // 2, 200 + i * 40))

    pygame.draw.rect(tela, (0, 128, 0), (botao_x, botao_y, botao_largura, botao_altura), border_radius=10)
    texto_botao = fonte_botao.render("INICIAR", True, (255, 255, 255))
    tela.blit(texto_botao, (botao_x + botao_largura // 2 - texto_botao.get_width() // 2,
                            botao_y + botao_altura // 2 - texto_botao.get_height() // 2))

    pygame.display.update()

    # A cada 5 segundos tenta ouvir por voz
    if pygame.time.get_ticks() - ultimo_voz > 5000:
        comando = ouvir_comando()
        if "iniciar" in comando:
            esperando = False
        ultimo_voz = pygame.time.get_ticks()

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif evento.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if botao_x <= mouse_x <= botao_x + botao_largura and botao_y <= mouse_y <= botao_y + botao_altura:
                esperando = False

            


# Estado inicial
x_persona = 80
y_persona = 330
vel_pulo = 20
gravidade = 1
pulo = False
vel_y = vel_pulo
frame_index = 0
frame_contador = 0
frame_velocidade = 5 

aviao_img = pygame.image.load('recursos/aviao.gif').convert_alpha()
tanque_img = pygame.image.load('recursos/TanqueGuerra.png').convert_alpha()
aviao_img = pygame.transform.scale(aviao_img, (120, 70))
tanque_img = pygame.transform.scale(tanque_img, (120, 70))

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
    random.randint(0, LARGURA - bomba_rect.width),
    random.randint(0, ALTURA - bomba_rect.height)
)
bomba_img.set_alpha(255)  # 0 = invisível, 255 = opaco

# Movimento randômico
def move_bomba(rect):
    dx = random.choice([-3, -2, -1, 0, 1, 2, 3])
    dy = random.choice([-3, -2, -1, 0, 1, 2, 3])
    rect.x += dx
    rect.y += dy

    # Mantém dentro da tela
    rect.x = max(0, min(LARGURA - rect.width, rect.x))
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

obstaculos = []
pontuacao = 0
rodando = True
pausado = False
relogio = pygame.time.Clock()
ultimo_obstaculo = pygame.time.get_ticks()

inicio_tempo = pygame.time.get_ticks()

# Loop principal do jogo
while rodando:
    relogio.tick(60)
    tela.blit(fundo, (0, 0))

    pausado = False

    # Animação do personagem
    frame_contador += 1
    if frame_contador >= frame_velocidade:
        frame_index = (frame_index + 1) % len(personagem_frames)
        frame_contador = 0
    personagem_img = personagem_frames[frame_index]
    tela.blit(personagem_img, (x_persona, y_persona))
    if pulo:
        y_persona -= vel_y
        vel_y -= gravidade
        if y_persona >= 330:
            y_persona = 330
            pulo = False
            vel_y = vel_pulo
    rect_persona = personagem_img.get_rect(topleft=(x_persona, y_persona))
    personagem_rect = personagem_img.get_rect(topleft=(LARGURA, ALTURA))
    aviao_rect = aviao_img.get_rect(topleft=(aviao_img .get_width(), 280))
    

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

        # ====== Explosão ======
    if explodindo:
        tempo_explosao = tempo_atual - explosao_timer 
        if tempo_atual - explosao_timer < explosao_duracao:
            tela.blit(explosao_img, explosao_pos)
        else:
            explodindo = False
    # ====== BOMBA  ======
    tempo_atual = pygame.time.get_ticks()
    if not bomba_visivel and tempo_atual - bomba_timer > bomba_intervalo:
        bomba_rect.x = random.randint(20, LARGURA - bomba_rect.width)
        bomba_rect.y = 0
        bomba_visivel = True
        bomba_timer = tempo_atual
        bomba_atingiu_chao_em = None

    if bomba_visivel:
        if bomba_rect.y < 420:
            bomba_rect.y += 8
            bomba_rect.x += random.choice([-1, 0, 1])
            bomba_rect.x = max(0, min(LARGURA - bomba_rect.width, bomba_rect.x))
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

    # Obstáculos
    tempo_atual = pygame.time.get_ticks()
    if tempo_atual - ultimo_obstaculo > 1500:
        tipo = random.choice(["tanque", "aviao"])
        if tipo == "tanque":
            obstaculos.append(["tanque", LARGURA, 420])
        else:
            obstaculos.append(["aviao", LARGURA, 420])
        ultimo_obstaculo = tempo_atual

     # Desenho e lógica dos obstáculos
    for o in list(obstaculos):
        if o[0] == "tanque":
            tela.blit(tanque_img, (o[1], o[2]))
            rect_obs = tanque_img.get_rect(topleft=(o[1], o[2]))
            o[1] -= 10
        else:
            tela.blit(aviao_img, (o[1], o[2]))
            rect_obs = aviao_img.get_rect(topleft=(o[1], o[2]))
            o[1] -= 10

    # Verificação de colisão
        if rect_persona.colliderect(rect_obs):
            som_colisao.play()
            rodando = False

    # Verifica se saiu da tela e soma pontos
        if o[1] < -200:
            obstaculos.remove(o)
            pontuacao += 1

    # Pontuação
    velocidade_mps = 10  # Velocidade do personagem em metros por segundo
    fonte = pygame.font.SysFont("arial", 36)
    texto_pontuacao = fonte.render(f"Pontuação: {pontuacao}", True, (255, 255, 255))
    tela.blit(texto_pontuacao, (10, 10))
    tempo_decorrido = tempo_atual - inicio_tempo
    distancia_metros = int(tempo_decorrido / 1000 * velocidade_mps)
    texto_distancia = fonte.render(f"Distância: {distancia_metros} m", True, (255, 255, 255))
    tela.blit(texto_distancia, (10, 40))


    # Eventos
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE and not pulo:
            # Código para pular
                pulo = True
                som_pulo.play()
            


        

    pygame.display.update()

# Game Over, fim de jogo
while True:
    tela_fim_jogo(tela, fonte_pontuacao, pontuacao, salvar_log, nome)
    tela.blit(fundoGameOver, (0, 0))
    tela.blit(fonte_titulo.render("The Last Knight Game", True, (128, 128, 128)), (250, 100))
    tela.blit(fonte_titulo.render("Você perdeu!", True, (255, 0, 0)), (400, 200))
    tela.blit(fonte_titulo.render("Pressione ENTER para jogar novamente ou ESC para sair", True, (255, 255, 0)), (150, 300))
    pygame.display.update()

    # Reinicializa variáveis principais para recomeçar o jogo
    x_persona = 80
    y_persona = 330
    vel_pulo = 20
    gravidade = 1
    pulo = False
    vel_y = vel_pulo
    frame_index = 0
    frame_contador = 0
    obstaculos = []
    pontuacao = 0
    rodando = True
    inicio_tempo = pygame.time.get_ticks()
    ultimo_obstaculo = pygame.time.get_ticks()

    # Reinicia loop principal
    break  # <-- Apenas para sair do while e deixar rodar novamente se necessário