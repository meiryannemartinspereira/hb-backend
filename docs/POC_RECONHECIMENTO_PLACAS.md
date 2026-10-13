# POC - Reconhecimento de placas veiculares (HB-2)

## Introdução e contexto

A tarefa **HB-2 - "POC - Reconhecimento placa veicular"** tem como objectivo explorar um sistema simples para detectar e reconhecer matrículas em imagens de veículos. Esta prova de conceito valida o percurso essencial: receber uma imagem, obter uma matrícula através de um serviço de reconhecimento externo e registar o resultado localmente.

A implementação existente separa esse percurso em componentes pequenos, com responsabilidades distintas. A POC não substitui um sistema de produção: depende da disponibilidade e das credenciais da API Plate Recognizer, e não inclui, actualmente, uma interface gráfica ou um endpoint HTTP dedicado ao reconhecimento.

## Arquitectura em camadas

As implementações estão dentro do pacote `app/`. O serviço coordena a integração e a persistência através de dependências recebidas no construtor, em vez de criar esses componentes por conta própria.

### Integração: Plate Recognizer

Ficheiro: `app/integrations/plate_recognizer/client.py`

`PlateRecognizerClient` encapsula a comunicação com a API Plate Recognizer:

- envia a imagem local com `requests.post` para o endpoint `/v1/plate-reader/`;
- usa `files` para enviar o ficheiro como `multipart/form-data` e inclui `regions='br'` nos dados do pedido;
- autentica o pedido com o cabeçalho `Authorization: Token ...`;
- interpreta a resposta JSON e devolve, em maiúsculas, a matrícula do primeiro resultado.

Se não houver resultados, a resposta não for bem-sucedida (o código aceite é `200` ou `201`) ou ocorrer uma excepção, o método devolve `None`. As excepções são impressas na saída do processo. A imagem é enviada para um serviço externo; confirme que o seu envio é permitido antes de utilizar imagens reais.

### Infra-estrutura: persistência SQLite

Ficheiro: `app/infrastructure/database/repositories/veiculo_repository.py`

`VeiculoRepository` é responsável pelo armazenamento local:

- usa SQLite e, por omissão, cria/abre `estacionamento.db` no directório de trabalho actual;
- ao ser instanciado, cria a tabela `registros_placas` caso ainda não exista, com `id`, `placa` e `data_hora`;
- o método `salvar` regista a matrícula e a data/hora obtida com `datetime.now()`, formatada como `AAAA-MM-DD HH:MM:SS`.

A criação da tabela é automática; cada reconhecimento bem-sucedido acrescenta um registo. O valor temporal é uma hora local sem informação de fuso horário.

### Serviço: orquestração do fluxo

Ficheiro: `app/services/veiculo_service.py`

`VeiculoService` recebe um `PlateRecognizerClient` e um `VeiculoRepository` através do construtor. O método `processar_veiculo(caminho_imagem)`:

1. pede ao cliente que analise a imagem;
2. se for devolvida uma matrícula, pede ao repositório que a grave e devolve `True`;
3. se não houver matrícula reconhecida, não grava qualquer registo e devolve `False`.

Esta injecção de dependências mantém a orquestração separada dos detalhes HTTP e SQLite, permitindo substituir ou simular os componentes em testes.

## Instruções de utilização

### Pré-requisitos

- Python 3.10 ou superior;
- um token válido da API Plate Recognizer;
- uma imagem acessível pelo processo;
- acesso à Internet para a chamada à API.

O cliente importa `requests`, mas esta dependência não está declarada directamente no `requirements.txt` actual. Instale-a no ambiente virtual, caso ainda não esteja disponível:

```console
python -m pip install requests
```

Não coloque o token no código nem o registe em controlo de versões. Defina-o como variável de ambiente antes de executar o exemplo.

Em PowerShell:

```powershell
$env:PLATE_RECOGNIZER_TOKEN = "o-seu-token"
```

### Executar o fluxo

Na raiz do repositório, execute um pequeno script que construa as dependências e invoque o serviço. Por exemplo, guarde o código seguinte num ficheiro temporário ou num script local não versionado, substitua o caminho da imagem e execute-o a partir da raiz do projecto:

```python
import os

from app.integrations.plate_recognizer.client import PlateRecognizerClient
from app.infrastructure.database.repositories.veiculo_repository import VeiculoRepository
from app.services.veiculo_service import VeiculoService

client = PlateRecognizerClient(os.environ["PLATE_RECOGNIZER_TOKEN"])
repository = VeiculoRepository()  # usa estacionamento.db no directório actual
service = VeiculoService(client, repository)

reconhecida = service.processar_veiculo(r"C:\imagens\veiculo.jpg")
print("Matrícula registada." if reconhecida else "Não foi reconhecida qualquer matrícula.")
```

O repositório cria `estacionamento.db` e a tabela `registros_placas` durante a sua inicialização, se necessário. Quando o serviço reconhece uma matrícula, grava-a com a data e hora actuais; caso contrário, não cria um registo. O ficheiro da base de dados fica no directório de trabalho a partir do qual o processo foi iniciado.

### Limites da execução actual

Os componentes da POC existem no código, mas o fluxo de reconhecimento não está ligado a uma interface de utilizador nem ao ponto de entrada/API da aplicação. O exemplo acima invoca o serviço directamente. Também não há configuração de timeout HTTP no cliente; para utilização além da POC, devem ser avaliados timeouts, tratamento explícito de erros, configuração segura do token, gestão do ciclo de vida das ligações SQLite e uma interface adequada ao utilizador.
