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
    async def filters():

        tres_meses_atras = (datetime.now().replace(day=1)- relativedelta(months=3)).strftime('%d/%m/%Y')

        sleep(3)

        makeThis(
            task_list=[
                lambda: write("Tipo Movto"),
                lambda: press("tab"),
                lambda: write("Cliente"),
                lambda: press("tab", presses=4, interval=0.3),
                lambda: press("up"),
                lambda: press("tab", presses=4, interval=0.3),
                lambda: press("space"),
                lambda: press("tab", presses=3, interval=0.3),
                lambda: write("51", interval=0.3),
                lambda: press("tab"),
                lambda: write("52", interval=0.3),
                lambda: press("tab", 3, interval=0.3),
                lambda: write(tres_meses_atras, interval=0.3),
                lambda: hotkey("alt", "v")
            ],
            cooldown_time=1
        )


    async def run(self):
        try:

            rpaGestaoAutomacaoParametros = paramsBuilder(self.rpa_data.rpaGestaoAutomacaoParametros)

            await self.log.create("Iniciando execução do RPA.")

            companies = self.rpa_data.rpaGestaoAutomacaoEmpresas

            for company in companies:
                await self.generate_standard_report(rpaGestaoAutomacaoParametros, company, lambda: self.filters())

            await self.log.create("Finalizou execução do RPA com sucesso.")

        except Exception as error:
            traceback.print_exc()
            await self.log.create(f"Finalizou execução do RPA com falha. \n Erro: {error}")