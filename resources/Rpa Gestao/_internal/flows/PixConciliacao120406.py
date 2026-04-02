import traceback
from time import sleep
from datetime import datetime, timedelta

from dtos import RpaGestaoAutomacao
from core import RuntimeEnvironmentConfig

from config import PROMAX_CREDENTIALS
from utils import (isImageOnScreen, clickOnTarget,getPageFromClipboard)
from modules import Promax, fetchPix, setAsReconcilied, applyFilters, find_pix
from tools import paramsBuilder, MediaLoader


class PixCobrancaNotasFiscaisRow:
    def __init__(self, data: dict):
        self.NotaFiscalId = data.get("NotaFiscalId", "")
        self.EmpresaId = data.get("EmpresaId", "")
        self.PixBancoRecebimento = data.get("PixBancoRecebimento", "")
        self.PixVlrPago = data.get("PixVlrPago", "")
        self.PixDtPagamento = data.get("PixDtPagamento", "")
        self.PromaxPortadorId = data.get("PromaxPortadorId", "")

    def to_dict(self):
        return self.__dict__


class IntegracaoPromaxPortadorRow:
    def __init__(self, data: dict):
        self.Id = data.get("Id", "")
        self.EmpresaId = data.get("EmpresaId", "")
        self.BancoId = data.get("BancoId", "")

    def to_dict(self):
        return self.__dict__


class BreakLoopException(Exception):
    pass


class RpaProcess(Promax):
    def __init__(self, rpa_data: RpaGestaoAutomacao, runtime_mode: RuntimeEnvironmentConfig):
        self.rpa_data = rpa_data
        self.rpa_data.rpaGestaoAutomacaoParametros = rpa_data.rpaGestaoAutomacaoParametros

        super().__init__(self.rpa_data.id, runtime_mode)

    @staticmethod
    async def filters(portador: str, date: str, pix_data_list: list):
        sleep(3)
        pix_list = [PixCobrancaNotasFiscaisRow(pix.__dict__) for pix in pix_data_list]

        reconcilied_pix_id_list = []
        reconciliation_count = 0

        await applyFilters(portador, date)
        number_of_pages = getPageFromClipboard()

        save_button = MediaLoader.Image("47bce5c74f589f4867dbd57e9ca9f808").path()
        next_button = MediaLoader.Image("92eb5ffee6ae2fec3ad71c777531578f").path()

        try:
            while len(pix_list) > 0 and number_of_pages > 0:
                pix_not_found_in_page = []

                for pix in pix_list:
                    found_pix = await find_pix(pix)

                    if not found_pix:
                        pix_not_found_in_page.append(pix)
                    else:
                        reconcilied_pix_id_list.append(pix.NotaFiscalId)
                        pix_list.remove(pix)
                        reconciliation_count += 1

                        if reconciliation_count % 10 == 0:
                            await clickOnTarget(save_button)
                            await applyFilters(portador, date)
                            number_of_pages = getPageFromClipboard()

                if pix_not_found_in_page:
                    next_page_found = await isImageOnScreen(next_button, 3)
                    if next_page_found:
                        await clickOnTarget(next_button)
                        number_of_pages -= 1
                    else:
                        break

        except BreakLoopException:
            pass

        finally:
            print(reconcilied_pix_id_list)
            await clickOnTarget(save_button)

            with open('log_reconcilied.txt', 'a') as arquivo:
                for item in reconcilied_pix_id_list:
                    arquivo.write(str(item) + '\n')

            with open('log_not_reconcilied.txt', 'a') as arquivo:
                for item in pix_list:
                    arquivo.write(str(item.NotaFiscalId) + '\n')

            await setAsReconcilied(reconcilied_pix_id_list, True)

            if number_of_pages == 0 or number_of_pages == 1:
                not_founded_pix = [item.NotaFiscalId for item in pix_list]
                await setAsReconcilied(not_founded_pix, False)

    async def run(self):
        try:
            data_atual = datetime.today().strftime("%Y-%m-%d")
            trinta_dias_atras = (datetime.today() - timedelta(days=30)).strftime("%Y-%m-%d")
            rpaGestaoAutomacaoParametros = paramsBuilder(self.rpa_data.rpaGestaoAutomacaoParametros)

            await self.log.create("Iniciando execução do RPA.")

            companies = self.rpa_data.rpaGestaoAutomacaoEmpresas

            while True:
                for company in companies:
                    self.company_id = company.empresaId
                    pix_data = await fetchPix(company.empresaId, start_date=trinta_dias_atras, end_date=data_atual)

                    if not pix_data:
                        continue

                    for portador, datas in pix_data.items():  #
                        for date, pix_list in datas.items():  #
                            pix_por_portador = [PixCobrancaNotasFiscaisRow(pix) for pix in pix_list]

                            try:
                                await self.open_promax(company.promaxUrl)
                                await self.login(PROMAX_CREDENTIALS["user"], PROMAX_CREDENTIALS["password"])
                                await self.company_select(company.promaxUnb)
                                await self.close_pop_ups()
                                await self.initiate_routine(rpaGestaoAutomacaoParametros["Rotina"])
                                await self.log.create("Selecionando filtros do relatório.")

                                #
                                await self.filters(portador=str(portador).rjust(3, "0"), date=str(date),
                                                   pix_data_list=pix_por_portador)

                            except Exception as error:
                                await self.log.create(f"Erro encontrado: {error}")
                                raise Exception(error)

                            finally:
                                await self.closeBrowser()

                response = await fetchPix(self.company_id, start_date=trinta_dias_atras, end_date=data_atual)

                if not response:
                    break

        except Exception as error:
            traceback.print_stack()
            await self.log.create(f"Finalizou execução do RPA com falha. \n Erro: {error}")
            raise Exception(error)
