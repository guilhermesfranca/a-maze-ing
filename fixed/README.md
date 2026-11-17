*This project has been created as part of the 42 curriculum by <login>.*

Substitua `<login>` pelos logins reais da equipe antes da entrega.

## Description

Gerador de labirintos em Python 3.10+ com visualização MiniLibX para Linux.
O algoritmo principal é DFS iterativo com backtracking aleatório. Ele foi
escolhido por ser simples de explicar, gerar uma árvore sem ciclos e não
depender da profundidade de recursão do Python. No modo imperfeito, paredes
são removidas para reduzir becos sem saída, sem criar áreas abertas 3×3.

## Instructions

Use Linux com sessão gráfica X11, suporte Vulkan e as dependências da MLX
disponíveis na máquina. O pacote incluído em `vendor/` é o wheel MLX 2.2
Linux x86-64 fornecido localmente; em outra arquitetura ou se bibliotecas
nativas estiverem ausentes, compile o `mlx_CLXV` disponibilizado pela 42 e
instale o wheel gerado. Não instale `mlx` diretamente do PyPI: é outro projeto.

```sh
make install
python3 a_maze_ing.py config.txt
make test
make lint
make package
```

`make run CONFIG=outro.txt` executa outra configuração; `make debug` usa pdb.
`make install MLX_WHEEL=/caminho/para/mlx-2.2-py3-none-any.whl` usa outro
wheel. O pacote `mazegen-*.whl` pode ser instalado com pip.

Controles: espaço regenera e atualiza o arquivo de saída; P mostra/esconde
o caminho mais curto; C muda a cor das paredes; Esc ou fechar a janela encerra.
Entrada é amarela, saída verde e o 42 azul.

## Configuration

Uma opção `KEY=VALUE` por linha; linhas vazias e linhas iniciadas por `#` são
ignoradas. Chaves repetidas ou desconhecidas são rejeitadas.

```text
WIDTH=30
HEIGHT=30
ENTRY=0,0
EXIT=29,29
OUTPUT_FILE=maze.txt
PERFECT=True
SEED=42
```

As seis primeiras chaves são obrigatórias. `SEED` é opcional e deve ser um
inteiro; a mesma seed e sequência de ações produzem os mesmos labirintos.
Coordenadas são `(x,y)`, a partir de zero. Entrada e saída devem ser distintas,
estar dentro da grade e fora do 42. A largura e altura devem ser pelo menos 2.
O 42 é omitido com aviso em dimensões menores que 9×7. No modo imperfeito,
dimensões que não permitam um tabuleiro válido produzem mensagem de erro.

O arquivo de saída contém uma linha hexadecimal por linha da grade, depois uma
linha vazia, entrada, saída e caminho mínimo em letras `N`, `E`, `S`, `W`.
Bits 1, 2, 4 e 8 representam respectivamente paredes norte, leste, sul e oeste.

## Reusable generator

`mazegen` é independente de MLX. Instale o wheel `mazegen-*.whl` ou use o
pacote no diretório do projeto:

```python
from mazegen import MazeGenerator

generator = MazeGenerator(width=20, height=15, seed=42)
maze = generator.generate(entry=(0, 0), exit=(19, 14), perfect=True)
print(maze.walls)            # máscaras de paredes por linha
print(maze.blocked)          # células reservadas para o 42
print(maze.shortest_path())  # caminho mínimo, por exemplo "EESS..."
print(maze.to_text())        # formato do arquivo do subject
```

Chamadas sucessivas ao mesmo gerador avançam seu estado aleatório. Criar outro
com os mesmos parâmetros e seed reproduz a sequência.

## Resources

- Subject A-Maze-ing v2.3.
- [MiniLibX Python: documentação e instalação](https://github.com/SaraFreitas-dev/MinilibX-42-Pyhton-Documentation).
- [Projeto de referência](https://github.com/SaraFreitas-dev/A-Maze-ing).
- [Python: collections.deque](https://docs.python.org/3/library/collections.html#collections.deque).
- IA foi usada na análise do subject, implementação inicial, documentação e
  testes; a equipe deve revisar, compreender e validar o código.

## Team and project management

Preencher antes da entrega: logins, funções dos membros, planejamento
inicial e alterações, o que funcionou, o que melhorar e ferramentas usadas.
