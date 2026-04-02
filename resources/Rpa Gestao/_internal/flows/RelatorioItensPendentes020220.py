import traceback

from pyautogui import press, hotkey

from dtos import RpaGestaoAutomacao
from core import RuntimeEnvironmentConfig
from time import sleep

from tools import paramsBuilder, MediaLoader
from modules import Promax
from utils import isImageOnScreen, clickOnTarget, makeThis
from config import PROMAX_CREDENTIALS


class RpaProcess(Promax):
    def __init__(self, rpa_data: RpaGestaoAutomacao, runtime_mode: RuntimeEnvironmentConfig):
        self.rpa_data = rpa_data
        self.rpa_data.rpaGestaoAutomacaoParametros = rpa_data.rpaGestaoAutomacaoParametros

        super().__init__(self.rpa_data.id, runtime_mode)

    @staticmethod
    async def filters():

        sleep(2)

        press("f11")

        sleep(2)

        campo_selecionar = MediaLoader.Image("3147da8ab4a0437c15ef51a5cc7f2dc4").path()
        selecionar_found = await isImageOnScreen(campo_selecionar,timeout=10)
        if selecionar_found:
            await clickOnTarget(campo_selecionar)

        geral = MediaLoader.Image("awgiee3o7ee9395f324cd2e7f331f").path()
        geral_found = await isImageOnScreen(geral,timeout=10)
        if geral_found:
            await clickOnTarget(geral)

        pendente = MediaLoader.Image("900150983cd24fb0d6963f7d28e17f72").path()
        pendente_found = await isImageOnScreen(pendente,timeout=5)
        if pendente_found:
            await clickOnTarget(pendente)

        checkbox_garrafeira = MediaLoader.Image("2a38a4a9316c49e5a833517c45d31070").path()
        garrafeira_found = await isImageOnScreen(checkbox_garrafeira,timeout=5)
        if garrafeira_found:
            await clickOnTarget(checkbox_garrafeira)
        sleep(1)

        press("tab")
        press("space")
        press("tab")
        press("space")
        press("tab")
        press("space")
        press("tab")
        press("space")
        press("tab")
        press("space")
        press("tab")
        press("space")

        checkbox_exibir_status = MediaLoader.Image("74b87337454200d4d33f80c4663dc5e5").path()
        exibir_status_found = await isImageOnScreen(checkbox_exibir_status, timeout=5)
        if exibir_status_found:
            await clickOnTarget(checkbox_exibir_status)

        sleep(1)

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
