import traceback
from time import sleep
from pyautogui import press, write, hotkey

from dtos import RpaGestaoAutomacao
from core import RuntimeEnvironmentConfig

from config import PROMAX_CREDENTIALS
from modules import Promax, fetchPendingCteForPromaxApproval, setCtePromaxApproved, setCteOrderIdToNull
from utils import makeThis, isImageOnScreen
from tools import paramsBuilder, MediaLoader


class RpaProcess(Promax):
    def __init__(self, rpa_data: RpaGestaoAutomacao, runtime_mode: RuntimeEnvironmentConfig):
        self.rpa_data = rpa_data
        self.rpa_data.rpaGestaoAutomacaoParametros = rpa_data.rpaGestaoAutomacaoParametros

        super().__init__(self.rpa_data.id, runtime_mode)

    @staticmethod
    async def filters(cte_list):
        sleep(3)

        for cte in cte_list:
            sleep(1.5)
            makeThis(
                task_list=[
                    lambda: write(cte.get("PromaxPedidoId")),
                    lambda: press("tab"),
                    lambda: press("enter"),
                ],
                cooldown_time=1
            )

            sleep(1)
            pedido_nao_digitado = MediaLoader.Image("8a2bb71bed68483817e705d93f89fc7b").path()
            warning_erro = await isImageOnScreen(pedido_nao_digitado, timeout=5)

            if warning_erro:
                sleep(1)
                press("enter")
                await setCteOrderIdToNull(cte["Id"])
                continue

            else:
                sleep(1)
                hotkey("alt", "a")
                sleep(2)
                pedido_aprovado = MediaLoader.Image("ea7fa8f3f139667a06362e36968bd8a1").path()
                warning_pedido = await isImageOnScreen(pedido_aprovado, timeout=5)

                if warning_pedido:
                    sleep(1)
                    press("enter")
                    await setCtePromaxApproved(cte["Id"])
                    continue

                else:
                    press("f5")
                    await setCtePromaxApproved(cte["Id"])
                    continue

    async def run(self):
        try:
            rpaGestaoAutomacaoParametros = paramsBuilder(self.rpa_data.rpaGestaoAutomacaoParametros)

            await self.log.create("Iniciando execução do RPA.")

            companies = self.rpa_data.rpaGestaoAutomacaoEmpresas

            for company in companies:
                cte_list = await fetchPendingCteForPromaxApproval(company.empresaId)

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