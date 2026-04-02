from pyautogui import press, hotkey, write
from datetime import datetime, timedelta
from time import sleep
import traceback

from dtos import RpaGestaoAutomacao
from core import RuntimeEnvironmentConfig

from tools import paramsBuilder
from modules import Promax
from utils import makeThis
from config import PROMAX_CREDENTIALS


class RpaProcess(Promax):
    def __init__(self, rpa_data: RpaGestaoAutomacao, runtime_mode: RuntimeEnvironmentConfig):
        self.rpa_data = rpa_data
        self.rpa_data.rpaGestaoAutomacaoParametros = rpa_data.rpaGestaoAutomacaoParametros

        super().__init__(self.rpa_data.id, runtime_mode)


    @staticmethod
    async def filters():
        inicio_do_ano = datetime(year=2025, month=1, day=1)
        seis_meses_depois = inicio_do_ano + timedelta(days=182)


        makeThis(
            task_list=[
                lambda: write("Mapa"),
                lambda: press('tab'),
                lambda: press('tab'),
                lambda: write(inicio_do_ano.strftime("%d/%m/%Y")),
                lambda: press('tab'),
                lambda: write(seis_meses_depois.strftime("%d/%m/%Y"))
            ],
            cooldown_time=1
        )
        hotkey("alt", "v")
        sleep(1.5)

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
                    await self.filters()
                    await self.save_file(
                        rpaGestaoAutomacaoParametros["Diretorio"],
                        company_name
                    )
                    file_path = f"{rpaGestaoAutomacaoParametros["DiretorioCarga"]}\\{company_name}.csv.inf"

                    await self.log.create("Enviando relatorios para o Gestao.")
                    await self.gestao.auth()
                    await self.gestao.sendReportToGestao("/Services/ImportacaoPromax/Relatorio031120/Import",
                                                         file_path)

                except Exception as error:
                    print(error)

                finally:
                    await self.closeBrowser()

            await self.log.create("Finalizou execução do RPA com sucesso.")

        except Exception as error:
            traceback.print_exc()
            await self.log.create(f"Finalizou execução do RPA com falha. \n Erro: {error}")
