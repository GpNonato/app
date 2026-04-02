import asyncio
import traceback

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
from dateutil.relativedelta import relativedelta


class RpaProcess(Promax):
    def __init__(self, rpa_data: RpaGestaoAutomacao, runtime_mode: RuntimeEnvironmentConfig):
        self.rpa_data = rpa_data
        self.rpa_data.rpaGestaoAutomacaoParametros = rpa_data.rpaGestaoAutomacaoParametros

        super().__init__(self.rpa_data.id, runtime_mode)



    @staticmethod
    async def filters(quantidade_tab:int):

        mes_passado = (datetime.now().replace(day=1)- relativedelta(months=1)).strftime('%d/%m/%Y')

        sleep(3)

        makeThis(
            task_list=[
                lambda: write("Operacao"),
                lambda: press("tab", presses=5, interval=0.3),
                lambda: press("up"),
                lambda: press("tab"),
                lambda: press("up"),
                lambda: press("tab", presses=3, interval=0.3),
                lambda: press("space"),
                lambda: press("tab", presses=2, interval=0.3),
                lambda: press("space"),
                lambda: press("tab", quantidade_tab, interval=0.3),
                lambda: write("251", interval=0.3),
                lambda: press("tab"),
                lambda: write("314", interval=0.3),
                lambda: press("tab"),
                lambda: write(mes_passado, interval=0.3),
                lambda: hotkey("alt", "v")
            ],
            cooldown_time=1
        )

        sleep(2)



    async def run(self):
        try:
            rpaGestaoAutomacaoParametros = paramsBuilder(self.rpa_data.rpaGestaoAutomacaoParametros)

            await self.log.create("Iniciando execução do RPA.")
            await self.scan_folder()


            companies = self.rpa_data.rpaGestaoAutomacaoEmpresas

            for company in companies:
                if (company.nome == "REVENDA A3P"):

                    quantidade_tab = 4

                else:

                    quantidade_tab = 3

                await self.generate_standard_report(rpaGestaoAutomacaoParametros, company, lambda: self.filters(quantidade_tab))
            await self.log.create("Finalizou execução do RPA com sucesso.")

        except Exception as error:
            traceback.print_exc()
            await self.log.create(f"Finalizou execução do RPA com falha. \n Erro: {error}")