from time import sleep
from datetime import datetime, timedelta

from pyautogui import press, write, hotkey

from dtos import RpaGestaoAutomacao
from core import RuntimeEnvironmentConfig

from tools import paramsBuilder, MediaLoader

from modules import Promax
from utils import makeThis, checkImage, clickOnTarget
import traceback


class RpaProcess(Promax):
    def __init__(self, rpa_data: RpaGestaoAutomacao, runtime_mode: RuntimeEnvironmentConfig):
        self.rpa_data = rpa_data
        self.rpa_data.rpaGestaoAutomacaoParametros = rpa_data.rpaGestaoAutomacaoParametros

        super().__init__(self.rpa_data.id, runtime_mode)

    @staticmethod
    async def filters():
        sleep(2)

        campo_quebra_1 = MediaLoader.Image("5fd19dc2a3065ec1b6ea25cfa8d65cb3").path()
        sleep(1)
        await clickOnTarget(campo_quebra_1)
        sleep(1)

        campo_area = MediaLoader.Image("d40cf8f7b3feab8ea15e803e1bfd2b88").path()
        sleep(0.5)
        await clickOnTarget(campo_area)
        sleep(0.5)

        campo_quebra_2 = MediaLoader.Image("9348098898d4e415e86d03102979c0d4").path()
        sleep(1)
        await clickOnTarget(campo_quebra_2)
        sleep(1)

        campo_setor = MediaLoader.Image("e2fc714c4727ee9395f324cd2e7f331f").path()
        sleep(0.5)
        await clickOnTarget(campo_setor)
        sleep(0.5)


        makeThis(
            task_list=[
                lambda: press("tab"),
                lambda: write("Tipo Movto"),
                lambda: press("tab"),
                lambda: write("Cliente"),
            ],
            cooldown_time=1
        )

        makeThis(
            task_list=[
                lambda: press(['tab'] * 2),
                lambda: press("down"),
                lambda: press(['tab'] * 3),
                lambda: press("left"),
                lambda: press(['tab'] * 4),
                lambda: press("space"),
            ],
            cooldown_time=1
        )

        makeThis(
            task_list=[
                lambda: press(['tab'] * 5),
                lambda: write("51"),
                lambda: press("tab"),
                lambda: write("52"),
                lambda: press("tab"),
                lambda: press("tab"),
                lambda: press("tab"),
            ],
            cooldown_time=2
        )

        data_atual = datetime.now()
        primeiro_dia_mes = data_atual.replace(day=1).strftime("%d/%m/%Y")
        write(primeiro_dia_mes)
        sleep(1)
        press("tab")

        seven_days_ago = (datetime.now() - timedelta(days=0)).strftime("%d/%m/%Y")
        write(seven_days_ago)
        sleep(1.5)
        hotkey("alt", "v")

    async def run(self):
        try:
            rpaGestaoAutomacaoParametros = paramsBuilder(self.rpa_data.rpaGestaoAutomacaoParametros)

            await self.log.create("Iniciando execução do RPA.")

            companies = self.rpa_data.rpaGestaoAutomacaoEmpresas

            for company in companies:
                await self.generate_standard_report(rpaGestaoAutomacaoParametros, company, self.filters)

            await self.log.create("Finalizou execução do RPA com sucesso.")

        except Exception as error:
            traceback.print_exc()
            await self.log.create(f"Finalizou execução do RPA com falha. \n Erro: {error}")
