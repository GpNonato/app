from datetime import datetime, timedelta
from pyautogui import press, write, hotkey
from time import sleep

from dtos import RpaGestaoAutomacao
from core import RuntimeEnvironmentConfig

from tools import paramsBuilder, MediaLoader
from modules import Promax, Gestao
from utils import makeThis, clickOnTarget


class RpaProcess(Promax):
    def __init__(self, rpa_data: RpaGestaoAutomacao, runtime_mode: RuntimeEnvironmentConfig):
        self.rpa_data = rpa_data
        self.rpa_data.rpaGestaoAutomacaoParametros = rpa_data.rpaGestaoAutomacaoParametros

        super().__init__(self.rpa_data.id, runtime_mode)

    @staticmethod
    async def filters():
        makeThis(
            task_list=[
                lambda: sleep(3),
                lambda: write("t"),
                lambda: press("tab"),

            ],
            cooldown_time=1
        )

        tipo_movto = MediaLoader.Image("7815696ecbf1c96e6894b779456d330e").path()  ##Clica no campo produto
        await clickOnTarget(tipo_movto)

        sleep(1)

        hotkey("ctrl", "a")
        write("51")
        sleep(1.5)
        press("tab")
        write("51")
        press("tab")

        ten_days_ago = (datetime.now() - timedelta(days=10)).strftime("%d/%m/%Y")
        write(ten_days_ago)

        hotkey("alt", "v")

    async def run(self):
        try:
            rpaGestaoAutomacaoParametros = paramsBuilder(self.rpa_data.rpaGestaoAutomacaoParametros)

            await self.log.create("Iniciando execução do RPA.")

            companies = self.rpa_data.rpaGestaoAutomacaoEmpresas

            gestao = Gestao()

            for company in companies:
                await self.generate_standard_report(rpaGestaoAutomacaoParametros, company, self.filters)
                await gestao.auth()
                await gestao.sendReportToGestao("/Services/ImportacaoPromax/Relatorio030237/JobImportar030237",
                                                f"{rpaGestaoAutomacaoParametros['DiretorioCarga']}\\{company.nome}.csv.inf")

            await self.log.create("Finalizou execução do RPA com sucesso.")

        except Exception as error:
            await self.log.create(f"Finalizou execução do RPA com falha. \n Erro: {error}")
            raise Exception(error)
