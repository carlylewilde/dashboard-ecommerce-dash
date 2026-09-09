# Dashboard de E-commerce com Dash

Projeto final do módulo **Python: Visualização de Dados Avançada**. A aplicação lê o arquivo `ecommerce_estatistica.csv` com Pandas e apresenta visualizações interativas com Plotly e Dash. Para proteger informações inseridas por terceiros, a versão pública do CSV não contém os textos livres das colunas de avaliações; todas as variáveis necessárias à análise foram preservadas.

## Recursos do dashboard

- filtros por gênero e marca;
- indicadores de produtos, preço médio, nota média e desconto médio;
- histograma de preços;
- dispersão entre preço e nota;
- mapa de calor das correlações;
- barras com as marcas mais frequentes;
- pizza com a composição por gênero;
- densidade dos preços;
- dispersão com linha de regressão entre avaliações e quantidade vendida.

## Estrutura

```text
projeto_dash_ecommerce/
├── app.py
├── ecommerce_estatistica.csv
├── requirements.txt
├── Procfile
├── render.yaml
├── README.md
└── assets/
    └── style.css
```

## Executar localmente

No terminal do PyCharm, dentro da pasta do projeto:

```bash
python -m venv .venv
```

Ative o ambiente no Windows:

```powershell
.venv\Scripts\activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Execute:

```bash
python app.py
```

Abra no navegador: `http://127.0.0.1:8050/`.

## Enviar ao GitHub pelo navegador

1. Entre em <https://github.com/> e faça login.
2. Clique no sinal **+** e em **New repository**.
3. Use o nome `dashboard-ecommerce-dash`.
4. Marque o repositório como **Public**.
5. Não adicione README, `.gitignore` ou licença, pois esses arquivos já existem no projeto.
6. Clique em **Create repository**.
7. Na página vazia, clique em **uploading an existing file**.
8. Arraste todos os arquivos e a pasta `assets` para a área de envio.
9. Em **Commit changes**, escreva `Projeto final Dash` e confirme.
10. Copie o endereço do repositório, parecido com `https://github.com/SEU_USUARIO/dashboard-ecommerce-dash`.

Esse é o link solicitado no campo de entrega da atividade.

## Enviar ao GitHub pelo terminal

Crie primeiro um repositório vazio no GitHub. Depois, execute dentro da pasta do projeto:

```bash
git init
git add .
git commit -m "Projeto final Dash"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/dashboard-ecommerce-dash.git
git push -u origin main
```

Troque `SEU_USUARIO` pelo seu nome de usuário no GitHub.

## Publicar o dashboard no Render

O GitHub hospeda o código, mas não executa permanentemente a aplicação Python. Para gerar um link utilizável pelo cliente:

1. Entre em <https://render.com/> e conecte sua conta do GitHub.
2. Clique em **New +** e escolha **Blueprint**.
3. Selecione o repositório `dashboard-ecommerce-dash`.
4. O Render lerá o arquivo `render.yaml` e preencherá a configuração.
5. Confirme a criação e aguarde o deploy.
6. Ao finalizar, copie a URL parecida com `https://dashboard-ecommerce.onrender.com`.

O repositório é o link acadêmico solicitado. A URL do Render é o link público para o cliente usar o dashboard.

## Como o código funciona

1. `pd.read_csv()` carrega o CSV em um DataFrame.
2. Funções separadas criam cada gráfico Plotly.
3. `app.layout` organiza títulos, filtros, indicadores e gráficos.
4. O callback recebe os filtros como `Input`.
5. Quando uma seleção muda, o callback filtra uma cópia do DataFrame.
6. Os indicadores e os sete gráficos são recalculados e enviados aos `Output`.
7. `server = app.server` permite que o Gunicorn execute a aplicação no servidor.

## Observação de segurança

Não envie senhas, tokens ou arquivos `.env` ao GitHub. O `.gitignore` já impede o envio dos arquivos locais mais comuns.
