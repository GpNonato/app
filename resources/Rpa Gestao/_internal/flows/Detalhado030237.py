import traceback
from time import sleep
from datetime import datetime, timedelta
from pyautogui import press, write, hotkey

from dtos import RpaGestaoAutomacao
from core import RuntimeEnvironmentConfig

from modules import Promax
from utils import makeThis, checkImage, clickOnTarget
from tools import paramsBuilder, MediaLoader


class RpaProcess(Promax):
    def __init__(self, rpa_data: RpaGestaoAutomacao, runtime_mode: RuntimeEnvironmentConfig):
        self.rpa_data = rpa_data
        self.rpa_data.rpaGestaoAutomacaoParametros = rpa_data.rpaGestaoAutomacaoParametros

        super().__init__(self.rpa_data.id, runtime_mode)
        

    @staticmethod
    async def filters():
        sleep(3)

        makeThis(
            task_list=[
                lambda: write("motorista"),
                lambda: press("tab"),
                lambda: write("vendedor"),
                lambda: press("tab"),
                lambda: write("tipo movto"),
                lambda: press("tab"),
            ],
            cooldown_time=1
        )

        makeThis(
            task_list=[
                lambda: press("tab"),
                lambda: press("tab"),
                lambda: press("left"),
            ],
            cooldown_time=1
        )

        campo_data = MediaLoader.Image("7815696ecbf1c96e6894b779456d330e").path()
        sleep(2)
        await clickOnTarget(campo_data)
        sleep(2)

        press("tab")
        sleep(1.5)
        press("tab")
        sleep(1.5)

        seven_days_ago = (datetime.now() - timedelta(days=7)).strftime("%d/%m/%Y")
        write(seven_days_ago)
        sleep(4)
        hotkey("alt","v")

    async def run(self):
        try:
            rpaGestaoAutomacaoParametros = paramsBuilder(self.rpa_data.rpaGestaoAutomacaoParametros)
            
            await self.log.create("Iniciando execução do RPA.")

            companies = self.rpa_data.rpaGestaoAutomacaoEmpresas


            for company in companies:
                await self.generate_standard_report(rpaGestaoAutomacaoParametros, company, self.filters)

                file_path = f"{rpaGestaoAutomacaoParametros['DiretorioCarga']}\\{company.nome}.csv.inf"

                await self.log.create("Enviando relatorios para o Gestao.")
                await self.gestao.sendReportToGestao("/Services/ImportacaoPromax/Relatorio030237Detalhado/Import",
                                                     file_path)

            await self.log.create("Finalizou execução do RPA com sucesso.")

        except Exception as error:
            traceback.print_exc()
            await self.log.create(f"Finalizou execução do RPA com falha. \n Erro: {error}")
