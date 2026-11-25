from mlx import Mlx


def mymouse(button, x, y, mystuff):
    print(f"Got mouse event! button {button} at {x},{y}.")


def mykey(keynum, mystuff):
    print(f"Got key {keynum}, and got my stuff back:")
    print(mystuff)
    if keynum == 32:
        m.mlx_mouse_hook(win_ptr, None, None)


def gere_close(dummy):
    m.mlx_loop_exit(mlx_ptr)


options = {
    "[SPACE]": "Generate a new Maze",
    "[R]": "Show / Hide Resolution",
    "[C]": "Change Maze Color"
    }
menu_options = " | ".join(
    f"{key} {value}" for key, value in options.items())


m = Mlx()
mlx_ptr = m.mlx_init()
win_ptr = m.mlx_new_window(mlx_ptr, 1920, 1080, "win title")
m.mlx_clear_window(mlx_ptr, win_ptr)
m.mlx_string_put(mlx_ptr, win_ptr, 20, 20, 0xffffff, menu_options)
(ret, w, h) = m.mlx_get_screen_size(mlx_ptr)
print(f"Got screen size: {w} x {h} .")

stuff = [1, 2]
m.mlx_mouse_hook(win_ptr, mymouse, None)
m.mlx_key_hook(win_ptr, mykey, stuff)
m.mlx_hook(win_ptr, 33, 0, gere_close, None)

m.mlx_loop(mlx_ptr)

# deactivate
# source venv/bin/activate
# python3 -m venv venv

import time

self.animating = False       # Diz se a animação está ativa
self.path_index = 0          # Qual passo do caminho está sendo desenhado agora
self.last_step_time = 0.0    # Hora em que o último passo foi desenhado
self.step_delay = 0.05       # Velocidade: 0.05s = 20 passos por segundo (use 1.0 para 1 segundo)


def update_loop(param: Any) -> None:
    if not self.animating or not self.resolution:
        return

    now = time.time()
    # Só desenha o próximo passo se já passou o tempo do delay
    if now - self.last_step_time >= self.step_delay:
        if self.path_index < len(self.resolution):
            # Pega apenas o passo atual
            passo_atual = self.resolution[self.path_index]
            
            # Desenha só esse passo no buffer da imagem
            self.draw_single_step(passo_atual) 
            
            # Atualiza a imagem na janela
            self.mlx.mlx_put_image_to_window(
                self.mlx_ptr, self.win_ptr, self.img_ptr,
                start_width, start_height)
            
            self.path_index += 1
            self.last_step_time = now
        else:
            # Terminou de desenhar o caminho inteiro
            self.animating = False


# Dentro do on_keypress (quando apertar R):
if key == 82 or key == 114:
    if not self.resolution:
        self.resolution = self.generator.resolution(
            self.config.entry, self.config.exit_cell)
        self.path_index = 0
        self.last_step_time = time.time()
        self.animating = True  # Inicia a animação no loop!
    else:
        self.animating = False
        self.resolution = []
        # Redesenha o labirinto limpo...

# Antes do mlx_loop, registre o loop_hook:
self.mlx.mlx_loop_hook(self.mlx_ptr, update_loop, None)
self.mlx.mlx_loop(self.mlx_ptr)
