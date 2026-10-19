import requests

class PlateRecognizerClient:
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.api_url = "https://api.platerecognizer.com/v1/plate-reader/"

    def ler_placa(self, caminho_imagem: str) -> str | None:
        """Envia a imagem para a API via POST e retorna a placa."""
        try:
            with open(caminho_imagem, 'rb') as fp:
                resposta = requests.post(
                    self.api_url,
                    data=dict(regions='br'), 
                    files=dict(upload=fp),
                    headers={'Authorization': f'Token {self.api_token}'}
                )
            
            if resposta.status_code in (200, 201):
                dados = resposta.json()
                if dados.get('results'):
                    return dados['results'][0]['plate'].upper()
            
            return None
        except Exception as e:
            print(f"Erro na integração com a API: {e}")
            return None
