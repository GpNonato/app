import pyautogui
import traceback
from time import sleep
from datetime import datetime, timedelta
from pyautogui import press, write, hotkey

from dtos import RpaGestaoAutomacao
from core import RuntimeEnvironmentConfig

from tools import paramsBuilder, MediaLoader
from modules import Promax
from config import PROMAX_CREDENTIALS
from utils import makeThis, clickOnTarget


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
                lambda: write("Operacao"),
                lambda: press("tab"),
                lambda: press("tab"),
                lambda: press("tab"),
                lambda: press("tab"),
                lambda: press("tab"),
                lambda: press("tab"),
                lambda: press("tab"),
                lambda: press('space'),
            ],
            cooldown_time=1
        )

        campo_operacao = MediaLoader.Image("7ca218b0ef1b1382433cba6d147d5af5").path()
        sleep(2)
        await clickOnTarget(campo_operacao)
        sleep(1.5)
        hotkey("ctrl", "a")
        sleep(1)

        makeThis(
            task_list=[
                lambda: write("1"),
                lambda: press("tab"),
                lambda: write("2"),
            ],
            cooldown_time=1
        )

        checkbox = MediaLoader.Image("c32eb85cb251befc2bf76d3c41377870").path()
        sleep(1)
        await clickOnTarget(checkbox)
        sleep(1.5)

        hotkey("alt", "v")

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
                        f'{rpaGestaoAutomacaoParametros["Rotina"]}_{company.nome.split()[1].lower()}'
                    )

                except Exception as error:
                    print(error)

                finally:
                    await self.closeBrowser()

            await self.log.create("Finalizou execução do RPA com sucesso.")

        except Exception as error:
            traceback.print_exc()
            await self.log.create(f"Finalizou execução do RPA com falha. \n Erro: {error}")
