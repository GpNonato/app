import traceback

from pyautogui import press

from dtos import RpaGestaoAutomacao
from core import RuntimeEnvironmentConfig
from modules.Promax.methods import export_csv_file
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

        sleep(2)
        checkbox_venda = MediaLoader.Image("584da0a485f209242059e6de66aac904").path()
        venda_found = await isImageOnScreen(checkbox_venda,timeout=5)
        if venda_found:
            await clickOnTarget(checkbox_venda)

        checkbox_bloqueado = MediaLoader.Image("ff0eb2864feb22354747f8c85d42ccb5").path()
        bloqueado_found = await isImageOnScreen(checkbox_bloqueado,timeout=5)
        if bloqueado_found:
            await clickOnTarget(checkbox_bloqueado)

        checkbox_inativo = MediaLoader.Image("e6481c46e064c35e8f6e371d72912507").path()
        inativo_found = await isImageOnScreen(checkbox_inativo,timeout=5)
        if inativo_found:
            await clickOnTarget(checkbox_inativo)

        csv_button = MediaLoader.Image("2e764a251bab1e0ad47b53acf87d29af").path()
        csv_found = await isImageOnScreen(csv_button,timeout=5)
        if csv_found:
            await clickOnTarget(csv_button)

        error_warning = MediaLoader.Image("b245yu692b28").path()
        error_found = await isImageOnScreen(error_warning, timeout=10)
        if error_found:
            press("enter")
            warning = MediaLoader.Image("74w5by97ybw5b7yw598j").path()
            warning_found = await isImageOnScreen(warning, timeout=240)
            if warning_found:
                press("enter")

        else:
            warning = MediaLoader.Image("74w5by97ybw5b7yw598j").path()
            warning_found = await isImageOnScreen(warning, timeout=240)
            if warning_found:
                press("enter")

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
                    await export_csv_file(
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
