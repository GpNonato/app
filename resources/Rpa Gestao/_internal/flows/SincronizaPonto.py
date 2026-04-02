import traceback
import pyautogui
import time
import cv2
import easyocr
import numpy as np
import warnings
import os
import asyncio


from datetime import datetime, timedelta
from multiprocessing.process import BaseProcess
from dtos import RpaGestaoAutomacao
from core import RuntimeEnvironmentConfig
from tools import paramsBuilder
from modules import BaseRPA
from utils import makeThis
from pyautogui import press, write, hotkey, click
from utils import makeThis
from pyautogui import press, write, hotkey, click
from utils import makeThis, isImageOnScreen
from PIL import Image, ImageEnhance
from modules.SincronizaPonto import *

class RpaProcess(BaseRPA):
    def __init__(self, rpa_data: RpaGestaoAutomacao, runtime_mode: RuntimeEnvironmentConfig):
        self.rpa_data = rpa_data
        self.rpa_data.rpaGestaoAutomacaoParametros = rpa_data.rpaGestaoAutomacaoParametros
        self.terminais_error = []
        self.terminais_sucess = []
        super().__init__(self.rpa_data.id, runtime_mode)

    async def main(self, terminal: tuple[str, str]):
        try:
            nome, arquivo = terminal
            caminho_imagem = caminhoRelativoImagem(os.path.join("Imagens", arquivo))

            await self.log.create(f"\n> Atualizando o terminal: {nome}...\n ")
            await processoSincroniza(caminho_imagem)
            time.sleep(3)

            textos = "NÃO HÁ NOVOS REGISTROS NO TERMINAL"
            comparaTexto(nome, textos, self.terminais_sucess, self.terminais_error)

        except Exception as error:
            await self.log.create(f"Erro: {error}")
            await self.log.create(f"Finalizou execução do RPA com falha. \n Erro: {error}")
            input("\nPressione Enter para sair...")



    async def run(self):
        log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "crash_log.txt")

        try:
            rpaGestaoAutomacaoParametros = paramsBuilder(self.rpa_data.rpaGestaoAutomacaoParametros)

            await self.log.create("Iniciando execução do RPA.\n")

            companies = {
                "A3P": "A3P.png",
                "CACHOEIRA": "cachoeiro.png",
                "CONGONHAS": "congonhas.png",
                "CORPORATIVO": "corporativo.png",
                "HOME CENTER": "homeCenter.png",
                "HOME CENTER - PISOS": "homeCenterPisos.png",
                "MAISCOR": "maiscor.png",
                "MARIANA REVENDA": "marianaRevenda.png",
                "MARIANA VAREJO": "marianaVarejo.png",
                "MATRIZ": "matriz.png",
                "OURO PRETO": "ouroPreto.png"
            }

            time.sleep(3)


            makeThis(
                task_list=[
                    lambda: hotkey("win", "r"),
                    lambda: press("backspace"),
                    lambda: write(r"C:\Assepontoweb\Printpoint 3\PrintPointIII.exe", interval=0.02),
                    lambda: press("enter", interval=3),
                    lambda: hotkey("alt", "space", interval=0.3),
                    lambda: hotkey("x"),
                ],
                cooldown_time=0.5
            )

            for nome_terminal in companies:
                terminal = companies[nome_terminal]
                await self.main((nome_terminal, terminal))

            makeThis(
                task_list=[
                    lambda: click(7, 692, 1, 1),
                    lambda: hotkey("alt", "f4")
                ]
            )

            await self.log.create(f"\nTerminais que deram erro: {self.terminais_error}\n")
            await self.log.create(f"\nTodos os terminais que foram atualizados com sucesso!: {self.terminais_sucess} \n")
            await self.log.create("Finalizou execução do RPA com sucesso.")

        except Exception as error:
            with open(log_file_path, "w", encoding="utf-8") as f:
                f.write("Finalizou execução do RPA com falha. \n")
                f.write(f"Erro: {error}\n")
                f.write("\n" + traceback.format_exc())

            await self.log.create(f"Finalizou execução do RPA com falha. \n Erro: {error}")

        finally:
            input("\nPressione Enter para sair...")
