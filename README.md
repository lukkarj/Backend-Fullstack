# My Private CA Manager - API

O objetivo deste projeto é criar um ambiente para o gerenciamento de uma CA (Certificate Authority - Autoridade Certificadora) privada, oferecendo diversas ferramentas para um controle centralizado dos certificados privados.

# Funcionalidades disponíveis (v1.0)

* Geração de novas CAs
* Geração de certificados utilizando a CA desejada
* Listagem das CAs Geradas
* Download do certificado da CA
* Listagem dos certificados emitidos
* Listagem com filtro por CA
* Listagem com busca nos campos Common Name e SANs
* Download do par de chaves dos certificados
* Geração de CSR (Certificate Signing Request - Solicitação de Assinatura de Certificado)
* Decodificação de CSR
* Discovery - Faz a consulta em um servidor para verificar o certificado sendo utilizado

# Documentação

A documentação da API do My Private CA Manager pode ser consultada através do link http://127.0.0.1:5000 após fazer a instalação e rodar o aplicativo

# Instalação

Para utilizar o My Private CA Manager será necessário fazer a instalação das bibliotecas (libs) Python listadas no documento requirements.txt

A instalação pode ser realizada rodando o seguinte comando: `pip install -r requirements.txt`

Uma vez concluída a instalação, basta rodar o comando `python main.py` para rodar o My Private CA Manager localmente.

OBS.: O aplicativo está configurado para rodar em modo DEBUG.

# Primeiros passos

Para começar a usar o My Private CA Manager o primeiro passo será gerar um certificado CA. 

Após gerar o certificado CA, você poderá fazer o download do certificado para a instalação nas aplicações que farão uso do certificado de modo que não receba erro de "não seguro".

Agora você poderá gerar os certificados necessários para seus ambientes internos.

Você também poderá:

* Gerar um par de chaves - Caso precise fazer a solicitação de um certificado em uma CA pública poderá utilizar a ferramenta de geração do My Private CA Manager. Lembre-se de copiar os arquivos de CSR e a chave privativa.
* Decodificar um CSR - Caso tenha um CSR gerado e precisa visualizar os dados.
* Discovery - Verifique qual certificado está instalado em um servidor informando common name e porta.

# Nota do desenvolvedor

Por se tratar de um protótipo, esta versão v1.0 ainda não conta com login de usuário de e proteção dos dados.




