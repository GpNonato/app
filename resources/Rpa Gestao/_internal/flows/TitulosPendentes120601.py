from pyautogui import press, write, hotkey
from unidecode import unidecode
from time import sleep

from dtos import RpaGestaoAutomacao
from core import RuntimeEnvironmentConfig


from tools import paramsBuilder, MediaLoader
from modules import Promax
from utils import makeThis, checkImage, clickOnTarget, isImageOnScreen


class RpaProcess(Promax):
    def __init__(self, rpa_data: RpaGestaoAutomacao, runtime_mode: RuntimeEnvironmentConfig):
        self.rpa_data = rpa_data
        self.rpa_data.rpaGestaoAutomacaoParametros = rpa_data.rpaGestaoAutomacaoParametros

        super().__init__(self.rpa_data.id, runtime_mode)

    @staticmethod
    async def filters():
        sleep(1)
        
        caixa_selecionar = MediaLoader.Image("hwn48wb309u84b8w37v78").path()
        selecionar_found = await isImageOnScreen(caixa_selecionar,timeout=10)
        if selecionar_found:
            await clickOnTarget(caixa_selecionar)
        selecionar_alfabetica = MediaLoader.Image("iohrpaejk94ua8w5y8wa3668").path()
        alfabetica_found = await isImageOnScreen(selecionar_alfabetica,timeout=10)
        if alfabetica_found:
            await clickOnTarget(selecionar_alfabetica)

        checkbox_razao_social = MediaLoader.Image("83e83dafda7c9aeecc300716032da66e").path()
        sleep(1.5)
        await clickOnTarget(checkbox_razao_social)

        sleep(1)
        press("tab")

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
                    "/Services/ImportacaoPromax/Relatorio120601/JobImportar120601",
                    company_name,
                    company.cnpj)

            await self.log.create("Finalizou execução do RPA com sucesso.")

        except Exception as error:
            await self.log.create(f"Finalizou execução do RPA com falha. \n Erro: {error}")
