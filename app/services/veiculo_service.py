from app.integrations.plate_recognizer.client import PlateRecognizerClient
from app.infrastructure.database.repositories.veiculo_repository import VeiculoRepository

class VeiculoService:
    def __init__(self, client: PlateRecognizerClient, repository: VeiculoRepository):
        self.client = client
        self.repository = repository

    def processar_veiculo(self, caminho_imagem: str) -> bool:
        """
        Orquestra o fluxo:
        1. Chama a API via client.
        2. Se achar a placa, salva no banco via repository.
        """
        print(f"Analisando imagem: {caminho_imagem}...")
        placa = self.client.ler_placa(caminho_imagem)

        if placa:
            self.repository.salvar(placa)
            return True
        else:
            print("❌ Nenhuma placa foi reconhecida nesta imagem.")
            return False
