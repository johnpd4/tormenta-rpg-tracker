import pandas as pd
import os
import numpy as np
import math
from typing import Union
from pathlib import Path
import re

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
        self.atributos = self.inicializa_atributos()
        self.atributos_combate = self.inicializa_atributos_combate()
        self.tabela_perícias = None
        self.tabela_origem = self.inicializa_tabela_de_origem()
        self.num_poderes_disponíveis = None

    def adiciona_atributo(self, atributo: str, valor: int):
        #print("atributo: ", atributo)
        #print("self.tabela_perícias.columns: ", self.tabela_perícias["perícia"].values)
        if atributo in self.atributos.keys():
            valor_novo = self.atributos.get(atributo) + valor
            self.atributos.update({atributo: valor_novo})
            return
        if self.tabela_perícias is not None:
            if atributo in self.tabela_perícias["perícia"].values:
                tabela_perícias = self.tabela_perícias
                row = tabela_perícias[tabela_perícias["perícia"] == atributo]
                valor_novo = row["bônus_outro"].values + valor
                tabela_perícias.loc[tabela_perícias["perícia"] == atributo, "bônus_outro"] = valor_novo
                self.tabela_perícias = tabela_perícias
                return
        if atributo in self.atributos_combate.keys():
            valor_novo = self.atributos_combate.get(atributo) + valor
            self.atributos_combate.update({atributo: valor_novo})
            return

    def auto_rolagem_inicial(self, prioridades: list):
        i = 1
        tentativa = 0
        while True:
            dados = []
            tentativa += 1
            lista_atr = []
            lista_soma = []
            print("=============\nTentativa de rolagens ", tentativa)
            for i in range(6):
                roll = np.array(np.random.choice(6, 4) + 1)
                roll.sort()
                dados.append(roll[[1, 2, 3]])
                print("Dados rodados pro atributo ", i+1, ":", roll)
                print("Tira o menor: ", dados[i])
                soma = sum(roll[[1, 2, 3]])
                atr = math.floor(max((soma - 10) / 2, -2))
                print("Soma e valor correspondente: ", soma, atr, "\n#")
                lista_soma.append(soma)
                lista_atr.append(atr)

            lista_atr.sort(reverse = True)
            lista_soma.sort(reverse = True)
            print("Soma total dos atr: ", sum(lista_atr))
                
            if sum(lista_atr) >= 6:
                print("Soma maior que 6! Atributos finais: ", lista_atr)
                return(dict(zip(prioridades, lista_soma)))
            else:
                print("Soma menor que 6! Re-rolando...")

    def print_aviso(self, aviso: str):
        """
        Printa um aviso colorido para quando o usuário fizer algo sub-optimal
        aviso: str pra printar
        """
        print("\033[91m" + aviso + "\033[0m")

    def get_classe_principal(self):
        """
        Pega a classe principal de um personagem, isso é, a primeira classe
        """
        classe = list(self.classes.items())[0][0]
        if classe == None:
            raise Exception("Tentativa de acessar classe principal encontrou None")
        return(classe)

    def get_tabela(self, tabela):
        if tabela == "classes":
            return(pd.read_csv("./tabelas/info_classes.csv"))
        if tabela == "divindades":
            return(pd.read_csv("./tabelas/info_divindades.csv"))
        if tabela == "perícias":
            return(pd.read_csv("./tabelas/info_perícias.csv"))
        if tabela == "poderes":
            return(pd.read_csv("./tabelas/info_poderes.csv"))
        if tabela == "poderes_atributos":
            return(pd.read_csv("./tabelas/info_poderes_atributos.csv"))
        if tabela == "raças":
            return(pd.read_csv("./tabelas/info_raças.csv"))
        else:
            return(None)

    def get_nível_de_classe(self, classe: str):
        """
        Pega o nível de uma classe do personagem
        classe: str classe da qual o nível deve ser pego
        """
        if classe.lower == "total":
            return(self.get_nível_total())
        for classe_dict, nível in self.classes.items():
            if classe_dict == classe:
                return(nível)
        return(None)

    def get_lista_perícias(self):
        return(self.get_tabela("perícias")["perícia"].tolist())
    
    def get_lista_atributos(self):
        return(list(self.inicializa_atributos().keys()))
    
    def get_lista_atributos_combate(self):
        return(list(self.inicializa_atributos_combate().keys()))

    def adiciona_raça(self, raça: str):
        """
        Adiciona ou atualiza a raça do personagem
        raça: str com a raça
        """
        # Importar a lista de raças válidas
        tabela_raças = self.get_tabela("raças")
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
        tabela_divindades = self.get_tabela("divindades")
        divindades_válidas = tabela_divindades["divindade"].tolist()

        #print("divindades_válidas: ", divindades_válidas)
        
        # Testar se a divindade é válida
        if divindade not in divindades_válidas:
            raise Exception("Divindade inválida!")
        
        self.divindade = divindade

    def adiciona_classe(self, classe: dict):
        """
        Adiciona ou atualiza uma ou mais classes
        classe: dict que contém classe e nível
        """
        # Importar a lista de classes válidas
        tabela_classes = self.get_tabela("classes")
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

        self.num_poderes_disponíveis = self.get_num_poderes()
        
    def adiciona_atributos_de_combate(self):
        # Chamar a tabela de info e transformar em dicts
        tabela_classes = self.get_tabela("classes")
        pm_por_nível = dict(zip(tabela_classes["classe"], tabela_classes["pm_por_nível"]))
        classe_referência = dict(zip(tabela_classes["classe"], tabela_classes["referência"]))
        pv_base_lista = dict(zip(tabela_classes["classe"], tabela_classes["pv_base"]))
        pv_por_nível = dict(zip(tabela_classes["classe"], tabela_classes["pv_por_nível"]))
        

        # Adicionar pvs base
        #lista_classes = list(self.classes.copy())
        pv_base = pv_base_lista[self.get_classe_principal()]
        self.adiciona_linha_tabela_de_origem(nome = "".join(["Pontos de Vida Base da Classe ", self.get_classe_principal()]),
                                             origem = "Atributo de Constituição",
                                             prioridade = 1,
                                             bônus_em = "pv",
                                             valor_bônus = pv_base,
                                             restrição_classe = self.get_classe_principal(),
                                             automático = "Sim",
                                             referência = classe_referência[self.get_classe_principal()])

        pv_con = self.get_atributo("con") * self.get_nível_total()
        self.adiciona_linha_tabela_de_origem(nome = "Pontos de Vida de Constituição",
                                             origem = "Atributo de Constituição",
                                             prioridade = 1,
                                             bônus_em = "pv",
                                             valor_bônus = pv_con,
                                             automático = "Sim",
                                             referência = "Tormenta 20: Jogo do Ano, página 35")

        pm_classe = []
        pm_níveis = []
        pv_classe = []
        pv_níveis = []
        pv_classe_referência = []

        # Adicionar pvs de nível
        for classe, nível in self.classes.items():
            pv_classe.append(classe)
            pv_níveis.append(pv_por_nível[classe] * (nível - 1))
            pv_classe_referência.append(classe_referência[classe])
            pm_classe.append(classe)
            pm_níveis.append(pm_por_nível[classe] * nível)

        for classe, pvs, pms, referência in zip(pv_classe, pv_níveis, pm_níveis, pv_classe_referência):
            self.adiciona_linha_tabela_de_origem(nome = "".join(["Pontos de Vida da Classe ", classe]),
                                                 origem = "".join(["Classe ", classe]),
                                                 prioridade = 1,
                                                 bônus_em = "pv",
                                                 valor_bônus = pvs,
                                                 restrição_classe = classe,
                                                 automático = "Sim",
                                                 referência = referência)
            self.adiciona_linha_tabela_de_origem(nome = "".join(["Pontos de Mana da Classe ", classe]),
                                                 origem = "".join(["Classe ", classe]),
                                                 prioridade = 1,
                                                 bônus_em = "pm",
                                                 valor_bônus = pms,
                                                 restrição_classe = classe,
                                                 automático = "Sim",
                                                 referência = referência)

        # Adiciona armadura base
        self.adiciona_linha_tabela_de_origem(nome = "Armadura Básica",
                                                 origem = "Atributos Iniciais",
                                                 prioridade = 1,
                                                 bônus_em = "defesa",
                                                 valor_bônus = 10,
                                                 automático = "Sim",
                                                 referência = "Tormenta 20: Jogo do Ano, página 106")

        # Adiciona destreza na armadura
        self.adiciona_linha_tabela_de_origem(nome = "Armadura da Destreza",
                                                 origem = "Atributos Iniciais",
                                                 prioridade = 1,
                                                 bônus_em = "defesa",
                                                 valor_bônus = self.get_atributo("des"),
                                                 automático = "Sim",
                                                 referência = "Tormenta 20: Jogo do Ano, página 106")

    def perícias_das_classes(self):
        """
        Retorna uma tabela com todas as perícias do jogo com flags de obrigatória,
        alternativa, e treinável
        """
        classe = self.get_classe_principal()

        tabela_classes = self.get_tabela("classes")
        tabela_perícias = self.get_tabela("perícias")

        tabela_classes = tabela_classes.replace({float("nan"): None})
        tabela_perícias = tabela_perícias.replace({float("nan"): None})

        teste = tabela_classes.loc[tabela_classes["classe"] == classe]
        #print(teste["perícias_obg_str"])
        #print("Fortitude" in teste["perícias_obg_str"].to_string)

        linha = tabela_classes.loc[tabela_classes["classe"] == classe]

        perícias_obg = linha["perícias_obg_str"].values[0]
        perícias_alt = linha["perícias_alt_str"].values[0]
        perícias_op = linha["perícias_op_str"].values[0]

        # print("perícias_obg: ", perícias_obg)
        # print("perícias_alt: ", perícias_alt)
        # print("perícias_op: ", perícias_op)

        vetor_auxiliar = []

        for _, linha in tabela_perícias.iterrows():
            # print("perícia: ", linha["perícia"])
            # print("linha[perícia] in perícias_obg: ", linha["perícia"] in perícias_obg)
            # print("linha[perícia] in perícias_alt: ", linha["perícia"] in perícias_alt)
            # print("linha[perícia] in perícias_op: ", linha["perícia"] in perícias_op)
            status_perícia = str()

            if linha["perícia"] in perícias_obg:
                #print("perícia ", linha["perícia"], " é obrigatória")
                status_perícia = "".join([status_perícia, "Obrigatória"])
                vetor_auxiliar.append(status_perícia)
                continue
            if perícias_alt is not None:
                if linha["perícia"] in perícias_alt:
                    #print("perícia ", linha["perícia"], " é alternativa")
                    status_perícia = "".join([status_perícia, "Alternativa"])
            if linha["perícia"] in perícias_op:
                #print("perícia ", linha["perícia"], " é opcional")
                if status_perícia == "":
                    status_perícia = "".join([status_perícia, "Opcional"])
                else:
                    status_perícia = "".join([status_perícia, "|Opcional"])

            if status_perícia == "":
                vetor_auxiliar.append(None)
                continue
            
            vetor_auxiliar.append(status_perícia)

        tabela_perícias["perícias_da_classe"] = vetor_auxiliar
        tabela_perícias = tabela_perícias.sort_values("perícias_da_classe")

        return(tabela_perícias)

    def get_atributo(self, atributo: str):
        # TODO: Atualizar isso para os futuros todos atributos.
        # Não sei ainda se vou colocar tudo do dicionario_stats.txt no dict de atributos
        # ou separar de alguma maneira. Por enquanto fica essa função embrionária.

        return(self.atributos.get(atributo))

    def get_nível_total(self):
        """
        Retorna o nível total do personagem, incluíndo todas as classes
        """
        return(sum(self.classes.values()))

    def get_num_poderes(self):
        """
        Retorna o número de poderes que um personagem pode escolher.
        Todas as classes ganham um poder todo o nível com exceção do nível 1.
        """
        num_poderes = 0
        for _, nível in self.classes.items():
            num_poderes += nível - 1
        return(num_poderes)

    def get_poderes_do_personagem(self):
        return(self.tabela_origem["nome"].unique().tolist())

    def selecionar_perícias(self, perícias_op_selecionadas: list, perícias_livres_selecionadas: list, perícias_alt_selecionadas: Union[str, None] = None):
        """
        perícias_alt_selecionadas: a perícia alternativa selecionada. Apenas uma perícia alternativa pode ser selecionada,
        pois sempre se escolhe uma de duas
        perícias_op_selecionadas: uma lista de perícias para serem selecionadas como opcionais, tamanho limitado pelo número dado
        pela classe principal do personagem
        perícias_livres_selecionadas: uma lista de perícias para serem selecionadas como livres, tamanho limitado pela inteligênica
        do personagem
        Faz todos os cálculos e computações necessárias para as perícias, e atualiza a tabela de perícias do personagem
        """
        tabela_perícias_jogador = self.perícias_das_classes()
        #print(tabela_perícias_jogador)
        tabela_classes = self.get_tabela("classes")
        tabela_classes = tabela_classes[tabela_classes["classe"] == self.get_classe_principal()]
        tabela_classes = tabela_classes.replace({float("nan"): None})

        #print("tabela_classes[perícias_alt_str]: ", tabela_classes["perícias_alt_str"].values[0])

        if tabela_classes["perícias_alt_str"].values[0] is None and perícias_alt_selecionadas is not None:
            raise Exception("Essa classe não suporta perícias alternativas!")

        # O número e perícias opcionais é dado pela classe
        num_perícias_opcionais = tabela_classes["número_perícias_op"].values

        # Perícias livres vêm do seu stat de int, a diferença delas pras
        # opcionais é que pode ser literalmente qualquer perícia
        num_perícias_livres = self.get_atributo("int")
        if num_perícias_livres < 0:
            num_perícias_livres = 0

        if len(perícias_op_selecionadas) > num_perícias_opcionais:
            raise Exception("Foram selecionadas mais perícias opcionais do que a classe permite!\n Você esqueceu de transferir algumas para perícias livres?")
        elif len(perícias_op_selecionadas) == 0:
            self.print_aviso("Nenhuma perícia opcional selecionada.")
        elif len(perícias_op_selecionadas) < num_perícias_opcionais:
            self.print_aviso("Número de perícias opcionais selecionadas foi menor do que o permitido.")

        if len(perícias_livres_selecionadas) > num_perícias_livres:
            raise Exception("Foram selecionadas mais perícias livres do que a inteligência do personagem, ", self.get_atributo("int"), " permite!")
        elif len(perícias_livres_selecionadas) == 0:
            self.print_aviso("Nenhuma perícia livre selecionada.")
        elif len(perícias_livres_selecionadas) < num_perícias_livres:
            self.print_aviso("Número de perícias livres selecionadas foi menor do que o permitido.")

        if any(x in perícias_op_selecionadas for x in perícias_livres_selecionadas):
            self.print_aviso("Têm intersecção entre a lista de perícias opcionais e livres, considere perícias livres diferentes.")

        # Ordem pra processar:
        # 1. Perícias Obrigatórias
        # 2. Perícias Alternativas
        # 3. Perícias Opcionais
        # 4. Perícias Livres

        # O bônus escala de maneira mto bizarra, ent fiz isso
        # fuck you level 14
        if self.get_nível_total != 14:
            bônus_de_treino = 2 * (1 + max(0, math.floor((self.get_nível_total()) / 7)))
        else:
            bônus_de_treino = 4
        perícias_treinadas = []
        bônus_atributo = []
        bônus_treino = []
        bônus_nível = [math.floor(self.get_nível_total() / 2)] * len(tabela_perícias_jogador.index)

        for _, row in tabela_perícias_jogador.iterrows():
            #print(row["perícia"])
            #print(row["perícias_da_classe"])
            bônus_atributo.append(self.get_atributo(row["atributo"]))
            if row["perícias_da_classe"] is not None:
                if row["perícias_da_classe"] == "Obrigatória":
                    #print("Detectou Obrigatória!\n===========")
                    perícias_treinadas.append("Treinado (obg)")
                    bônus_treino.append(bônus_de_treino)
                    continue
                elif row["perícia"] is not None:
                    if "Alternativa" in row["perícias_da_classe"] and row["perícia"] in perícias_alt_selecionadas:
                        #print("Detectou Alternativa Escolhida!\n===========")
                        perícias_treinadas.append("Treinado (alt)")
                        bônus_treino.append(bônus_de_treino)
                        continue
                elif row["perícia"] is not None:
                    if row["perícia"] in perícias_alt_selecionadas:
                        #print("Perícia alternativa", row["perícia"], "inválida!")
                        pass
                elif "Opcional" in row["perícias_da_classe"] and row["perícia"] in perícias_op_selecionadas:
                    #print("Detectou Opcional Escolhida!\n===========")
                    perícias_treinadas.append("Treinado (op)")
                    bônus_treino.append(bônus_de_treino)
                    continue
                elif row["perícia"] in perícias_op_selecionadas:
                    #print("Perícia opcional", row["perícia"], "inválida!")
                    continue
            if row["perícia"] in perícias_livres_selecionadas:
                #print("Detectou Livre Escolhida!\n===========")
                perícias_treinadas.append("Treinado (livre)")
                bônus_treino.append(bônus_de_treino)
                continue
            else:
                #print("Detectou Livre não Escolhida\n===========")
                perícias_treinadas.append("Não Treinada")
                bônus_treino.append(0)
            #print("===========")
        
        tabela_perícias_jogador["treino"] = perícias_treinadas
        tabela_perícias_jogador["bônus_nível"] = bônus_nível
        tabela_perícias_jogador["bônus_atributo"] = bônus_atributo
        tabela_perícias_jogador["bônus_treino"] = bônus_treino
        tabela_perícias_jogador["bônus_outro"] = [0] * len(tabela_perícias_jogador.index)

        tabela_perícias_jogador["bônus_total"] = [nível + atr + treino for nível, atr, treino in zip(bônus_nível, bônus_atributo, bônus_treino)]

        self.tabela_perícias = tabela_perícias_jogador

    def inicializa_tabela_de_origem(self):
        return(pd.DataFrame(columns = ["nome", "origem", "prioridade", "automático", "referência", "bônus_em", "valor_bônus",
                                        "efeito_bônus", "condição", "restrição_classe", "restrição_raça", "restrição_nível",
                                        "restrição_poderes", "restrição_divindade", "restrição_perícia", "restrição_magia",
                                        "restrição_atributo", "já_processado"]))

    def inicializa_atributos(self):
        return({"for": 0, "des": 0, "con": 0, "int": 0, "sab": 0, "car": 0})

    def inicializa_atributos_combate(self):
        return({"pv": 0, "pm": 0, "defesa": 0, "resistência_mágica": 0, "ataque": 0,
                "dano": 0, "penalidade_armadura": 0, "deslocamento": 0, "categoria_tamanho": 0,
                "margem_ameaça": 0, "multiplicador": 0})

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
        #print("tabela_origem: ", self.tabela_origem.columns)
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
            #self.atributos.update({atributo: valor})
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
        tabela_raças = self.get_tabela("raças")
        atributos_raça = tabela_raças[tabela_raças["raça"] == self.raça]
        #print(atributos_raça)

        quantidade_pontos_livres = atributos_raça["pontos_livres"].tolist().pop()
        permite_mais_2 = atributos_raça["permite_mais_2"].tolist().pop()
        restrição_pontos_livres = atributos_raça["restrição_pontos_livres"].tolist().pop()
        referência = atributos_raça["referência"].tolist().pop()

        #print("atributos_raça['for']: ", atributos_raça["for"])
        #print("atributos_raça['for'].tolist().pop(): ", atributos_raça["for"].tolist().pop())

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
            #self.atributos[atributo] += atributos_raça[atributo] + pontos_livres[atributo]
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

    # TODO: Essa função será redundante quando a "adiciona_lista_para_tabela_origem" for completa
    def aumentos_de_atributos_disponíveis(self):
        tabela_aumento_atributo = self.get_tabela("poderes_atributos")
        tabela_aumento_atributo = tabela_aumento_atributo.sort_values(by = "prioridade", ascending = False)

        tabela_aumentos_válidos = self.inicializa_tabela_de_origem()

        for _, row in tabela_aumento_atributo.iterrows():
            # Se há restrição de nível
            if row["restrição_nível"] is not None:
                if not any(x >= row["restrição_nível"] for x in self.classes.values()):
                    print("Poder ", row["nome"], " não válido pois a restrição de nível ", row["restrição_nível"], " não cumprida")
                    continue
            
            # Apenas testamos restrições de níveis porque esses poderes apenas dependem de sí mesmos
            tabela_aumentos_válidos.loc[self.tabela_origem.last_valid_index() + 1] = row

        return(tabela_aumentos_válidos)
    
    # TODO: Essa função será semi-redundante quando a "adiciona_lista_para_tabela_origem" for completa
    def poderes_disponíveis(self):
        """
        Pegar a giga-gigante tabela de todos os poderes e fazer um subset daqueles que estão
        disponíveis para o personagem atual
        """
        tabela_poderes = self.get_tabela("poderes")
        tabela_poderes = tabela_poderes.replace({float("nan"): None})
        # Ordena a tabela pela prioridade necessário para ver a restrição dos poderes
        tabela_poderes = tabela_poderes.sort_values (by = "prioridade", axis = 0, ascending = False)

        tabela_poderes_válidos = self.inicializa_tabela_de_origem()

        # Iterar pelas linhas para testar as restrições
        for _, row in tabela_poderes.iterrows():

            classe_do_poder = None

            # Primeiro ver se há alguma restrição de classe
            if row["restrição_classe"] is not None:
                # Se têm testar se a classe a qual o poder é restrito não está nas
                # classes do personagem, se ele não estiver, podemos parar de
                # processar esse poder aqui
                if not any(x in row["restrição_classe"] for x in self.classes.keys()):                
                    print("Poder ", row["nome"], " não válido pois a restrição de classe ", row["restrição_classe"], " não foi cumprida")
                    continue
                # Se teve um match da classe a qual o poder é restrito e as classes
                # do personagem, queremos saber que classe é, pois quando há uma
                # restrição de nível em conjunto com uma de classe, a restrição
                # é interpretada como "seja um inventor de nível 9" ao invés de
                # "seja um inventor e tenha alguma classe nível 9"
                else:
                    for classe in self.classes.keys():
                        if classe == row["restrição_classe"]:
                            classe_do_poder = classe

            # Se há restrição de nível
            if row["restrição_nível"] is not None:
                # Testar a classe que a qual o poder pertence, se ela existir
                if classe_do_poder is not None:
                    if self.get_nível_de_classe(classe_do_poder) < row["restrição_nível"]:
                        print("Poder ", row["nome"], " não válido pois a restrição de nível ", row["restrição_nível"], " da classe do poder não cumprida")
                        continue
                # Se não tiver classe a qual o poder pertence, testar todos os níveis de classe
                else:
                    if not any(x >= row["restrição_nível"] for x in self.classes.values()):
                        print("Poder ", row["nome"], " não válido pois a restrição de nível ", row["restrição_nível"], " não cumprida")
                        continue

            if row["restrição_divindade"] is not None:
                if self.divindade not in row["restrição_divindade"]:
                    print("Poder ", row["nome"], " não válido pois a restrição de divindade ", row["restrição_divindade"], " não cumprida")
                    continue

            #print("tabela_poderes_válidos: ", tabela_poderes_válidos)
            #print("row: ", row)

            aux_row = pd.DataFrame.from_dict([row.to_dict()])
            #print("aux_row: ", aux_row)

            tabela_poderes_válidos = pd.concat([tabela_poderes_válidos, aux_row], ignore_index = True)
            #tabela_poderes_válidos.loc[tabela_poderes_válidos.last_valid_index() + 1] = row

        return(tabela_poderes_válidos)

    def get_perícias_treinadas(self):
        if self.tabela_perícias is None:
            raise Exception("Tentativa de acesso à tabela de perícias resultou em None")
        lista_perícias_treinadas = self.tabela_perícias[["perícia", "treino"]]
        lista_perícias_treinadas = lista_perícias_treinadas[lista_perícias_treinadas["treino"] != "Não Treinada"]
        #print("lista_perícias_treinadas: ", lista_perícias_treinadas["perícia"].values)
        return(lista_perícias_treinadas["perícia"].values)

    def adiciona_lista_para_tabela_origem(self, tabela_generalizada: pd.DataFrame, lista_selecionados: list):
        """
        Checa restrições e adiciona os poder válidos duma lista de poderes para a tabela de origem
        lista_selecionados: uma lista dos poderes da tabela dada a serem checados e adicionados
        tabela_generalizada: uma tabela formatada como uma tabela generalizada
        """

        tabela_generalizada = tabela_generalizada.sort_values(by = "prioridade", ascending = False)
        tabela_generalizada = tabela_generalizada.replace({float("nan"): None})

        poderes_do_personagem = self.get_poderes_do_personagem()

        if len(lista_selecionados) > self.num_poderes_disponíveis:
            raise Exception("Número de poderes escolhidos para o personagem maior do que o possível")

        for _, row in tabela_generalizada.iterrows():

            if row["nome"] in lista_selecionados:
                #print("lista_selecionados: ", lista_selecionados)
                #print("row[nome]: ", row["nome"])
                classe_do_poder = None
                # Primeiro ver se há alguma restrição de classe
                if row["restrição_classe"] is not None:
                    # Se têm testar se a classe a qual o poder é restrito não está nas
                    # classes do personagem, se ele não estiver, podemos parar de
                    # processar esse poder aqui
                    if not any(x in row["restrição_classe"] for x in self.classes.keys()):                
                        print("Poder ", row["nome"], " não válido pois a restrição de classe ", row["restrição_classe"], " não foi cumprida")
                        continue
                    # Se teve um match da classe a qual o poder é restrito e as classes
                    # do personagem, queremos saber que classe é, pois quando há uma
                    # restrição de nível em conjunto com uma de classe, a restrição
                    # é interpretada como "seja um inventor de nível 9" ao invés de
                    # "seja um inventor e tenha alguma classe nível 9"
                    else:
                        for classe in self.classes.keys():
                            if classe == row["restrição_classe"]:
                                classe_do_poder = classe

                # Se há restrição de nível
                if row["restrição_nível"] is not None:
                    # Testar a classe que a qual o poder pertence, se ela existir
                    if classe_do_poder is not None:
                        if self.get_nível_de_classe(classe_do_poder) < row["restrição_nível"]:
                            print("Poder ", row["nome"], " não válido pois a restrição de nível ", row["restrição_nível"], " da classe do poder não cumprida")
                            continue
                    # Se não tiver classe a qual o poder pertence, testar todos os níveis de classe
                    else:
                        if self.get_nível_total() < row["restrição_nível"]:
                            print("Poder ", row["nome"], " não válido pois a restrição de nível ", row["restrição_nível"], " não cumprida")
                            continue

                if row["restrição_divindade"] is not None:
                    # O primeiro poder concedido é uma freebie, tem q ver isso aqui
                    if self.divindade in row["restrição_divindade"]:
                        if "Poder Concedido" not in self.tabela_origem["origem"].unique():
                            row["automático"] = "Sim"
                        # Testar tmb se o poder já antes ganhou sim, dai botar sim dnv
                        if row["nome"] in self.tabela_origem["nome"].unique() and row["nome"]:
                            row_aux = self.tabela_origem[self.tabela_origem["nome"] == row["nome"]]
                            # print("row_aux[automático]", row_aux["automático"].values)
                            # print("'sim' in row_aux[automático]", "Sim" in row_aux["automático"].values)
                            if "Sim" in row_aux["automático"].values:
                                row["automático"] = "Sim"
                    else:
                        print("Poder ", row["nome"], " não válido pois a restrição de divindade ", row["restrição_divindade"], " não cumprida")
                        continue
                
                if row["restrição_raça"] is not None:
                    if self.raça not in row["restrição_raça"]:
                        print("Poder ", row["nome"], " não válido pois a restrição de raça ", row["restrição_raça"], " não cumprida")
                        continue

                if row["restrição_perícia"] is not None:
                    if row["restrição_perícia"] not in self.get_perícias_treinadas():
                        print("Poder ", row["nome"], " não válido pois a restrição de perícia ", row["restrição_perícia"], " não cumprida")
                        continue

                if row["restrição_atributo"] is not None:
                    lista_stats = row["restrição_atributo"].split("|")

                    skip = False

                    for string_atr in lista_stats:
                        atributo, valor = string_atr.split(":")
                        if self.get_atributo(atributo) < int(valor):
                            print("Poder ", row["nome"], " não válido pois a restrição de atributo ", row["restrição_atributo"], " não cumprida")
                            skip = True

                    if skip:
                        continue

                if row["restrição_poderes"] is not None:
                    if row["restrição_poderes"] not in poderes_do_personagem:
                        print("poderes_do_personagem", poderes_do_personagem)
                        print("Poder ", row["nome"], " não válido pois a restrição de poderes ", row["restrição_poderes"], " não cumprida")
                        continue

                # TODO: falta restrição de magia

                if row["nome"] not in poderes_do_personagem:
                    poderes_do_personagem.append(row["nome"])
                    #print(poderes_do_personagem)
                aux_row = pd.DataFrame.from_dict([row.to_dict()])
                #tabela_generalizada = pd.concat([tabela_generalizada, aux_row], ignore_index = True)
                self.tabela_origem = pd.concat([self.tabela_origem, aux_row], ignore_index = True)

    def adiciona_ao_sabor_do_destino(self, lista_escolhas: list()):
        """
        Adiciona especificamente o poder "Ao Sabor do Destino"
        """

        if self.get_nível_total() < 6:
            raise Exception("Nível muito baixo para adicionar Ao Sabor do Destino!")

        if len(lista_escolhas) != len(set(lista_escolhas)):
            raise Exception("Lista do poder Ao Sabor do Destino tem valores duplicados, o que não deveria ser possível!")

        i = 6
        cont_pra_lista = 0

        while i <= self.get_nível_total():
            # Se o mod de 5 é 1 é 6, 11, 16 e são níveis q dão perícia
            if i % 5 == 1:
                if lista_escolhas[cont_pra_lista] not in self.get_lista_perícias():
                    raise Exception("O valor encontrado no índice", cont_pra_lista, "da lista de bônus para o poder Ao Sabor do Destino não é uma perícia quando deveria ser!")

                self.adiciona_linha_tabela_de_origem(nome = "Ao Sabor do Destino",
                                                     origem = "Poderes de Destino",
                                                     prioridade = 1,
                                                     automático = "Não",
                                                     referência = "Tormenta 20: Jogo do Ano, página 130",
                                                     bônus_em = lista_escolhas[cont_pra_lista],
                                                     valor_bônus = 2,
                                                     restrição_nível = i,
                                                     condição = "Não usar itens mágicos")
                cont_pra_lista += 1
            # Se o mod de 5 é 2 é 7, 12, 17 e são níveis q dão armadura
            if i % 5 == 2:
                self.adiciona_linha_tabela_de_origem(nome = "Ao Sabor do Destino",
                                                     origem = "Poderes de Destino",
                                                     prioridade = 1,
                                                     automático = "Não",
                                                     referência = "Tormenta 20: Jogo do Ano, página 130",
                                                     bônus_em = "defesa",
                                                     valor_bônus = 1,
                                                     restrição_nível = i,
                                                     condição = "Não usar itens mágicos")
            # Se o mod de 5 é 3 é 8, 13, 18 e são níveis q dão dano
            if i % 5 == 3:
                self.adiciona_linha_tabela_de_origem(nome = "Ao Sabor do Destino",
                                                     origem = "Poderes de Destino",
                                                     prioridade = 1,
                                                     automático = "Não",
                                                     referência = "Tormenta 20: Jogo do Ano, página 130",
                                                     bônus_em = "dano",
                                                     valor_bônus = 1,
                                                     restrição_nível = i,
                                                     condição = "Não usar itens mágicos")
            # Se o mod de 5 é 4 é 9, 14, 19 e são níveis q dão atributos
            if i % 5 == 4:
                if lista_escolhas[cont_pra_lista] not in self.get_lista_atributos():
                    raise Exception("O valor encontrado no índice", cont_pra_lista, "da lista de bônus para o poder Ao Sabor do Destino não é um atributo quando deveria ser!")
                self.adiciona_linha_tabela_de_origem(nome = "Ao Sabor do Destino",
                                                     origem = "Poderes de Destino",
                                                     prioridade = 1,
                                                     automático = "Não",
                                                     referência = "Tormenta 20: Jogo do Ano, página 130",
                                                     bônus_em = lista_escolhas[cont_pra_lista],
                                                     valor_bônus = 1,
                                                     restrição_nível = i,
                                                     condição = "Não usar itens mágicos")
                cont_pra_lista += 1

            i += 1

    def interpreta_tabela_de_origem(self):

        self.num_poderes_disponíveis = self.get_num_poderes()

        tabela_origem = self.tabela_origem

        for classe, nível in self.classes.items():
            num_poderes_classe = len(tabela_origem.loc[(tabela_origem["restrição_classe"] == classe) & (tabela_origem["automático"] != "Sim"), "nome"].unique())
            if num_poderes_classe > nível - 1:
                raise Exception("Número de poderes selecionados da classe ", classe, " maior do que o permitido", num_poderes_classe, ">", nível - 1)

        #print("len stuff:", len(tabela_origem.loc[tabela_origem["automático"] != "Sim", "nome"].unique()))
        #print(tabela_origem.loc[tabela_origem["automático"] != "Sim", "nome"])

        if len(tabela_origem.loc[tabela_origem["automático"] != "Sim", "nome"].unique()) > self.num_poderes_disponíveis:
            raise Exception("Número de poderes selecionados maior do que a classe e nível permitem")

        tabela_origem = tabela_origem.replace({float("nan"): None})

        for indx, row in tabela_origem.iterrows():
            if row["já_processado"] is True:
                continue
            if row["já_processado"] is not True:
                self.tabela_origem.at[indx, "já_processado"] = True

            if row["valor_bônus"] is not None:
                string_bônus = str(row["valor_bônus"])
                # print("row[valor_bônus]: ", row["valor_bônus"])
                # Esse match é pra ver se a string é apenas números
                # assim, podemos jogar ela direto pra atribuição
                if re.match(r"\-?([0-9])+", string_bônus):
                    #print(row["bônus_em"], int(row["valor_bônus"]))
                    self.adiciona_atributo(row["bônus_em"], int(row["valor_bônus"]))
                else:
                    exprs_completas = re.findall(r"\"(.[^\"]+)\"", string_bônus)
                    # print("exprs_completas: ", exprs_completas)
                    # print("len(exprs_completas): ", len(exprs_completas))
                    vetor_expressões = []
                    expressão_sub = []
                    for expressão in exprs_completas:
                        expressão_sem_aspas = re.search(r"([^\"\n]+)", expressão)
                        variável, valor = expressão_sem_aspas.group(0).split(":")
                        if variável == "atr":
                            valor_bônus = self.get_atributo(valor)
                            #print("valor_bônus: ", valor_bônus)
                        if variável == "nível":
                            valor_bônus = self.get_nível_de_classe(valor)
                            #print("valor_bônus: ", valor_bônus)
                        vetor_expressões.append(expressão)
                        expressão_sub.append(valor_bônus)

                    for expressão, sub in zip(vetor_expressões, expressão_sub):
                        string_bônus = string_bônus.replace("".join(["\"", expressão, "\""]), str(sub))
                        # print("string_bônus: ", string_bônus)
                        # print("".join(["\"", expressão, "\""]))
                        # print("expressão: ", expressão)
                        # print("sub: ", sub)
                    
                    # print("eval: ", eval(string_bônus))
                    # print("vetor_expressões: ", vetor_expressões)
                    # print("expressão_sub: ", expressão_sub)

                    self.adiciona_atributo(row["bônus_em"], int(eval(string_bônus)))