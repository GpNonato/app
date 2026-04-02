import traceback
from time import sleep
from pyautogui import press, write, hotkey
from datetime import datetime, timedelta

from dtos import RpaGestaoAutomacao
from core import RuntimeEnvironmentConfig

from config import PROMAX_CREDENTIALS
from modules import Promax
from modules.RenovaSenhas import fetchUsuariosPromax
from tools import paramsBuilder


class RpaProcess(Promax):
    def __init__(self, rpa_data: RpaGestaoAutomacao, runtime_mode: RuntimeEnvironmentConfig):
        self.rpa_data = rpa_data
        self.rpa_data.rpaGestaoAutomacaoParametros = rpa_data.rpaGestaoAutomacaoParametros

        super().__init__(self.rpa_data.id, runtime_mode)

    @staticmethod
    async def filters():
        data_renovada = (datetime.today() + timedelta(days=30)).strftime("%d/%m/%Y")
        for username in fetchUsuariosPromax():
            sleep(2.5)
            write(username)
            sleep(1.5)
            press("tab")
            sleep(1)
            press("enter")
            sleep(1)
            press("tab")
            sleep(1)
            write(data_renovada)
            sleep(1)
            hotkey("alt", "s")

    async def run(self):
        try:
            rpaGestaoAutomacaoParametros = paramsBuilder(self.rpa_data.rpaGestaoAutomacaoParametros)

            await self.log.create("Iniciando execução do RPA.")

            companies = self.rpa_data.rpaGestaoAutomacaoEmpresas

            for company in companies:
                await self.open_promax(company.promaxUrl)
                await self.login(PROMAX_CREDENTIALS["user"], PROMAX_CREDENTIALS["password"])
                await self.company_select(company.promaxUnb)
                await self.close_pop_ups()
                await self.initiate_routine(rpaGestaoAutomacaoParametros["Rotina"])
                await self.log.create("Selecionando filtros do relatório.")
                await self.filters()
                await self.closeBrowser()

            await self.log.create("Finalizou execução do RPA com sucesso.")
        except Exception as error:
            traceback.print_exc()
            await self.log.create(f"Finalizou execução do RPA com falha. \n Erro: {error}")
