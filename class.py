import pandas as pd
import os
from pathlib import Path

os.chdir(Path(__file__).resolve().parent)

class personagem:
    def __init__(self, nome_personagem: str, jogador: str) -> None:
        """
        nome_personagem: string do nome do personagem para display
        jogador: string do nome do jogador
        """
        self.nome_personagem = nome_personagem
        self.jogador = jogador
        self.divindade = None
        self.raça = None
        self.classes = dict()
        # TODO: para os atributos seria ideal ter uma lista de todas as fontes
        # de aumento de atributos, e somar apenas quando necessário
        #self.atributos =

    def get_classe_principal(self):
        classe = list(self.classes.items())[0][0]
        if classe == None:
            raise Exception("Tentativa de acessar classe principal encontrou None")
        return(classe)
    
    def adiciona_raça(self, raça: str):
        """
        Adiciona ou atualiza a raça do personagem
        raça: str com a raça
        """
        # Importar a lista de raças válidas
        tabela_raças = pd.read_csv("./tabelas/info_classes.csv")
        raças_válidas = tabela_raças["raça"].tolist()
        
        # Testar se a divindade é válida
        if raça not in raças_válidas:
            raise Exception("Raça inválida!")
        
        self.raça = raça
        return(self)

    def adiciona_divindade(self, divindade: str):
        """
        Adiciona ou atualiza a divindade
        divindade: str com o nome da divindade
        """
        # TODO: Colocar aqui hard coded a lista de classes é ruim
        # econtrar algum arquivo pra por ela e chamar aqui
        divindades_válidas = ["Aharadak", "Allihanna", "Arsenal"]
        
        # Testar se a divindade é válida
        if divindades_válidas not in divindades_válidas:
            raise Exception("Divindade inválida!")
        
        self.divindade = divindade
        return(self)

    def adiciona_classe(self, classe: dict):
        """
        Adiciona ou atualiza uma ou mais classes
        classe: dict que contém classe e nível
        """
        # Importar a lista de classes válidas
        tabela_classes = pd.read_csv("./tabelas/info_classes.csv")
        classes_válidas = tabela_classes["classe"].tolist()

        # Testar se a classe e o nível dados são validos pra por na classe
        for classe, nível in classe.items():
            if nível < 1 or nível > 20:
                raise Exception("Nível para uma classe deve estar entre 1 e 20!")
            if classe not in classes_válidas:
                raise Exception("Classe dada não está dentre as classes válidas!")
            self.classes.update([(classe, nível)])

        # Mesmo sendo válidos por sí só, podem introduzir erro com o que já estava lá
        # testar se nenhuma condição foi ferida
        contador_níveis = 0
        for classe, nível in self.classes.items():
            contador_níveis += nível
            #print("contador_níveis:", contador_níveis)
            if contador_níveis > 20:
                raise Exception("Níveis total de todas as classes não podem ser maiores que 20!")
        return(self)

    def calcula_pv_das_classes(self):
        """
        Calcula a quantidade de pv's de um jogador.
        Só leva em consideração a classe do jogador.
        """
        # Chamar a tabela de info e transformar em dicts
        tabela_classes = pd.read_csv("./tabelas/info_classes.csv")
        pv_base = dict(zip(tabela_classes["classe"], tabela_classes["pv_base"]))
        pv_por_nível = dict(zip(tabela_classes["classe"], tabela_classes["pv_por_nível"]))

        # Adicionar pvs base
        lista_classes = list(self.classes.copy())
        pv = pv_base[lista_classes[0]] # TODO: por Constituição aqui

        # Adicionar pvs de nível
        for classe, nível in self.classes.items():
            pv += pv_por_nível[classe] * nível # TODO: por Constituição aqui

        return(pv) # TODO: Adicionar dados de atribuição daonde veio os stats

    def calcula_pm_das_classes(self):
        """
        Calcula a quantidade de pm's de um jogador.
        Só leva em consideração a classe do jogador.
        """
        # Chamar a tabela de info e transformar em dicts
        tabela_classes = pd.read_csv("./tabelas/info_classes.csv")
        pm_por_nível = dict(zip(tabela_classes["classe"], tabela_classes["pm_por_nível"]))

        pm = 0
        for classe, nível in self.classes.items():
            pm += pm_por_nível[classe] * nível

        return(pm) # TODO: Adicionar dados de atribuição daonde veio os stats

    def perícias_das_classes(self):
        """
        Retorna uma tabela com todas as perícias do jogo com flags de obrigatória,
        alternativa, e treinável
        """
        classe = self.get_classe_principal()

        tabela_classes = pd.read_csv("./tabelas/info_classes.csv")        
        tabela_pericias = pd.read_csv("./tabelas/info_pericias.csv")

        pericias_obg = tabela_classes.loc[tabela_classes["classe"] == classe]["pericias_obg_str"][0].split("|")
        pericias_alt = tabela_classes.loc[tabela_classes["classe"] == classe]["pericias_alt_str"][0].split("|")
        pericias_op = tabela_classes.loc[tabela_classes["classe"] == classe]["pericias_op_str"][0].split("|")

        vetor_auxiliar = []

        for indice, linha in tabela_pericias.iterrows():
            if linha["pericia"] == "Nenhuma":
                vetor_auxiliar.append("-")
                continue
            if linha["pericia"] in pericias_obg:
                vetor_auxiliar.append("Obrigatória")
            elif linha["pericia"] in pericias_alt:
                vetor_auxiliar.append("Alternativa")
            elif linha["pericia"] in pericias_op:
                vetor_auxiliar.append("Opcional")
            else:
                vetor_auxiliar.append("-")
        
        tabela_pericias["pericias_do_jogador"] = vetor_auxiliar
        
        return(tabela_pericias)
        

    def calcula_atributos_raça(self, método: str, valores: dict):
        """
        Calcula os atributos baseado ou no negocio de dados ou em valores.
        Só leva em consideração a raça do jogador.
        método: str que identifica se os stats são pra ser feitos por
        rolagem ou por pontos
        valores: dict dicionario de valores ou valores da rolagem.
        """
        # # Pegar os atributos de raça
        # tabela_raças = pd.read_csv("./tabelas/info_raças.csv")

        # # Método dos pontos
        # if método == "pontos":
        #     valores_mod = valores
        # # Método dos dados
        # elif método == "rolagens":
        #     for atributo, valor in valores:
        #         valores[atributo] = 
        # else:
        #     raise Exception("Método de cálculo dos atributos de raça inválido!")

teste = personagem(nome_personagem = "NOME_PERSONAGEM", jogador = "JOGADOR")

# print(teste.perícias_das_classes())

print(teste.classes)

teste.adiciona_classe({"Arcanista": 9})

print(teste.perícias_das_classes())

print(teste.classes)

teste.adiciona_classe({"Arcanista": 1})

print(teste.classes)

teste_lista = list(teste.classes)
print(teste_lista)
print(teste_lista[0])

teste.adiciona_classe({"Bárbaro": 10})
print(teste.classes)

print(teste.get_classe_principal())

teste_pv = teste.calcula_pv_das_classes()
print(teste_pv)

teste_pm = teste.calcula_pm_das_classes()
print(teste_pm)