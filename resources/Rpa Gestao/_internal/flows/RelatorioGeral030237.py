from pyautogui import press, hotkey, write
from datetime import datetime, timedelta
from time import sleep
import traceback
import os

from dtos import RpaGestaoAutomacao
from core import RuntimeEnvironmentConfig
from modules.Promax.methods import export_csv_file

from tools import paramsBuilder, MediaLoader
from modules import Promax
from utils import makeThis, isImageOnScreen, clickOnTarget
from config import PROMAX_CREDENTIALS


class RpaProcess(Promax):
    def __init__(self, rpa_data: RpaGestaoAutomacao, runtime_mode: RuntimeEnvironmentConfig):
        self.rpa_data = rpa_data
        self.rpa_data.rpaGestaoAutomacaoParametros = rpa_data.rpaGestaoAutomacaoParametros

        super().__init__(self.rpa_data.id, runtime_mode)

    @staticmethod
    async def filters():

        press("down")

        hotkey("alt", "v")
        sleep(4)
        hotkey("alt", "c")


    async def run(self):
        try:
            rpaGestaoAutomacaoParametros = paramsBuilder(self.rpa_data.rpaGestaoAutomacaoParametros)

            await self.log.create("Iniciando execução do RPA.")

            companies = self.rpa_data.rpaGestaoAutomacaoEmpresas

            pasta_map = {
                "a3p": "A3P",
                "cachoeiro": "CACHOEIRO",
                "janauba": "JANAUBA",
                "januaria": "JANUARIA",
                "joao": "JOAO PINHEIRO",
                "manhuaçu": "FARID MH",
                "mariana": "FARID MA",
                "ponte": "FARID PN",
                "unai": "UNAI",
                "lafaiete": "FARID CL",
                "são joão": "FARID SJ",
            }

            base_path = r"\\winsrvfs02\share$\OPERAÇÕES\CORPORATIVO\21_CTE\01_Faturamento\02_Gerador de CTE's\RELATÓRIOS PROMAX"

            for company in companies:
                nome_raw = company.nome.strip().lower().replace("revenda ", "")
                print(company.nome)
                pasta_revenda = None
                for key, folder in pasta_map.items():
                    if key in nome_raw:
                        pasta_revenda = folder
                        break

                if not pasta_revenda:
                    raise ValueError(f"Empresa “{company.nome}” sem mapeamento de pasta!")

                full_folder = os.path.join(base_path, pasta_revenda)
                os.makedirs(full_folder, exist_ok=True)

                try:
                    await self.open_promax(company.promaxUrl)
                    await self.login(PROMAX_CREDENTIALS["user"], PROMAX_CREDENTIALS["password"])
                    await self.company_select(company.promaxUnb)
                    await self.close_pop_ups()
                    await self.initiate_routine(rpaGestaoAutomacaoParametros["Rotina"])
                    sleep(1)
                    await self.filters()

                    rotina = rpaGestaoAutomacaoParametros["Rotina"]
                    if len(rotina) % 2 != 0:
                        rotina = rotina.zfill(len(rotina) + 1)
                    formatted_rotina = '.'.join([rotina[i:i + 2] for i in range(0, len(rotina), 2)])

                    filename = f"{formatted_rotina}"
                    await export_csv_file(full_folder, filename)

                except Exception as error:
                    print(f"Erro em {company.nome}: {error}")
                finally:
                    await self.closeBrowser()

            await self.log.create("Finalizou execução do RPA com sucesso.")

        except Exception as error:
            traceback.print_exc()
            await self.log.create(f"Finalizou execução do RPA com falha. \n Erro: {error}")