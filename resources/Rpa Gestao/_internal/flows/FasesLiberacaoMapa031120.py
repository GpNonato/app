import traceback

from pyautogui import press, hotkey, write
from datetime import date

from dtos import RpaGestaoAutomacao
from core import RuntimeEnvironmentConfig
from time import sleep

from tools import paramsBuilder, MediaLoader
from modules import Promax
from utils import isImageOnScreen, clickOnTarget
from config import PROMAX_CREDENTIALS


class RpaProcess(Promax):
    def __init__(self, rpa_data: RpaGestaoAutomacao, runtime_mode: RuntimeEnvironmentConfig):
        self.rpa_data = rpa_data
        self.rpa_data.rpaGestaoAutomacaoParametros = rpa_data.rpaGestaoAutomacaoParametros

        super().__init__(self.rpa_data.id, runtime_mode)

    async def filters(self, rpaGestaoAutomacaoParametros, company):
        ano_atual = date.today().year
        inicio_primeiro_semestre = date(ano_atual, 1, 1).strftime('%d%m%Y')
        fim_primeiro_semestre = date(ano_atual, 6, 30).strftime('%d%m%Y')
        inicio_segundo_semestre = date(ano_atual, 7, 1).strftime('%d%m%Y')
        fim_segundo_semestre = date(ano_atual, 12, 31).strftime('%d%m%Y')

        sleep(2)
        press("m")
        press("tab")
        press("tab")
        write(inicio_primeiro_semestre)
        press("tab")
        write(fim_primeiro_semestre)

        visualizar_button = MediaLoader.Image("q0384ut8qu34tbqr8u3b4j98").path()
        if await isImageOnScreen(visualizar_button, timeout=5):
            await clickOnTarget(visualizar_button)
            await self.save_file(
                rpaGestaoAutomacaoParametros["Diretorio"],
                f"{rpaGestaoAutomacaoParametros['Rotina']}_{company.nome.split()[1].lower()}_1"
            )

        sleep(2)
        press("f11")

        hotkey("alt", "f4")
        sleep(4)

        write("031120")
        press("enter")
        sleep(4)

        press("m")
        press("tab")
        press("tab")
        write(inicio_segundo_semestre)
        press("tab")
        write(fim_segundo_semestre)

        if await isImageOnScreen(visualizar_button, timeout=5):
            await clickOnTarget(visualizar_button)

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
                    await self.filters(rpaGestaoAutomacaoParametros, company)

                    await self.save_file(
                        rpaGestaoAutomacaoParametros["Diretorio"],
                        f"{rpaGestaoAutomacaoParametros['Rotina']}_{company.nome.split()[1].lower()}_2"
                    )
                except Exception as error:
                    print(error)
                finally:
                    await self.closeBrowser()

            await self.log.create("Finalizou execução do RPA com sucesso.")
        except Exception as error:
            traceback.print_exc()
            await self.log.create(f"Finalizou execução do RPA com falha. \n Erro: {error}")
