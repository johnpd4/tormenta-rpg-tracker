import pandas as pd
import os
import math
from typing import Union
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
        self.atributos = {"for": None, "des": None, "con": None, "int": None, "sab": None, "car": None}
        self.tabela_origem = self.inicializa_tabela_de_origem()

    def print_aviso(self, aviso):
        print("\033[91m" + aviso + "\033[0m")

    def get_classe_principal(self):
        classe = list(self.classes.items())[0][0]
        if classe == None:
            raise Exception("Tentativa de acessar classe principal encontrou None")
        return(classe)

    def get_nível_de_classe(self, classe_match):
        for classe, nível in self.classes.items():
            if classe == classe_match:
                return(nível)
        return(None)
    
    def adiciona_raça(self, raça: str):
        """
        Adiciona ou atualiza a raça do personagem
        raça: str com a raça
        """
        # Importar a lista de raças válidas
        tabela_raças = pd.read_csv("./tabelas/info_raças.csv")
        raças_válidas = tabela_raças["raça"].tolist()
        
        # Testar se a raça é válida
        if raça not in raças_válidas:
            raise Exception("Raça inválida!")
        
        self.raça = raça

    def adiciona_divindade(self, divindade: str):
        """
        Adiciona ou atualiza a divindade
        divindade: str com o nome da divindade
        """
        tabela_divindades = pd.read_csv("./tabelas/info_divindades.csv")
        divindades_válidas = tabela_divindades["divindade"].tolist()
        
        # Testar se a divindade é válida
        if divindades_válidas not in divindades_válidas:
            raise Exception("Divindade inválida!")
        
        self.divindade = divindade

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

        for _, linha in tabela_pericias.iterrows():
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

    def inicializa_tabela_de_origem(self):
        return(pd.DataFrame(columns = ["nome", "origem", "prioridade", "automático", "referência", "bônus_em", "valor_bônus",
                                        "efeito_bônus", "condição", "restrição_classe", "restrição_raça", "restrição_nível",
                                        "restrição_poderes", "restrição_divindade", "restrição_perícia", "restrição_magia",
                                        "restrição_atributo"]))

    # TODO: Lembrar de atualizar essa porra horrível
    def adiciona_linha_tabela_de_origem(self,
                                        nome,
                                        origem,
                                        prioridade,
                                        automático,
                                        referência,
                                        bônus_em = None,
                                        valor_bônus = None,
                                        efeito_bônus = None,
                                        condição = None,
                                        restrição_classe = None,
                                        restrição_raça = None,
                                        restrição_nível = None,
                                        restrição_poderes = None,
                                        restrição_divindade = None,
                                        restrição_perícia = None,
                                        restrição_magia = None,
                                        restrição_atributo = None):
        dict_para_df = {"nome": [nome],
                        "origem": [origem],
                        "prioridade": [prioridade],
                        "bônus_em": [bônus_em],
                        "valor_bônus": [valor_bônus],
                        "efeito_bônus": [efeito_bônus],
                        "condição": [condição],
                        "restrição_classe": [restrição_classe],
                        "restrição_raça": [restrição_raça],
                        "restrição_nível": [restrição_nível],
                        "restrição_poderes": [restrição_poderes],
                        "restrição_divindade": [restrição_divindade],
                        "restrição_perícia": [restrição_perícia],
                        "restrição_magia": [restrição_magia],
                        "restrição_atributo": [restrição_atributo],
                        "automático": [automático],
                        "referência": [referência]}

        tabela_origem = pd.DataFrame.from_dict(data = dict_para_df)
        self.tabela_origem = pd.concat([self.tabela_origem, tabela_origem], ignore_index = True)
        
    def calcula_atributos_iniciais(self, método: str, valores: dict):
        """
        Calcula os atributos baseado ou no negocio de dados ou em valores.
        Só leva em consideração a raça do jogador.
        método: str que identifica se os stats são pra ser feitos por
        rolagem ou por pontos
        valores: dict dicionario de valores ou valores da rolagem.
        """
        # Checar se no dicionario tem os stats certos
        if self.atributos.keys() != valores.keys():
            raise Exception("Dicionário de valores usados para calcular os atributos não contém as chaves corretas!")

        atributos_calculados = dict()

        # Método dos pontos
        if método == "pontos":            
            aux = 0
            for atributo, valor in valores.items():
                # Ver se todos os valores são válidos
                match valor:
                    case -1:
                        aux += -1
                    case 0:
                        aux += 0
                    case 1:
                        aux += 1
                    case 2:
                        aux += 2
                    case 3:
                        aux += 4
                    case 4:
                        aux += 7
                    case _:
                        raise Exception("Valor inválido ao calcular os atributos básicos com o método de pontos!")
                
                atributos_calculados.update({atributo: valor})
                
            # Se os números são sub-ótimos mandar um aviso, se forem melhores do que poderia
            # ser possível dar um erro
            if aux > 10:
                raise Exception("Soma dos valores ao calcular os atributos básicos com o método de pontos excedeu 10!")
            if aux < 10:
                self.print_aviso("Soma dos valores ao calcular os atributos básicos com o método de pontos foi menor que 10")
                        
        # Método dos dados
        elif método == "rolagens":
            for atributo, valor in valores.items():
                if valor < 3 or valor > 18:
                    raise Exception("Valor inválido para calcular os atributos básicos com o método das rolagens!")

                atributos_calculados.update({atributo: math.floor(max((valor - 10) / 2, -2))})

            if sum(atributos_calculados.values()) < 6:
                self.print_aviso("Soma dos atributos rolados foi menor que 6, pode-se re-rolar o menor")
        else:
            raise Exception("Método de cálculo de atributos básicos inválido!")

        for atributo, valor in atributos_calculados.items():
            self.atributos.update({atributo: valor})
            self.adiciona_linha_tabela_de_origem(nome = "".join(["Atributos básicos do método de ", método]),
                                                origem = "".join([método.capitalize(), " iniciais"]),
                                                prioridade = 1,
                                                bônus_em = atributo,
                                                valor_bônus = valor,
                                                automático = "Sim",
                                                referência = "Tormenta 20: Jogo do Ano, página 17")

    def adiciona_atributos_raça(self, pontos_livres: Union[dict, None]):
        if self.raça == None:
            raise Exception("A tentativa de calcular atributos de raça encontrou None ao invés de uma raça válida!")

        if pontos_livres == None:
            pontos_livres = {"for": 0, "des": 0, "con": 0, "int": 0, "sab": 0, "car": 0}

        valor_dois_presente = False

        for _, valor in pontos_livres.items():
            if valor < 0:
                raise Exception("Não se pode ter um ponto livre de raça negativo!")
            if valor > 1:
                valor_dois_presente = True

        # Pegar os atributos de raça
        tabela_raças = pd.read_csv("./tabelas/info_raças.csv")
        atributos_raça = tabela_raças[tabela_raças["raça"] == self.raça]
        print(atributos_raça)

        quantidade_pontos_livres = atributos_raça["pontos_livres"].tolist().pop()
        permite_mais_2 = atributos_raça["permite_mais_2"].tolist().pop()
        restrição_pontos_livres = atributos_raça["restrição_pontos_livres"].tolist().pop()
        referência = atributos_raça["referência"].tolist().pop()

        print("atributos_raça['for']: ", atributos_raça["for"])
        print("atributos_raça['for'].tolist().pop(): ", atributos_raça["for"].tolist().pop())

        atributos_raça = {"for": atributos_raça["for"].tolist().pop(), "des": atributos_raça["des"].tolist().pop(),
                          "con": atributos_raça["con"].tolist().pop(), "int": atributos_raça["int"].tolist().pop(),
                          "sab": atributos_raça["sab"].tolist().pop(), "car": atributos_raça["car"].tolist().pop()}

        if permite_mais_2 != "Sim" and valor_dois_presente:
            raise Exception("Tentativa de atribuir um valor de ponto livre maior que um quando a raça não permite!")

        if quantidade_pontos_livres > sum(pontos_livres.values()):
            self.print_aviso("Nem todos os pontos livres de atributos da raça foram atribuídos")
        elif quantidade_pontos_livres < sum(pontos_livres.values()):
            raise Exception("Mais pontos livres foram atribuídos do que tinham disponíveis!")

        for atributo, _ in self.atributos.items():
            if atributo in restrição_pontos_livres:
                self.print_aviso("Pontos livres alocados para um atributo inválido para essa raça. Pontos não foram atribuídos")
                continue
            self.atributos[atributo] += atributos_raça[atributo] + pontos_livres[atributo]
            if atributos_raça[atributo] != 0:
                self.adiciona_linha_tabela_de_origem(nome = "".join([atributo.capitalize(), " da raça ", self.raça]),
                                                    origem = "".join(["Raça ", self.raça]),
                                                    prioridade = 1,
                                                    bônus_em = atributo,
                                                    valor_bônus = atributos_raça[atributo],
                                                    restrição_raça = self.raça,
                                                    automático = "Sim",
                                                    referência = referência)
            if pontos_livres[atributo] != 0:
                self.adiciona_linha_tabela_de_origem(nome = "".join([atributo.capitalize(), " de pontos livres da raça ", self.raça]),
                                                    origem = "".join(["Raça ", self.raça]),
                                                    prioridade = 1,
                                                    bônus_em = atributo,
                                                    valor_bônus = pontos_livres[atributo],
                                                    restrição_raça = self.raça,
                                                    automático = "Sim",
                                                    referência = referência)

    def poderes_disponíveis(self):
        """
        Pegar a giga-gigante tabela de todos os poderes e fazer um subset daqueles que estão
        disponíveis para o personagem atual
        """
        tabela_poderes = pd.read_csv("./tabelas/info_poderes.csv")
        tabela_poderes = tabela_poderes.replace({float("nan"): None})
        
        # Iterar pelas linhas para testar as restrições
        for _, row in tabela_poderes.iterrows():

            poder_restrito = True
            classe_do_poder = None
            # TODO: shit still doesnt work, a maneira q os testes estão estruturados ainda é uma merda
            if row["restrição_classe"] is not None:
                for classe in self.classes.keys():
                    if classe == row["restrição_classe"]:
                        poder_restrito = False
                        classe_do_poder = classe

            if row["restrição_nível"] is not None:
                if classe_do_poder is not None:
                    if self.get_nível_de_classe(classe_do_poder) < row["restrição_nível"]:
                        poder_restrito = False
                else:
                    for nível in self.classes.values():
                        if nível < row["restrição_nível"]:
                            poder_restrito = False
            
            if not poder_restrito:
                self.tabela_origem.loc[self.tabela_origem.last_valid_index() + 1] = row


teste = personagem(nome_personagem = "NOME_PERSONAGEM", jogador = "JOGADOR")

teste.calcula_atributos_iniciais(método = "rolagens", valores = {"for": 18, "des": 17, "int": 13, "con": 13, "sab": 8, "car": 18})

teste.adiciona_raça("Elfo")
#teste.adiciona_atributos_raça(pontos_livres = {"for": 1, "des": 1, "int": 0, "con": 1, "sab": 0, "car": 0})
teste.adiciona_atributos_raça(pontos_livres = None)
#print(teste.atributos)

# for atributo, valor in teste.atributos.items():
#     print(atributo, ": ", valor)

#print("teste.tabela_origem: \n", teste.tabela_origem)

teste.tabela_origem.to_csv("tabela_teste.csv")

teste.adiciona_classe({"Bárbaro": 10})

teste.adiciona_classe({"Lutador": 9})

teste.poderes_disponíveis()

teste.tabela_origem.to_csv("tabela_teste.csv")

#print(teste.classes.keys())

#aaah = teste.poderes_disponíveis()
#print(aaah)

# print(teste.perícias_das_classes())

# print(teste.classes)

# print(teste.perícias_das_classes())

# print(teste.classes)

# teste.adiciona_classe({"Arcanista": 1})

# print(teste.classes)

# teste_lista = list(teste.classes)
# print(teste_lista)
# print(teste_lista[0])

# print(teste.classes)

# print(teste.get_classe_principal())

# teste_pv = teste.calcula_pv_das_classes()
# print(teste_pv)

# teste_pm = teste.calcula_pm_das_classes()
# print(teste_pm)