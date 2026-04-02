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

    @staticmethod
    async def filters():

        mes_atual = date.today().month
        ano_atual = date.today().year

        mes_ano_str = date.today().strftime('%m%Y')

        sleep(4)
        press("tab")
        press("tab")
        press("tab")
        press("tab")
        press("tab")
        press("tab")
        sleep(1)
        write(mes_ano_str)

        press("tab")
        press("tab")
        press("space")
        sleep(2)

        press("tab")
        press("tab")
        press("tab")
        press("tab")
        press("space")
        sleep(2)

        press("tab")
        press("tab")
        press("tab")
        press("tab")
        press("space")
        sleep(2)

        press("tab")
        press("tab")
        press("tab")
        press("tab")
        press("space")
        sleep(2)

        press("tab")
        press("tab")
        press("tab")
        press("tab")
        press("space")
        sleep(2)

        visualizar_button = MediaLoader.Image("q0384ut8qu34tbqr8u3b4j98").path()
        visualizar_found = await isImageOnScreen(visualizar_button,timeout=5)
        if visualizar_found:
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
