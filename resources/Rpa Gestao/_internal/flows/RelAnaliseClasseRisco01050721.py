from pyautogui import press, hotkey
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
                lambda: press("space"),
            ],
            cooldown_time=1
        )

        sleep(1)

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
                await self.gestao.sendReportToGestao(
                    "/Services/ImportacaoPromax/Relatorio01050721/JobImportar01050721",
                    company_name,
                    company.cnpj)

            await self.log.create("Finalizou execução do RPA com sucesso.")

        except Exception as error:
            await self.log.create(f"Finalizou execução do RPA com falha. \n Erro: {error}")
