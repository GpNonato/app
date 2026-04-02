from datetime import datetime, timedelta
from pyautogui import press, hotkey, write
from unidecode import unidecode

from dtos import RpaGestaoAutomacao
from core import RuntimeEnvironmentConfig

from tools import paramsBuilder

from modules import Promax
from utils import makeThis

from time import sleep


class RpaProcess(Promax):
    def __init__(self, rpa_data: RpaGestaoAutomacao, runtime_mode: RuntimeEnvironmentConfig):
        self.rpa_data = rpa_data
        self.rpa_data.rpaGestaoAutomacaoParametros = rpa_data.rpaGestaoAutomacaoParametros

        super().__init__(self.rpa_data.id, runtime_mode)

    @staticmethod
    async def filters():
        makeThis(
            task_list=[
                lambda: hotkey("shift", "tab"),
                lambda: hotkey("shift", "tab"),
                lambda: sleep(2)
            ],
            cooldown_time=1
        )

        six_months_ago = (datetime.now() - timedelta(days=30 * 6)).strftime("%d %m %Y")

        sleep(2)

        makeThis(
            task_list=[
                lambda: write(six_months_ago),
                lambda: sleep(1.5),
                lambda: press("tab"),
                lambda: press("tab"),
                lambda: press("tab"),
                lambda: press("tab"),
            ],
            cooldown_time=1
        )

        makeThis(
            task_list=[
                lambda: press("enter"),
            ],
            cooldown_time=1
        )

    async def run(self):
        try:
            rpaGestaoAutomacaoParametros = paramsBuilder(self.rpa_data.rpaGestaoAutomacaoParametros)

            await self.log.create("Iniciando execução do RPA.")

            companies = self.rpa_data.rpaGestaoAutomacaoEmpresas

            for company in companies:
                company.nome = (
                    unidecode(company.nome.strip())
                    .lower()
                    .replace(" ", "_")
                )

                await self.generate_standard_report(rpaGestaoAutomacaoParametros, company, self.filters)

                company_name = f'{rpaGestaoAutomacaoParametros["DiretorioCarga"]}\\{company.nome}.csv.inf'

                await self.log.create("Enviando relatorios para o Gestao.")
                await self.gestao.sendReportToGestao("/Services/ImportacaoPromax/Relatorio210407/JobImportar210407",
                                                     company_name,
                                                     company.cnpj)

            await self.log.create("Finalizou execução do RPA com sucesso.")

        except Exception as error:
            await self.log.create(f"Finalizou execução do RPA com falha. \n Erro: {error}")
            raise Exception(error)
