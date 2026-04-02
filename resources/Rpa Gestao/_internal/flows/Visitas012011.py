from time import sleep
from datetime import datetime, timedelta
from config import PROMAX_CREDENTIALS
import pyautogui
from pyautogui import press, write, hotkey

from dtos import RpaGestaoAutomacao
from core import RuntimeEnvironmentConfig

from tools import paramsBuilder
from modules import Promax
from utils import makeThis, checkImage
import traceback


class RpaProcess(Promax):
    def __init__(self, rpa_data: RpaGestaoAutomacao, runtime_mode: RuntimeEnvironmentConfig):
        self.rpa_data = rpa_data
        self.rpa_data.rpaGestaoAutomacaoParametros = rpa_data.rpaGestaoAutomacaoParametros

        super().__init__(self.rpa_data.id, runtime_mode)

    @staticmethod
    async def filters():
        sleep(2)
        makeThis(
            task_list=[
                lambda: press("tab"),
                lambda: write("05"),
                lambda: press('tab'),
                lambda: press('space'),
                lambda: press(['tab']*6),
                lambda: press('enter')
            ],
            cooldown_time=1
        )

    async def run(self):
        try:
            rpaGestaoAutomacaoParametros = paramsBuilder(self.rpa_data.rpaGestaoAutomacaoParametros)

            await self.log.create("Iniciando execução do RPA.")

            companies = self.rpa_data.rpaGestaoAutomacaoEmpresas

            for company in companies:
                try:
                    await self.open_promax(company.promaxUrl)
                    await self.login(PROMAX_CREDENTIALS["user"], PROMAX_CREDENTIALS["password"])
                    await self.company_select(company.promaxUnb)
                    await self.close_pop_ups()
                    await self.initiate_routine(rpaGestaoAutomacaoParametros["Rotina"])
                    sleep(3)
                    await self.filters()
                    await self.save_file(
                        rpaGestaoAutomacaoParametros["Diretorio"],
                        f"{rpaGestaoAutomacaoParametros["Rotina"]}_{company.nome.split()[1].lower()}"
                    )
                except Exception as error:
                    print(error)

                finally:
                    await self.closeBrowser()

            await self.log.create("Finalizou execução do RPA com sucesso.")

        except Exception as error:
            traceback.print_exc()
            await self.log.create(f"Finalizou execução do RPA com falha. \n Erro: {error}")