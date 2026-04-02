from time import sleep
import traceback
from os import path, mkdir, remove, makedirs
from pyautogui import write, press, hotkey

from dtos import RpaGestaoAutomacao
from core import RuntimeEnvironmentConfig

from config import PROMAX_CREDENTIALS
from modules import Promax
from utils import makeThis, isImageOnScreen, clickOnTarget
from tools import paramsBuilder, MediaLoader, File
from modules import Promax, fetchPendingDocuments, setEnviadoPromax, fetchPendingAllDocuments


class RpaProcess(Promax):
    def __init__(self, rpa_data: RpaGestaoAutomacao, runtime_mode: RuntimeEnvironmentConfig):
        self.rpa_data = rpa_data
        self.rpa_data.rpaGestaoAutomacaoParametros = rpa_data.rpaGestaoAutomacaoParametros

        super().__init__(self.rpa_data.id, runtime_mode)

    @staticmethod
    async def filters(documents):
        base_dir = path.expanduser("~")
        temp_folder = path.join(base_dir, "Rpa Gestao", "root", "temp").split("/")[-1]

        if not path.exists(temp_folder):
            makedirs(temp_folder)

        for document in documents:
            for image in document.get("ImagePath"):
                image_name = image.get("Filename").split("/")[-1]
                server_path = (
                    r"\\192.168.0.12\inetpub\wwwroot\gestao\App_Data\upload"
                )
                full_image_path = path.join(server_path, image.get("Filename"))

                if not path.exists(full_image_path):
                    print(f"Arquivo não encontrado: {full_image_path}")
                    continue

                temp_image_path = path.join(temp_folder, image_name)

                document_photo = File(full_image_path)
                document_photo.image_compressor(temp_image_path)

                try:
                    sleep(2)
                    
                    makeThis(
                        task_list=[
                            lambda: write(str(document.get("ClienteId"))),
                            lambda: press("Tab"),
                        ],
                        cooldown_time=1.5
                    )

                    sleep(1)

                    procurar_button = MediaLoader.Image("7694f4a66316e53c8cdd9d9954bd611d").path()
                    await isImageOnScreen(procurar_button, timeout=15)
                    await clickOnTarget(procurar_button)
                    sleep(2.5)
                    hotkey("ctrl", "a")
                    press("backspace")

                    makeThis(
                        task_list=[
                            lambda: write(temp_image_path),
                            lambda: press("Enter"),
                            lambda: press("Tab"),
                            lambda: write(str(document.get("TipoDocumento"))),
                            lambda: hotkey("alt", "c"),
                            lambda: press("enter"),
                            lambda: press("f5")
                        ],
                        cooldown_time=1.5
                    )

                    # Marca o documento como enviado após a última imagem ser processada
                    if image == document.get("ImagePath")[-1]:
                        await setEnviadoPromax(document.get("Id"))

                except Exception as e:
                    print(f"Erro durante o processamento da imagem: {e}")
                    traceback.print_exc()

                finally:
                    if path.exists(temp_image_path):
                        remove(temp_image_path)
                        print(f"Imagem removida: {temp_image_path}")


    async def run(self):
        try:
            rpaGestaoAutomacaoParametros = paramsBuilder(self.rpa_data.rpaGestaoAutomacaoParametros)

            await self.log.create("Iniciando execução do RPA.")

            companies = self.rpa_data.rpaGestaoAutomacaoEmpresas

            while True:
                for company in companies:
                    documents = await fetchPendingDocuments(company.empresaId)

                    if len(documents) == 0:
                         continue

                    await self.open_promax(company.promaxUrl)
                    await self.login(PROMAX_CREDENTIALS["user"], PROMAX_CREDENTIALS["password"])
                    await self.company_select(company.promaxUnb)
                    await self.close_pop_ups()
                    await self.initiate_routine(rpaGestaoAutomacaoParametros["Rotina"])
                    await self.log.create("Selecionando filtros do relatório.")
                    await self.filters(documents)
                    await self.closeBrowser()

                response = await fetchPendingAllDocuments()

                if response == 0:
                    sleep(600)  # Espera 10 minutos e roda novamente.
                    continue

            await self.log.create("Finalizou execução do RPA com sucesso.")

        except Exception as error:
            traceback.print_exc()
            await self.log.create(f"Finalizou execução do RPA com falha. \n Erro: {error}")
