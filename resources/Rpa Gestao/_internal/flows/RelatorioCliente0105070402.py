from pyautogui import press, hotkey
from unidecode import unidecode
from time import sleep

from dtos import RpaGestaoAutomacao
from core import RuntimeEnvironmentConfig

from tools import paramsBuilder, MediaLoader

from modules import Promax
from utils import makeThis, clickOnTarget


class RpaProcess(Promax):
    def __init__(self, rpa_data: RpaGestaoAutomacao, runtime_mode: RuntimeEnvironmentConfig):
        self.rpa_data = rpa_data
        self.rpa_data.rpaGestaoAutomacaoParametros = rpa_data.rpaGestaoAutomacaoParametros

        super().__init__(self.rpa_data.id, runtime_mode)

    @staticmethod
    async def filters():
        sleep(2)

        checkbox_todos = MediaLoader.Image("329131699f3e278738597a733adbd3d1").path()
        sleep(1)
        await clickOnTarget(checkbox_todos)

        sleep(1.5)

        checkbox_inativos = MediaLoader.Image("99c4cab0bb8c91127bdf1e40a34f1462").path()
        sleep(1)
        await clickOnTarget(checkbox_inativos)

        sleep(1.5)

        checkbox_as = MediaLoader.Image("81d930eb7998578c2ee32a8f8a7a2ff4").path()
        sleep(1)
        await clickOnTarget(checkbox_as)

        sleep(1.5)

        gerar_csv = MediaLoader.Image("2e764a251bab1e0ad47b53acf87d29af").path()
        sleep(1)
        await clickOnTarget(gerar_csv)

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

                company_name = f'{rpaGestaoAutomacaoParametros["Diretorio"]}\\{company.nome}.csv.inf'
                cnpj = company.cnpj

                await self.log.create("Enviando relatorios para o Gestao.")
                enviado = await self.gestao.sendReportToGestao("/Services/ImportacaoPromax/Relatorio0105070402/JobImportar0105070402", company_name, cnpj)

                await self.log.create(enviado)

            await self.log.create("Finalizou execução do RPA com sucesso.")

        except Exception as error:
            await self.log.create(f"Finalizou execução do RPA com falha. \n Erro: {error}")
