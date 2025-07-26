from classe_personagem import personagem  
import pandas as pd
import re

# Passo 1:
teste = personagem(nome_personagem = "NOME_PERSONAGEM", jogador = "JOGADOR")

# Passo 2:
teste.adiciona_classe({"Lutador": 5})

teste.calcula_atributos_iniciais(método = "rolagens", valores = {"for": 18, "des": 17, "int": 15, "con": 13, "sab": 8, "car": 18})

teste.adiciona_raça("Humano")

teste.adiciona_divindade("Valkaria")

teste.adiciona_atributos_raça(pontos_livres = {"for": 0, "des": 1, "con": 1, "int": 1, "sab": 0, "car": 0})

teste.interpreta_tabela_de_origem()

print(teste.atributos)

#teste.adiciona_lista_para_tabela_origem()

#print("int: ", teste.get_atributo("int"))

teste.selecionar_perícias(perícias_livres_selecionadas = ["Ladinagem", "Luta", "Intimidação"],
                          perícias_op_selecionadas = ["Cavalgar", "Guerra"])

# print(teste.tabela_perícias)
# print(teste.get_perícias_treinadas())

# print(teste.get_poderes_do_personagem())

# print(teste.tabela_origem)

tabela_poderes = pd.read_csv("./tabelas/info_poderes.csv")
tabela_poderes = tabela_poderes.replace({float("nan"): None})
tabela_poderes = tabela_poderes.sort_values(by = "prioridade", axis = 0, ascending = False)

lista = ["Braços Calejados", "Até Acertar", "Língua dos Becos"]

teste.tabela_origem.to_csv("tabela_teste.csv")

teste.adiciona_lista_para_tabela_origem(tabela_generalizada = tabela_poderes, lista_selecionados = lista)

teste.interpreta_tabela_de_origem()

print(teste.atributos)

# print(teste.get_poderes_do_personagem())

#teste.tabela_origem.to_csv("tabela_teste.csv")

# string = "for:1"

# lista_stats = string.split("|")

# print(lista_stats)

# for string_atr in lista_stats:
#     atributo, valor = string_atr.split(":")
#     print("atributo: ", atributo)
#     print("valor: ", valor)