import traceback
from time import sleep
from pyautogui import press, write, hotkey, click
from pyperclip import paste, copy
from datetime import date, timedelta, datetime

from dtos import RpaGestaoAutomacao
from core import RuntimeEnvironmentConfig

from config import PROMAX_CREDENTIALS
from modules import Promax, fetchPendingCte, setCteOrderId
from utils import makeThis, activateCaretBrowsing, isImageOnScreen, clickOnTarget
from tools import paramsBuilder, MediaLoader


class RpaProcess(Promax):
    def __init__(self, rpa_data: RpaGestaoAutomacao, runtime_mode: RuntimeEnvironmentConfig):
        self.rpa_data = rpa_data
        self.rpa_data.rpaGestaoAutomacaoParametros = rpa_data.rpaGestaoAutomacaoParametros

        super().__init__(self.rpa_data.id, runtime_mode)


    @staticmethod
    async def filters(cte_list):

        for cte in cte_list:

            if cte.get("CteTotalEmpresaVlr",0) == 0:
                continue

            hoje = date.today()

            dias_para_quinta = (3 - hoje.weekday()) % 7
            if dias_para_quinta == 0:
                dias_para_quinta = 7  # força a busca para a próxima quinta-feira

            quinta_mais_proxima = hoje + timedelta(days=dias_para_quinta)
            quinta_mais_proxima_f = quinta_mais_proxima.strftime('%d%m%Y')

            data_pedidof = cte.get("CteEmissaoDate")
            data_obj = datetime.strptime(data_pedidof, "%d/%m/%Y")
            data_pedido = data_obj.strftime('%d%m%Y')

            campo_pedido = MediaLoader.Image("0b51aa44fbccd4095576b89823705ce8").path()
            image_found = await isImageOnScreen(campo_pedido, timeout=10)

            if image_found:
                criar_pedido = MediaLoader.Image("3c93757d29fb183272deb53b8c30460f").path()
                pedido_found = await isImageOnScreen(criar_pedido, timeout=10)
                await clickOnTarget(criar_pedido)

                if pedido_found:
                    hotkey("ctrl", "f"),

                    caixa_de_pesquisa = MediaLoader.Image("yuiws4yhgj787ehauj8").path()
                    pesquisa_found = await isImageOnScreen(caixa_de_pesquisa,timeout=10)

                    if pesquisa_found:
                        await clickOnTarget(caixa_de_pesquisa)
                        write("Pedido")
                        press("esc")

                    await activateCaretBrowsing()

                    makeThis(
                        task_list=[
                            lambda: press("right"),
                            lambda: press("right"),
                            lambda: press("right"),
                            lambda: press("backspace"),
                            lambda: hotkey("ctrl", "a"),
                            lambda: hotkey("ctrl", "c"),
                        ],
                        cooldown_time=1
                    )

                    order_id = paste()

                    Cte_Emissao_Datef = cte.get("CteEmissaoDate")
                    data_objt = datetime.strptime(Cte_Emissao_Datef, "%d/%m/%Y")
                    Cte_Emissao_Date = data_objt.strftime('%d%m%Y')

                    campo_fornecedor = MediaLoader.Image("9c6a01f3b8a5353b7a397b8cf77565fa").path()
                    await clickOnTarget(campo_fornecedor)

                    makeThis(
                        task_list=[
                            lambda: write(cte.get("FornecedorCod")),
                            lambda: hotkey("shift", "tab"),
                            lambda: hotkey("ctrl", "a"),
                            lambda: press("backspace"),
                            lambda: write(Cte_Emissao_Date)
                        ],
                        cooldown_time=1
                    )


                    campo_entrega = MediaLoader.Image("852723f4351d511bed8154af66602198").path()
                    await clickOnTarget(campo_entrega)
                    write(Cte_Emissao_Date)

                    campo_contaGerencial = MediaLoader.Image("9e55e9bc9b034364f1848bee6eb5402a").path()
                    await clickOnTarget(campo_contaGerencial)
                    write("2060040005")

                    campo_departamento = MediaLoader.Image("2e95bd5f4503efbdc2ada8a9f0e68085").path()
                    await clickOnTarget(campo_departamento)
                    if cte.get("CteDestinatarioCnpj") == "40188785000192":
                       write("101")
                    else:
                       write("501")

                    press("f11")

                    makeThis(
                        task_list=[
                        lambda: press("tab"),
                        lambda: press("tab"),
                        lambda: press("tab"),
                        lambda: press("tab"),
                        lambda: press("tab"),
                        lambda: press("tab"),
                        lambda: write("transporte"),
                        lambda: press("tab"),
                        lambda: write("003"),
                        lambda: press("tab"),
                        lambda: press("tab"),
                        lambda: write("1"),
                        lambda: press("tab"),
                        lambda: press("tab"),
                        lambda: write(str(cte.get("CteTotalEmpresaVlr"))),
                        ],
                        cooldown_time=1
                    )

                    salvar_button = MediaLoader.Image("7af8iauyu9gday98ga").path()
                    await clickOnTarget(salvar_button)
                    salvar_found = await isImageOnScreen(salvar_button, timeout=10)
                    if salvar_found:
                        hotkey("alt", "s")
                    else:
                        hotkey("alt", "s")


                    campo_parcelas = MediaLoader.Image("b53987yb8324tu9").path()
                    await clickOnTarget(campo_parcelas)
                    campo_parcelas_found = await isImageOnScreen(campo_parcelas, timeout=10)
                    if campo_parcelas_found:
                        write("1")

                    makeThis(
                        task_list=[
                        lambda: press("tab"),
                        lambda: press("down"),
                        lambda: press("down"),
                        lambda: press("down"),
                        lambda: press("down"),
                        lambda: press("tab"),
                        lambda: write (str(quinta_mais_proxima_f)),
                        lambda: press("tab"),
                        ],
                        cooldown_time = 1
                    )

                    data_invalida = MediaLoader.Image("23v8524u6v058v48").path()
                    data_invalida_found = await isImageOnScreen(data_invalida, timeout=5)
                    if data_invalida_found:
                        press("enter")
                        sleep(1)
                        hotkey("alt","o")
                        hotkey("alt","o")
                        hotkey("alt","f4")
                    else:
                        makeThis(
                            task_list=[
                            lambda: hotkey("alt","o"),
                            lambda: hotkey("alt","o"),
                            lambda: hotkey("alt","f4"),
                            ],
                            cooldown_time = 1
                        )
                    await setCteOrderId(cte.get("Id"), order_id)

                    makeThis(
                        task_list=[
                        lambda: press("f7"),
                        lambda: press("enter"),
                        lambda: hotkey("ctrl", "f"),
                        lambda: press("backspace"),
                        lambda: press("esc"),
                        lambda: write("13020301"),
                        lambda: press("enter")
                        ],
                        cooldown_time=1
                    )

    async def run(self):
        try:
            rpaGestaoAutomacaoParametros = paramsBuilder(self.rpa_data.rpaGestaoAutomacaoParametros)

            await self.log.create("Iniciando execução do RPA.")

            companies = self.rpa_data.rpaGestaoAutomacaoEmpresas

            for company in companies:
                cte_list = await fetchPendingCte(company.empresaId)

                if len(cte_list) == 0:
                    continue

                await self.open_promax(company.promaxUrl)
                await self.login(PROMAX_CREDENTIALS["user"], PROMAX_CREDENTIALS["password"])
                await self.company_select(company.promaxUnb)
                await self.close_pop_ups()
                await self.initiate_routine(rpaGestaoAutomacaoParametros["Rotina"])
                await self.log.create("Selecionando filtros do relatório.")
                await self.filters(cte_list)
                await self.closeBrowser()

            await self.log.create("Finalizou execução do RPA com sucesso.")

        except Exception as error:
            traceback.print_exc()
            await self.log.create(f"Finalizou execução do RPA com falha. \n Erro: {error}")