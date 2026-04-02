from time import sleep
from datetime import datetime, timedelta, date
from pyautogui import press, write, hotkey

from dtos import RpaGestaoAutomacao
from core import RuntimeEnvironmentConfig

from tools import paramsBuilder, MediaLoader
from config import PROMAX_CREDENTIALS
from utils import makeThis, isImageOnScreen, clickOnTarget
from modules import Promax, fetchApprovedCte, setLancamentoCteDate, setCteOrderIdToNull, setLancamentoWinthorDate


class RpaProcess(Promax):
    def __init__(self, rpa_data: RpaGestaoAutomacao, runtime_mode: RuntimeEnvironmentConfig):
        self.rpa_data = rpa_data
        self.rpa_data.rpaGestaoAutomacaoParametros = rpa_data.rpaGestaoAutomacaoParametros

        super().__init__(self.rpa_data.id, runtime_mode)

    @staticmethod
    async def filters(cte_list):

        data_atual = (datetime.now() - timedelta(days=0)).strftime("%d/%m/%Y")
        mes_atual = (datetime.now() - timedelta(days=0)).strftime("%m/%Y")
        data_cinco_dias = (datetime.now() + timedelta(days=5)).strftime("%d/%m/%Y")

        hoje = date.today()
        dias_para_quinta = (3 - hoje.weekday()) % 7
        if dias_para_quinta == 0:
            dias_para_quinta = 7  # força a busca para a próxima quinta-feira

        quinta_mais_proxima = hoje + timedelta(days=dias_para_quinta)
        quinta_mais_proxima_f = quinta_mais_proxima.strftime('%d/%m/%Y')


        for cte in cte_list:
            data_emissao = datetime.fromisoformat(cte.get("CteEmissaoDate")).strftime('%d/%m/%Y')
            pedidoId = cte.get("PromaxPedidoId")
            cte_numero = cte.get("CteNumero")
            cte_valor = cte.get("CteTotalEmpresaVlr")
            cte_valor_str = f"{cte_valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

            print(pedidoId)

            campo_pedido_null = MediaLoader.Image("guhnahugw43h47wg4h78h78g3q").path()
            campo_pedido_null_found = await isImageOnScreen(campo_pedido_null,timeout=5)
            if campo_pedido_null_found:
                press("f5")

            campo_pedido = MediaLoader.Image("1973gtfu131983hf829h3").path()
            pedido_found = await isImageOnScreen(campo_pedido, timeout=5)

            if pedido_found:
                await clickOnTarget(campo_pedido)
                makeThis(
                    task_list=[
                        lambda: write(pedidoId),
                        lambda: press("tab")
                    ],
                    cooldown_time=1
                )

            nao_cadastrado = MediaLoader.Image("iw4b576843aup").path()
            nao_cadastrado_found = await isImageOnScreen(nao_cadastrado,timeout=5)

            if nao_cadastrado_found:
                press("enter")
                press("f5")
                await setCteOrderIdToNull(cte["Id"])
                continue

            nao_cadastrado_secundario = MediaLoader.Image("uodvryt96897").path()
            nao_cadastrado_found_secundario = await isImageOnScreen(nao_cadastrado_secundario,timeout=5)

            if nao_cadastrado_found_secundario:
                press("enter")
                press("f5")
                await setCteOrderIdToNull(cte["Id"])
                continue

            pedido_almoxarifado = MediaLoader.Image("d87c95c7bbabc45f89ef9bbdbf6908c5").path()
            warning_almoxarifado = await isImageOnScreen(pedido_almoxarifado, timeout=5)

            if warning_almoxarifado:
                press("enter")
                press("f5")
                await setCteOrderIdToNull(cte["Id"])
                continue

            pedido_nao_cadastrado = MediaLoader.Image("240c21e9bea5b4862425ca3b64b693f9").path()
            warning_nao_cadastrado = await isImageOnScreen(pedido_nao_cadastrado, timeout=5)

            if warning_nao_cadastrado:
                press("enter")
                press("f5")
                await setCteOrderIdToNull(cte["Id"])
                continue

            pedido_entregue = MediaLoader.Image("0cc175b9c0f1b6a831c399e269772661").path()
            pedido_warning = await isImageOnScreen(pedido_entregue, timeout=5)

            if pedido_warning:
                press("enter")
                press("f5")
                await setLancamentoCteDate(cte["Id"],quinta_mais_proxima_f)
                continue

            campo_modelo = MediaLoader.Image("t1331wsdeggegwgweg3").path()
            modelo_found = await isImageOnScreen(campo_modelo, timeout=5)
            nf_compra = MediaLoader.Image("28g63782963n").path()
            if modelo_found:
                await clickOnTarget(campo_modelo)
                await clickOnTarget(nf_compra)

            nota_serie = MediaLoader.Image("vw8u7hr4g98u32h4").path()
            await clickOnTarget(nota_serie)

            makeThis(
                task_list=[
                    lambda: write(cte_numero),
                    lambda: press("tab"),
                    lambda: write("0"),
                    lambda: press("tab"),
                ],
                cooldown_time=1
            )

            warning = MediaLoader.Image("a5391beadda64c9ab94d40a489a218c9").path()
            image_found = await isImageOnScreen(warning, timeout=5)

            if image_found:
                press("enter")
                hotkey("alt", "c")
                continue

            makeThis(
                task_list=[
                    lambda: write("717"),
                ],
                cooldown_time=1
            )

            campo_deposito = MediaLoader.Image("ae97gt8g7ae76q3").path()
            await clickOnTarget(campo_deposito)

            makeThis(
                task_list=[
                    lambda: hotkey("ctrl", "a"),
                    lambda: press("backspace"),
                    lambda: write("1"),
                    lambda: press("tab"),
                    lambda: hotkey("ctrl", "a"),
                    lambda: press("backspace"),
                    lambda: write("20"),
                ],
                cooldown_time=1
            )

            campo_motorista = MediaLoader.Image("qb9837yhtb83h").path()
            await clickOnTarget(campo_motorista)
            press("tab")
            press("tab")
            sleep(1)
            hotkey("ctrl", "a")
            write(data_emissao)
            sleep(1)
            press("tab")
            write(data_emissao)

            makeThis(
                task_list=[
                    lambda: press("tab"),
                    lambda: write(data_atual),
                    lambda: press("tab"),
                ],
                cooldown_time=1
            )
            hotkey("alt", "e")


            warning_erro_abertura = MediaLoader.Image("0i35juyjb0934q5ujy9bq58").path()
            warning_erro_abertura_found = await isImageOnScreen(warning_erro_abertura,timeout=5)

            if warning_erro_abertura_found:
                press("enter")
                press("f5")
                continue

            warning_erro_pedido = MediaLoader.Image("3ew5uhj3o5k3jh9h234983t8").path()
            erro_pedido_found = await isImageOnScreen(warning_erro_pedido, timeout=10)

            if erro_pedido_found:
                press("enter")
                press("f5")
                continue

            campo_produto = MediaLoader.Image("b07770e261a641748e788d0c09d11a181").path()
            image_produto = await isImageOnScreen(campo_produto, timeout=5)

            if image_produto:
                await clickOnTarget(campo_produto)
            else:
                campo_produto_secundario = MediaLoader.Image("b07770e261a641748e788d0c09d11a181_antiga").path()
                await clickOnTarget(campo_produto_secundario)

            makeThis(
                task_list=[
                     lambda: write("90"),
                     lambda: press("enter"),
                     lambda: press("tab"),
                     lambda: press("tab"),
                     lambda: press("tab"),
                     lambda: press("tab"),
                     lambda: press("tab"),
                     lambda: press("tab"),
                     lambda: press("tab"),
                     lambda: write("2060040005"),
                     lambda: press("tab"),
                 ],
                cooldown_time=1
             )

            cst_pis_cofins = MediaLoader.Image("748y5789v9i34oujht").path()
            cst_found = await isImageOnScreen(cst_pis_cofins,timeout=5)

            if cst_found:
                await clickOnTarget(cst_pis_cofins)
                hotkey("ctrl", "a")
                write("50")

            cst_pis_confins_secundario = MediaLoader.Image("gw8yhe4g7u8").path()
            cst_secundario_found = await isImageOnScreen(cst_pis_confins_secundario,timeout=5)

            if cst_secundario_found:
                await clickOnTarget(cst_pis_confins_secundario)
                hotkey("ctrl", "a")
                write("50")

            campo_diferido = MediaLoader.Image("diferido1").path()
            campo_diferido_found = await isImageOnScreen(campo_diferido)

            if campo_diferido_found:
                await clickOnTarget(campo_diferido)
                press("tab")
                press("tab")
                press("tab")
                write(cte_valor_str)

            sleep(1)
            press("tab")
            hotkey("ctrl", "a")
            write("1,65")

            press("tab")

            press("tab")
            hotkey("ctrl", "a")
            write(cte_valor_str)

            press("tab")
            hotkey("ctrl", "a")
            write("7,6")
            press("tab")

            makeThis(
                task_list=[
                    lambda: hotkey("alt", "v"),
                ],
                cooldown_time=1
            )

            warning_erro_abertura = MediaLoader.Image("0i35juyjb0934q5ujy9bq58").path()
            warning_erro_abertura_found = await isImageOnScreen(warning_erro_abertura,timeout=5)

            if warning_erro_abertura_found:
                press("enter")
                press("f5")
                continue

            makeThis(
                task_list=[
                    lambda: hotkey("alt", "t"),
                ],
                cooldown_time=1
            )

            warning_erro_abertura = MediaLoader.Image("0i35juyjb0934q5ujy9bq58").path()
            warning_erro_abertura_found = await isImageOnScreen(warning_erro_abertura,timeout=5)

            if warning_erro_abertura_found:
                press("enter")
                press("f5")
                continue

            makeThis(
                task_list=[
                    lambda: hotkey("alt", "o")
                ],
                cooldown_time=1
            )

            warning_erro_abertura = MediaLoader.Image("0i35juyjb0934q5ujy9bq58").path()
            warning_erro_abertura_found = await isImageOnScreen(warning_erro_abertura,timeout=5)

            if warning_erro_abertura_found:
                press("enter")
                press("f5")
                continue

            destino = MediaLoader.Image("2g747h8h8g2w").path()
            await clickOnTarget(destino)

            makeThis(
                task_list=[
                    lambda: press("tab"),
                    lambda: press("tab"),
                    lambda: press("tab"),
                    lambda: press("tab"),
                    lambda: press("tab"),
                    lambda: press("tab"),
                    lambda: press("space"),
                    lambda: hotkey("shift", "tab"),
                    lambda: hotkey("shift", "tab"),
                    lambda: press("enter"),
                ],
                cooldown_time=1
            )

            makeThis(
                task_list=[
                    lambda: write("2060040005"),
                    lambda: press("tab"),
                    lambda: write("0501"),
                    lambda: press("tab"),
                    lambda: write(cte_valor_str),
                    lambda: press("tab"),
                    lambda: press("enter"),
                ],
                cooldown_time=2
            )

            warning_item = MediaLoader.Image("87yu4e43t65t2wi9").path()
            warning_item_found = await isImageOnScreen(warning_item,timeout=5)

            if warning_item_found:
                press("enter")
                press("f5")
                continue

            warning_info = MediaLoader.Image("756daewrtf687yehauji")
            warning_info_found = await isImageOnScreen(warning_info,timeout=5)

            if warning_info_found:
                press("enter")
                press("f5")
                continue

            campo_historico = MediaLoader.Image("EtOXvMsLrk").path()
            image_historico = await isImageOnScreen(campo_historico, timeout=5)

            if image_historico:
                await clickOnTarget(campo_historico)
            else:
                campo_historico_secundario = MediaLoader.Image("a9ufe98sgg8sr").path()
                await clickOnTarget(campo_historico_secundario,timeout=5)

            makeThis(
                task_list=[
                    lambda: hotkey("ctrl", "a"),
                    lambda: write("FRETE REFERENTE NOTAS FISCAIS AMBEV."),
                    lambda: hotkey("alt", "s"),
                ],
                cooldown_time=1
            )

            warning_erro_abertura = MediaLoader.Image("0i35juyjb0934q5ujy9bq58").path()
            warning_erro_abertura_found = await isImageOnScreen(warning_erro_abertura,timeout=5)
            if warning_erro_abertura_found:
                press("enter")
                press("f5")
                continue

            excluir_titulo = MediaLoader.Image("3hy7835huo8").path()
            excluir_titulo_found = await isImageOnScreen(excluir_titulo,timeout=5)
            if excluir_titulo_found:
                await clickOnTarget(excluir_titulo)
            else:
                press("f5")
                continue

            excluir_botao = MediaLoader.Image("excluir_button").path()
            await clickOnTarget(excluir_botao)

            makeThis(
                task_list=[
                    lambda: press("tab"),
                    lambda: write(quinta_mais_proxima_f),
                    lambda: press("tab"),
                    lambda: write("00"),
                    lambda: press("tab"),
                    lambda: press("down"),
                    lambda: press("down"),
                    lambda: press("down"),
                    lambda: press("down"),
                    lambda: press("down"),
                    lambda: press("tab"),
                    lambda: write("00"),
                    lambda: press("tab"),
                    lambda: press("tab"),
                    lambda: write(cte_valor_str),
                    lambda: press("tab"),
                    lambda: press("tab"),
                    lambda: press("enter"),
                ],
                cooldown_time=1
            )

            warning_erro_abertura = MediaLoader.Image("0i35juyjb0934q5ujy9bq58").path()
            warning_erro_abertura_found = await isImageOnScreen(warning_erro_abertura,timeout=10)

            if warning_erro_abertura_found:
                press("enter")
                press("f5")
                continue

            salvar_nota = MediaLoader.Image("9f8u23y8239yui8j").path()
            salvar_nota_found = await isImageOnScreen(salvar_nota,timeout=5)

            if salvar_nota_found:
                await clickOnTarget(salvar_nota)

            competencia_error = MediaLoader.Image("2359y8uij892y").path()
            competencia_error_found = await isImageOnScreen(competencia_error, timeout=5)

            if competencia_error_found:
                press("enter")
                clica_nota = MediaLoader.Image("iu2y3gt82w4yehif8u3yh4").path()
                await clickOnTarget(clica_nota)

            hotkey("alt", "s")

            nenhum_titulo = MediaLoader.Image("83294y7325y82u3").path()
            nenhum_titulo_found = await isImageOnScreen(nenhum_titulo,timeout=5)

            if nenhum_titulo_found:
                press("enter")
                press("f5")
                continue

            await setLancamentoCteDate(cte["Id"],quinta_mais_proxima_f)

    async def run(self):
        try:
            rpaGestaoAutomacaoParametros = paramsBuilder(self.rpa_data.rpaGestaoAutomacaoParametros)

            await self.log.create("Iniciando execução do RPA.")

            companies = self.rpa_data.rpaGestaoAutomacaoEmpresas

            for company in companies:
                cte_list = await fetchApprovedCte(company.empresaId)

                if len(cte_list) == 0:
                    continue

                await self.open_promax(company.promaxUrl)
                await self.login(PROMAX_CREDENTIALS["user"], PROMAX_CREDENTIALS["password"])
                await self.company_select(company.promaxUnb)
                await self.close_pop_ups()
                await self.initiate_routine(rpaGestaoAutomacaoParametros["Rotina"])
                await self.log.create("Selecionando filtros do relatorio.")
                await self.filters(cte_list)
                await self.closeBrowser()

            await self.log.create("Finalizou execucao do RPA com sucesso.")

        except Exception as error:
            await self.log.create(f"Finalizou execucao do RPA com falha. \n Erro: {error}")
            raise Exception(error)
