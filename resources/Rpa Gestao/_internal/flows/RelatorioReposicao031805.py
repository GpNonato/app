import traceback

from pyautogui import press, hotkey, write
from datetime import date, timedelta

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

        sleep(2)

        hoje = date.today()
        semana_passada = hoje - timedelta(days=7)
        hoje = hoje.strftime("%d%m%Y")
        semana_passada = semana_passada.strftime("%d%m%Y")

        press("tab")
        write(semana_passada, interval= 0.3)
        press("tab")
        write(hoje, interval= 0.3)
        press("tab")
        hotkey("alt", "v")

    async def run(self):
        try:
            rpaGestaoAutomacaoParametros = paramsBuilder(self.rpa_data.rpaGestaoAutomacaoParametros)

            await self.log.create("Iniciando execução do RPA.")

            companies = self.rpa_data.rpaGestaoAutomacaoEmpresas

            for company in companies:

                try:
                    diretorio = rpaGestaoAutomacaoParametros["Diretorio"]
                    nome_base = f"{rpaGestaoAutomacaoParametros["Rotina"]}_{company.nome.split()[1].lower()}"

                    await self.open_promax(company.promaxUrl)
                    await self.login(PROMAX_CREDENTIALS["user"], PROMAX_CREDENTIALS["password"])
                    await self.company_select(company.promaxUnb)
                    await self.close_pop_ups()
                    await self.initiate_routine(rpaGestaoAutomacaoParametros["Rotina"])
                    await self.filters()
                    await self.save_file(rpaGestaoAutomacaoParametros["Diretorio"],f"{rpaGestaoAutomacaoParametros["Rotina"]}_{company.nome.split()[1].lower()}")

                    file_path = f"{diretorio}\\{nome_base}.csv.inf"
                    await self.log.create(f"O caminho é: {file_path} ")

                    cnpj = company.cnpj
                    await self.log.create(f"O Cnpj é: {cnpj}")
                    await self.gestao.auth()

                    await self.log.create("Enviando arquivo para o Gestão...")

                    enviado = await self.gestao.sendReportToGestao("/Services/ImportacaoPromax/Relatorio031805/Import", file_path, cnpj)

                    await self.log.create(enviado)

                except Exception as error:
                    print(error)

                finally:
                    await self.closeBrowser()

            await self.log.create("Finalizou execução do RPA com sucesso.")

        except Exception as error:
            traceback.print_exc()
            await self.log.create(f"Finalizou execução do RPA com falha. \n Erro: {error}")
