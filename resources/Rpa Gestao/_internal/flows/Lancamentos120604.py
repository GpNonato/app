from datetime import datetime, timedelta
from pyautogui import press, write, hotkey
from time import sleep

from dtos import RpaGestaoAutomacao
from core import RuntimeEnvironmentConfig

from tools import paramsBuilder
from unidecode import unidecode

from modules import Promax
from utils import makeThis


class RpaProcess(Promax):
    def __init__(self, rpa_data: RpaGestaoAutomacao, runtime_mode: RuntimeEnvironmentConfig):
        self.rpa_data = rpa_data
        self.rpa_data.rpaGestaoAutomacaoParametros = rpa_data.rpaGestaoAutomacaoParametros

        super().__init__(self.rpa_data.id, runtime_mode)

    @staticmethod
    async def filters():
        sleep(1)

        makeThis(
            task_list=[
                lambda: write("pagos"),
                lambda: press("tab"),
                lambda: write("contabil"),
                lambda: press("tab"),
                lambda: press("tab"),
                lambda: press("tab"),
                lambda: press("space"),
                lambda: press("tab"),
                lambda: press("tab"),
                lambda: press("tab"),
            ],
            cooldown_time=1
        )

        seven_days_ago = (datetime.now() - timedelta(days=7)).strftime("%d/%m/%Y")
        write(seven_days_ago),
        press("tab"),
        hotkey("alt", "v")

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
                await self.gestao.sendReportToGestao("/Services/ImportacaoPromax/Relatorio120604/JobImportar120604",
                                                     company_name,
                                                     company.cnpj)

            await self.log.create("Finalizou execução do RPA com sucesso.")

        except Exception as error:
            await self.log.create(f"Finalizou execução do RPA com falha. \n Erro: {error}")
