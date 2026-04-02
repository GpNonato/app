import asyncio
import traceback

from modules import Gestao
from time import sleep
from datetime import datetime, timedelta
from pyautogui import press, write, hotkey
from dtos import RpaGestaoAutomacao
from core import RuntimeEnvironmentConfig
from config import PROMAX_CREDENTIALS
from modules import Promax
from modules.Promax.methods import export_csv_file
from utils import makeThis, checkImage, clickOnTarget
from tools import paramsBuilder, MediaLoader
from unidecode import unidecode


class RpaProcess(Promax):
    def __init__(self, rpa_data: RpaGestaoAutomacao, runtime_mode: RuntimeEnvironmentConfig):
        self.rpa_data = rpa_data
        self.rpa_data.rpaGestaoAutomacaoParametros = rpa_data.rpaGestaoAutomacaoParametros

        super().__init__(self.rpa_data.id, runtime_mode)

    @staticmethod
    async def filters():
        sleep(3)

        hotkey("alt", "v")

        sleep(2)

    async def run(self):
        try:

            rpaGestaoAutomacaoParametros = paramsBuilder(self.rpa_data.rpaGestaoAutomacaoParametros)

            await self.log.create("Iniciando execução do RPA.")

            companies = self.rpa_data.rpaGestaoAutomacaoEmpresas

            for company in companies:
                await self.open_promax(company.promaxUrl)
                await self.login(PROMAX_CREDENTIALS["user"], PROMAX_CREDENTIALS["password"])
                await self.log.create(f"Selecionando Revenda: {company.nome} - {company.promaxUnb}")
                await self.company_select(company.promaxUnb)
                await self.close_pop_ups()
                await self.initiate_routine(rpaGestaoAutomacaoParametros["Rotina"])
                await self.filters()

                file_folder = f"{rpaGestaoAutomacaoParametros['Diretorio']}"
                file_name = f"{company.nome.replace(" ", "_").lower()}.csv"


                await self.closeBrowser()

            await self.log.create("Finalizou execução do RPA com sucesso.")

        except Exception as error:
            traceback.print_exc()
            await self.log.create(f"Finalizou execução do RPA com falha. \n Erro: {error}")