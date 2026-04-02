from datetime import datetime, timedelta

import pyperclip
from pyautogui import press, write, hotkey
from time import sleep

from dtos import RpaGestaoAutomacao
from core import RuntimeEnvironmentConfig

from tools import paramsBuilder
from modules import Promax, fetchEmployees
from utils import makeThis
import json


class RpaProcess(Promax):
    def __init__(self, rpa_data: RpaGestaoAutomacao, runtime_mode: RuntimeEnvironmentConfig):
        self.rpa_data = rpa_data
        self.rpa_data.rpaGestaoAutomacaoParametros = rpa_data.rpaGestaoAutomacaoParametros

        super().__init__(self.rpa_data.id, runtime_mode)

    @staticmethod
    async def filters(employees: list):
        sleep(3)

        for employee in employees:
            valor_rescisao = employee.get("RescisaoPagamentoVlr")

            makeThis(
                task_list=[
                    lambda: write("8067"),
                    lambda: press("tab"),
                    lambda: write("1"),
                    lambda: press("tab"),
                    lambda: write("8068"),
                    lambda: press("tab"),
                ],
                cooldown_time=1
            )

            data_emissao = (datetime.now() - timedelta(days=9)).strftime("%d/%m/%Y")
            write(data_emissao)
            press("tab")
            press("tab")

            data_pagamento = (datetime.now() + timedelta(days=4)).strftime("%d/%m/%Y")
            write(data_pagamento)

            makeThis(
                task_list=[
                    lambda: press("tab"),
                    lambda: write("001"),
                    lambda: press("tab"),
                    lambda: write("001"),
                    lambda: press(['tab']*2),
                    lambda: write("017"),
                    lambda: press("tab"),
                ],
                cooldown_time=1
            )

            makeThis(
                task_list=[
                    lambda: write(f"{valor_rescisao:.2f}"),
                    lambda: press(['tab'] * 3),
                    lambda: write("2010060001"),
                    lambda: press('tab'),
                    lambda: write("501"),
                    lambda: press('tab'),
                    lambda: write("PAGAMENTO RESCISAO"),
                    lambda: press('tab'),
                    lambda: press('space'),
                ],
                cooldown_time=3.5
            )

            for _ in range(6):
                press("tab")
            press("enter")

            for _ in range(7):
                press("tab")
            press("space")

    async def run(self):
        try:
            rpaGestaoAutomacaoParametros = paramsBuilder(self.rpa_data.rpaGestaoAutomacaoParametros)

            await self.log.create("Iniciando execução do RPA.")

            companies = self.rpa_data.rpaGestaoAutomacaoEmpresas

            for company in companies:
                employees_response = await fetchEmployees(company.empresaId)

                company.extra_fields["employees"] = employees_response.Entities

                await self.generate_standard_report(rpaGestaoAutomacaoParametros, company, self.filters)

            await self.log.create("Finalizou execução do RPA com sucesso.")

        except Exception as error:
            await self.log.create(f"Finalizou execução do RPA com falha. \n Erro: {error}")
            raise Exception(error)
