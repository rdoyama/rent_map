# Mapa de imóveis para aluguel do Zap Imóveis

Coleta dados de imóveis disponíveis para aluguel diretamente da API de dados do ZAP Imóveis e compila os resultados em formato JSON, CSV e em um arquivo KMZ, que pode ser aberto por programas de mapa (Google Earth, Google Maps) e contém a localização exata dos imóveis, a descrição, valores (Aluguel, Condomínio e IPTU) e o contato dos anunciantes.

## Instalação
Clone o repositório e, em um ambiente virtual, instale as dependências
```console
$ pip install -r requirements.txt
```

## Execução
```console
$ python3 app.py
```
### Arquivos gerados
* `data/yyyymmdd-HHMMSS/listings.csv` (Opcional)
* `data/yyyymmdd-HHMMSS/listings.json` (Opcional)
* `rentMap.kmz`

## Configuração
1. Abra o site do [Zap Imóveis](https://https://www.zapimoveis.com.br) e faça uma busca pelos imóveis para alugar com os filtros que deseja
2. Abra as ferramentas de desenvolvedor (F12 no Firefox) e vá para a aba Network
3. No canto inferior esquerdo do site, clique no botão "Buscar Imóveis"
![Buscar Imóveis](/resources/buscar.png "Filtro")
4. Aparecerá uma única chamada HTTP cujo resultado é um JSON. A URL desta chamada contém os filtros inseridos e o conteúdo que será retornado. Clique com o botão direito na chamada e copie a URL do link
![GET dos dados](/resources/get_json.png "URL")
5. No arquivo config.ini, substitua o conteúdo da variável `data_api` e ajuste os filtros


### Parâmetros de Configuração
#### `[ZAP]`
* `base_url` (str): URL base do Zap Imóveis
* `data_api` (str): URL da API que fornece os dados para o site (passo 4 da Configuração)
* `save_json_listings` (bool): Salvar os dados de todos os imóveis em formato JSON em `data/yyyymmdd-HHMMSS/listings.json`
* `save_csv_listings` (bool): Salvar os dados de todos os imóveis em formato CSV em `data/yyyymmdd-HHMMSS/listings.csv`
#### `[FILTERS]`
* `rent_price_min` (`int`): Valor mínimo do aluguel
* `rent_price_max` (`int`): Valor máximo do aluguel
* `neighborhood` (`str`): Nome do bairro como aparece no site. Ex: `Butantã`, `Boa Viagem`, etc.
* `pets_allowed` (`str`): Se `True`, filtra apenas os imóveis que aceitam pets e que possuem a flag `PETS_ALLOWED` na descrição. Caso contrário, busca todos os resultados
* `min_unit_floor` (`int`): Se fornecido, busca apenas os imóveis cujo andar foi informado na descrição e é maior que `min_unit_floor`
#### `[UTILITY]`
* `add_markets` (`str`): Se `True`, mostra no mapa todos os mercados descritos no arquivo `resources/markets.json`

## Como abrir o arquivo KMZ
### Google Earth
No menu `Arquivo -> Abrir` escolha o arquivo KMZ
![Resultados Google Earth](/resources/earth.png "Earth")

### Google Maps
1. Acesse a ferramenta [MyMaps](https://www.google.com/maps/d/u/0/) do Google
2. Clique em `Criar Novo Mapa`
3. Na nova página, clique em `Importar` e selecione o arquivo KMZ
![Resultados Google Maps](/resources/maps.png "Maps")