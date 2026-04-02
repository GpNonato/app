import traceback

from pyautogui import press, hotkey, write
from datetime import date

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

        hoje = date.today()
        primeiro_dia_mes = hoje.replace(day=1)

        hoje_str = hoje.strftime("%d%m%Y")
        primeiro_dia_mes_str = primeiro_dia_mes.strftime("%d%m%Y")

        sleep(2)

        press("t")

        check_liberada = MediaLoader.Image("f903fd4af4a0ae1616618894ec1ee3fa").path()
        liberada_found = await isImageOnScreen(check_liberada,timeout=5)
        if liberada_found:
            await clickOnTarget(check_liberada)

        check_c_devolv = MediaLoader.Image("562b530cff1f5bca3b1a4c1ad4ad9962").path()
        c_devolv_found = await isImageOnScreen(check_c_devolv,timeout=5)
        if c_devolv_found:
            await clickOnTarget(check_c_devolv)

        campo_tipo_marca = MediaLoader.Image("b305c28a936ae3c03be903ea8d7aeba3").path()
        tipo_found = await isImageOnScreen(campo_tipo_marca,timeout=5)
        if tipo_found:
            await clickOnTarget(campo_tipo_marca)

        hotkey("shift", "tab")
        hotkey("shift", "tab")
        write(primeiro_dia_mes_str)
        press("tab")
        write(hoje_str)
        sleep(1)
        press("f11")
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
