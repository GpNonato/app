from pyautogui import press, hotkey, write
from datetime import datetime, timedelta
from time import sleep
import traceback

from dtos import RpaGestaoAutomacao
from core import RuntimeEnvironmentConfig

from tools import paramsBuilder, MediaLoader
from modules import Promax
from utils import makeThis, clickOnTarget, isImageOnScreen
from config import PROMAX_CREDENTIALS


class RpaProcess(Promax):
    def __init__(self, rpa_data: RpaGestaoAutomacao, runtime_mode: RuntimeEnvironmentConfig):
        self.rpa_data = rpa_data
        self.rpa_data.rpaGestaoAutomacaoParametros = rpa_data.rpaGestaoAutomacaoParametros

        super().__init__(self.rpa_data.id, runtime_mode)

    @staticmethod
    async def filters():
        hoje = datetime.now()

        if hoje.day == 1:
            mes_atual = (hoje - timedelta(days=1)).strftime("%m-%Y")
        elif hoje.day ==2:
            mes_atual = (hoje - timedelta(days=2)).strftime("%m-%Y")
        else:
            mes_atual = hoje.strftime("%m-%Y")

        campo_selecionar = MediaLoader.Image("yw754w5y984skfd").path()
        selecionar_found = await isImageOnScreen(campo_selecionar,timeout=10)
        if selecionar_found:
            await clickOnTarget(campo_selecionar)
        makeThis(
            task_list=[
                lambda: write("Alfa"),
                lambda: press("tab"),
                lambda: press("tab"),
                lambda: press("tab"),
                lambda: write(mes_atual),
                lambda: press("tab"),
                lambda: hotkey("alt", "v"),
            ],
            cooldown_time=1
        )
    async def run(self):
        try:
            rpaGestaoAutomacaoParametros = paramsBuilder(self.rpa_data.rpaGestaoAutomacaoParametros)

            await self.log.create("Iniciando execução do RPA.")

            companies = self.rpa_data.rpaGestaoAutomacaoEmpresas

            for company in companies:
                company_name = f"{rpaGestaoAutomacaoParametros["Rotina"]}_{company.nome.split()[1].lower()}_{datetime.now().strftime("%d-%m-%Y")}"
                try:
                    await self.open_promax(company.promaxUrl)
                    await self.login(PROMAX_CREDENTIALS["user"], PROMAX_CREDENTIALS["password"])
                    await self.company_select(company.promaxUnb)
                    await self.close_pop_ups()
                    await self.initiate_routine(rpaGestaoAutomacaoParametros["Rotina"])
                    sleep(3)
                    await self.filters()

                    await self.save_file(
                        rpaGestaoAutomacaoParametros["Diretorio"],
                        f"{rpaGestaoAutomacaoParametros["Rotina"]}_{company.nome.split()[1].lower()}"
                    )

                    file_path = f"{rpaGestaoAutomacaoParametros["Diretorio"]}\\{company_name}.csv.inf"
                    await self.log.create("Enviando relatorios para o Gestao.")
                    await self.gestao.auth()
                    await self.gestao.sendReportToGestao("/Services/ImportacaoPromax/Relatorio020253"
                                                         "/Import",
                                                         file_path)
                except Exception as error:
                    print(error)

                finally:
                    await self.closeBrowser()

            await self.log.create("Finalizou execução do RPA com sucesso.")

        except Exception as error:
            traceback.print_exc()
            await self.log.create(f"Finalizou execução do RPA com falha. \n Erro: {error}")