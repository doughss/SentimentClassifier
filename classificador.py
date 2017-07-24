# -*- coding: utf-8 -*-

from math import log
from nltk.classify import NaiveBayesClassifier, accuracy
from random import shuffle
from utils import tokenizar


class Palavra(object):

    def __init__(self, palavra):
        self.palavra = palavra
        self.ocorrencia = 1
        self.idf = None

    def __repr__(self):
        return "Palavra '{0}'".format(self.palavra)

    def add_ocorrencia(self):
        """Método que incrementa em 1 quando a palavra ocorre em um documento.
            :return :None:
        """
        self.ocorrencia += 1

    def calcular_idf(self, total_documentos):
        """Método que calcula o idf de uma palavra.
            :param total_documentos: :int: referente ao total de documentos.

            :return :None:
        """
        self.idf = log(float(total_documentos) / float(self.ocorrencia))


class ClassificadorSentimento(object):

    # ###############
    # # CONSTRUTOR ##
    # ###############

    def __init__(self, reviews_positivos, reviews_negativos):
        """
        :param reviews_positivos: :list: dos arquivos positivos que treinarão o classificador.
        :param reviews_negativos: :list: dos arquivos negativos que treinarão o classificador.
        """

        self.conjunto_treinamento = {"positivo": [], "negativo": []}

        self.bag_of_words = self._criar_bow(dict_arquivos={"positivo": reviews_positivos,
                                                           "negativo": reviews_negativos})

        self._treinar_classificador()

    # #####################
    # # MÉTODOS PRIVADOS ##
    # #####################

    def _criar_bow(self, dict_arquivos):
        """Metodo que cria a bag of words de um conjunto de arquivos.
            :param dict_arquivos: :dict: key: classe dos arquivo value: :list: dos arquivos

            :return :list: de :Palavra:
        """
        dict_palavras = {}
        count = 0
        for classe, arquivos in dict_arquivos.items():
            for caminho_arquivo in arquivos:
                count += 1
                arquivo = open(caminho_arquivo, mode="r")
                texto_arquivo = " ".join(arquivo.readlines()).decode("utf-8")

                tokens = tokenizar(texto_arquivo)

                for palavra in tokens.keys():
                    try:
                        dict_palavras[palavra].add_ocorrencia()
                    except KeyError:
                        dict_palavras[palavra] = Palavra(palavra=palavra)

                self.conjunto_treinamento[classe].append(tokens)

        for palavra in dict_palavras.values():
            palavra.calcular_idf(count)

        return dict_palavras.values()

    def _treinar_classificador(self):
        """ Método que treina o classificador

            :return: :None:
        """
        lista_treinamento = []

        for classe, lista_textos in self.conjunto_treinamento.items():
            for textos_tokenizados in lista_textos:
                lista_treinamento.append((self.extrair_caracteristicas(textos_tokenizados),
                                          classe))
        shuffle(lista_treinamento)

        self.classificador = NaiveBayesClassifier.train(lista_treinamento)

    # #####################
    # # MÉTODOS PÚBLICOS ##
    # #####################

    def extrair_caracteristicas(self, tokens):
        """Metodo que extrai as caracteristicas de uma lista tokens de um review.
            :param tokens: :dict: key:token value:tf*idf

            :return :dict: com as caracteristicas extraidas
        """
        numero_tokens = sum(tokens.values())

        def calcular_tf(palavra_obj):
            frequencia_token = tokens.get(palavra_obj.palavra, 0)
            return float(frequencia_token)/numero_tokens

        return {palavra.palavra: calcular_tf(palavra) * palavra.idf
                for palavra in self.bag_of_words}

    def classificar_reviews(self, arquivos):
        """ Método que classifica uma lista de arquivos.
            :param arquivos: :list: dos caminhos dos arquivos a serem classificados.

            :return: :list: contendo a classificação dos respectivos arquivos.
        """
        lista_de_caracteristicas = []
        for caminho_arquivo in arquivos:
            arquivo = open(caminho_arquivo, mode="r")
            texto_arquivo = " ".join(arquivo.readlines()).decode("utf-8")
            tokens = tokenizar(texto_arquivo)

            lista_de_caracteristicas.append((self.extrair_caracteristicas(tokens)))

        return self.classificador.classify_many(lista_de_caracteristicas)

    def medir_taxa_acerto(self, conjunto_de_teste):
        """Método para medir a taxa de acerto do classificador.
            :param conjunto_de_teste: :list: contendo :tuple:(:dict: de caracteristicas, classe)

            :return: :float:
        """
        return accuracy(self.classificador, conjunto_de_teste)