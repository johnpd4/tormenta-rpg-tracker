from classe_personagem import personagem  
import pandas as pd
import re

# Passo 1:
# Coloque o nome do personagem e jogador (até agora, nada usa essa informação)
teste = personagem(nome_personagem = "NOME_PERSONAGEM", jogador = "JOGADOR")

# Passo 2:
# Adicone sua classe(s)
teste.adiciona_classe({"Lutador": 9})
teste.adiciona_classe({"Arcanista": 2})

# Passo 3:
# Adicione seus atributos iniciais. Temos o método das rolagens e o método dos pontos.
# Para mais info: Tormenta 20: Jogo do Ano, página 17
teste.calcula_atributos_iniciais(método = "rolagens", valores = {"for": 18, "des": 17, "int": 15, "con": 13, "sab": 8, "car": 18})

# Passo 4:
# Escolha sua raça
teste.adiciona_raça("Humano")

# Passo 5:
# Alocar os pontos livres da raça.
# NOTA: se sua raça não tem pontos livres, troque a linha abaixo pela com "None" nos pontos livres
teste.adiciona_atributos_raça(pontos_livres = {"for": 0, "des": 1, "con": 1, "int": 1, "sab": 0, "car": 0})
# teste.adiciona_atributos_raça(pontos_livres = None)

# Passo 6:
# Adicione sua divindade
teste.adiciona_divindade("Valkaria")

# Passo 7:
# Adicone os PODERES DE AUMENTO DE ATRIBUTO, EXCLUSIVAMENTE. Nenhum outro tipo de poder.
lista = ["Aumento de Atributo (+1 for)",
         "Aumento de Atributo (+2 for)",
         "Aumento de Atributo (+3 for)"]

teste.adiciona_lista_para_tabela_origem(tabela_generalizada = teste.get_tabela("poderes_atributos"),
                                        lista_selecionados = lista)

teste.interpreta_tabela_de_origem()

teste.adiciona_atributos_de_combate()


# Passo 8:
# Selecione suas perícias. Temos 3 tipos:
# perícias_alt_selecionadas: Perícias que podem ser selecionadas quando sua classe pede para escolher entre duas perícias como obrigatória
# perícias_op_selecionadas: Perícias selecionadas da lista de perícias opcionais
# perícias_livres_selecionadas: Perícias quaisquer, com número limitado pela sua inteligência
teste.selecionar_perícias(perícias_livres_selecionadas = ["Ladinagem", "Luta", "Intimidação"],
                          perícias_op_selecionadas = ["Cavalgar", "Guerra"])

tabela_poderes = pd.read_csv("./tabelas/info_poderes.csv")
tabela_poderes = tabela_poderes.replace({float("nan"): None})
tabela_poderes = tabela_poderes.sort_values(by = "prioridade", axis = 0, ascending = False)

# Passo 9:
# Selecione seus poderes. No momento apenas os poderes presentes na tabela "info_poderes.csv" na pasta de tabelas estão presentes.
# Isso inclui, no momento, apenas alguns poderes de lutador. Se quiseres por poderes para seu personagem cheque o arquivo
# "como_contribuir.txt"
lista = ["Braços Calejados", "Até Acertar", "Língua dos Becos", "Casca Grossa"]
teste.adiciona_lista_para_tabela_origem(tabela_generalizada = tabela_poderes, lista_selecionados = lista)

teste.interpreta_tabela_de_origem()

# Resultado:
# Mostra os atributos básicos, de combate + duas tabelas mostrandos todas suas perícias e todos seus poderes
print(teste.atributos)
print(teste.atributos_combate)
print(teste.tabela_origem)
print(teste.tabela_perícias)

# Tabelas também podem ser salvas para poder vê-las melhor em outro aplicativo
teste.tabela_origem.to_csv("tabela_origem_teste.csv")
teste.tabela_perícias.to_csv("tabela_perícias_teste.csv")