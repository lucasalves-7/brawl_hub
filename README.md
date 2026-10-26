# 🎮 Brawl Hub

> **Your Stats. Your Strategy. Your Brawl.**

Plataforma de estatísticas de Brawl Stars construída como uma extensão do universo do jogo. Consulte perfis, explore seus Brawlers, acompanhe seu desempenho e descubra informações sobre sua conta.

> **Projeto independente.** Brawl Hub não é afiliado, patrocinado ou endossado pela Supercell. Brawl Stars é marca da Supercell. As ilustrações e o logotipo do Brawl Hub são originais.

---

## Status atual

| Fase | Entrega | Status |
|------|---------|--------|
| 1 | Fundação visual (paleta, tipografia, componentes) | ✅ Concluída |
| 2 | Home e navegação | ✅ Concluída |
| 3 | Dashboard (agora com dados reais) | ✅ Concluída |
| 4 | Integração com a API da Supercell | ✅ Concluída |
| 5 | Página individual de Brawlers | ⏳ Próxima |
| 6 | Clubes e rankings | ⏳ |
| 7 | Histórico próprio | ⏳ |
| 8 | Preparação para produção | ⏳ |

### O que já consulta a API real

- **`/perfil/<tag>/`** — dashboard do jogador: perfil, estatísticas gerais, distribuição de troféus (gráfico), grade de Brawlers com filtros, desempenho recente e histórico de partidas.
- **`/exemplo/`** — redireciona para o perfil do líder global.

**Fonte dos dados (plano, seção 10):**
- *Grupo A (fornecido)*: troféus, recorde, vitórias por modo, nível, clube, lista de Brawlers.
- *Grupo B (calculado)*: quantidade de Brawlers, distribuição de troféus e **aproveitamento da amostra** — sempre com o tamanho da amostra visível.

> A API da Supercell **não fornece imagens**. Os retratos dos Brawlers são **avatares originais** gerados a partir do nome, mantendo a identidade própria do Brawl Hub.

A chave da API fica em `.env` (não versionado). O cache evita novas consultas a cada interação.

---

## Rodando localmente

```bash
# 1. Crie e ative a virtualenv
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Configure o ambiente
copy .env.example .env        # Windows
# cp .env.example .env        # macOS / Linux

# 4. Suba o servidor
python manage.py runserver
```

Acesse <http://127.0.0.1:8000/>.

---

## Estrutura do projeto

```
brawl-hub/
├── manage.py
├── requirements.txt
├── .env.example
│
├── config/                  # Settings, URLs, WSGI/ASGI
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── apps/
│   └── core/                # Home e navegação (mais apps nas fases seguintes)
│
├── services/                # Cliente da Supercell, cache, estatísticas
│
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── partials/            # Cabeçalho e rodapé
│   └── players/
│
└── static/
    ├── css/                 # tokens, base, components, páginas
    ├── js/                  # Interações
    └── img/                 # Logotipo e artes originais em SVG
```

---

## Identidade visual

- **Fundo:** azul profundo · **Superfícies:** azul médio
- **Destaque:** amarelo vibrante · **Secundário:** azul-celeste · **Especial:** roxo
- **Tipografia:** *Lilita One* (títulos) + *Nunito* (textos e estatísticas)
- **Componentes:** botões encorpados com sombra inferior, cards arredondados, etiquetas coloridas, barras de progresso animadas e efeito de pressão.

A regra de design: **as cores comunicam informação, não apenas decoram.**

---

## Segurança da API

A chave da Supercell fica em variáveis de ambiente (`.env`, fora do controle de versão). Ela nunca aparece no HTML, no JavaScript enviado ao navegador nem no repositório. O `.env` está no `.gitignore`.
