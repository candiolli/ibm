#!/usr/bin/env python3
"""Gera o README.md com o índice do acervo de músicas.

    python3 tools/build.py

Varre a pasta Musicas/, cruza com as tabelas .tsv deste diretório e reescreve o
README.md na raiz. Rode depois de acrescentar, remover ou renomear arquivos.

Fontes de dados (todas neste diretório, separadas por TAB):

  hcc_titles.tsv   número, título e seção temática dos 441 hinos do HCC. Os PDFs
                   são scans sem camada de texto, nomeados só pelo número; estes
                   títulos foram lidos do cabeçalho impresso de cada página, e a
                   seção temática é a do próprio hinário.
  variados.tsv     caminho do arquivo a partir da raiz do repositório, autor e
                   tema. A letra da seção (A/, B/, C/…) sai do próprio caminho.
  cc.tsv           número, título e tema do Cantor Cristão simplificado. Os
                   nomes dos arquivos em disco têm a acentuação corrompida
                   (ANT+ìFONA); aqui fica o título correto, e o link continua
                   apontando para o arquivo real.

Ao editar um .tsv, mantenha o caminho/número idêntico ao do arquivo em disco: o
script aborta se algum caminho não existir, o que impede link quebrado no
README. Um tema seguido de † indica classificação inferida só pelo título.

O repertório principal e as seções 5 a 7 são escritos aqui mesmo, em listas
Python, porque são poucos itens e cada um tem particularidades (vários arquivos
por música, link do YouTube).
"""
import os, re, urllib.parse, unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(AQUI)

def dados(nome):
    """Abre um .tsv ao lado deste script, independente do diretório atual."""
    return open(os.path.join(AQUI, nome), encoding='utf-8')

out = []
W = out.append

# Os nomes em disco vêm em NFD (origem macOS); as strings deste script estão em NFC.
# Mapeia forma NFC -> caminho real, para que os links apontem para os bytes corretos.
REAL = {}
for dirpath, dirnames, filenames in os.walk(ROOT):
    if '.git' in dirpath.split(os.sep):
        continue
    for name in filenames + dirnames:
        rel = os.path.relpath(os.path.join(dirpath, name), ROOT)
        REAL[unicodedata.normalize('NFC', rel)] = rel

def resolve(path):
    key = unicodedata.normalize('NFC', path)
    if key not in REAL:
        raise SystemExit(f'CAMINHO INEXISTENTE: {path}')
    return REAL[key]

def link(label, path):
    if label == 'LOCAL':
        return f'*{path}*'
    if path.startswith('http'):                            # sem cópia local no acervo
        return f'[{label}]({path})'
    return f'[{label}]({urllib.parse.quote(resolve(path))})'

def sortkey(s):
    s = unicodedata.normalize('NFD', s.lower())
    return ''.join(c for c in s if not unicodedata.combining(c))

MINUSCULAS = {'e', 'de', 'do', 'da', 'ao', 'a', 'à', 'com', 'em', 'o', 'os', 'as'}

def titulo_pt(s):
    """Title case respeitando conectivos do português."""
    palavras = s.lower().split()
    saida = []
    for i, p in enumerate(palavras):
        if i > 0 and p in MINUSCULAS:
            saida.append(p)
        else:
            saida.append('-'.join(x[:1].upper() + x[1:] for x in p.split('-')))
    return ' '.join(saida)

def anchor(titulo):
    """Reproduz o slug de cabeçalho do GitHub."""
    s = titulo.lower().replace(' ', '-')
    return '#' + ''.join(c for c in s if c.isalnum() or c in '-_')

# ---------------------------------------------------------------- cabeçalho
W('# 🎵 Acervo de Músicas — Ministério de Louvor')
W('')
W('Repertório, hinários digitalizados, cifras, slides e playbacks usados nos cultos.')
W('Este índice foi montado a partir dos arquivos da pasta [`Musicas/`](Musicas) — todo')
W('item da tabela aponta para o arquivo real no repositório.')
W('')
W('> **Arquivo gerado — não edite à mão.** Para atualizar, ajuste as tabelas em')
W('> [`tools/`](tools) e rode `python3 tools/build.py`, que reescreve este README.')
W('> O script aborta se algum caminho não existir, então link quebrado não passa.')
W('')
W('## Como o acervo está organizado')
W('')
W('```')
W('Musicas/')
W('├── hinos/                 hinários da igreja')
W('│   ├── hcc/               Hinário para o Culto Cristão (JUERP)')
W('│   ├── cantor-cristao/    Cantor Cristão, completo e simplificado')
W('│   └── harpa-crista/')
W('├── canticos-maranata/     hinário Maranata / Vida Nova')
W('│   ├── c-bom/')
W('│   └── ibm-nh/            revisão usada pela igreja')
W('├── contemporaneas/        cifrário A–W + repertório em uso')
W('│   ├── A/ … W/')
W('│   └── repertorio/        músicas ativas: cifra, slide e áudio')
W('├── coral/                 partituras e ensaios por naipe')
W('└── material-de-apoio/     escalas, dicionários de acordes, apostilas')
W('```')
W('')
W('## O que tem aqui')
W('')
W('| Coleção | Itens | Formato | O que é |')
W('|---|---:|---|---|')
W('| [Repertório principal](' + anchor('1. Repertório principal') + ') | 39 | pdf · docx · pptx · mp3 | `contemporaneas/repertorio/` — em uso nos cultos |')
W('| [Contemporâneas — cifrário](' + anchor('2. Contemporâneas — cifrário A–W') + ') | 382 | pdf | `contemporaneas/` — cifrário geral de A a W |')
W('| [Hinário para o Culto Cristão (HCC)](' + anchor('3. Hinário para o Culto Cristão — HCC') + ') | 441 | pdf | `hinos/hcc/` — hinário cifrado da JUERP |')
W('| [Cantor Cristão simplificado](' + anchor('4. Cantor Cristão simplificado') + ') | 71 | pdf | `hinos/cantor-cristao/` — versão simplificada |')
W('| [Cânticos Maranata / Vida Nova](' + anchor('5. Cânticos Maranata / Vida Nova') + ') | ~460 | doc | `canticos-maranata/` — hinário num único documento |')
W('| [Coral 2018 — Voz de Melodia](' + anchor('6. Coral 2018 — Voz de Melodia') + ') | 144 | mp3 · jpg | `coral/` — playbacks e ensaios por naipe |')
W('| [Material de apoio](' + anchor('7. Material de apoio') + ') | 13 | pdf · docx · xlsx | `material-de-apoio/` — escalas, acordes, apostilas |')
W('')
W('**Tema principal:** classificação por assunto do cântico. No HCC o tema vem da própria')
W('seção temática do hinário; nas demais coleções foi atribuído a partir do cântico —')
W('as marcadas com **†** foram inferidas apenas pelo título e valem uma conferência.')
W('')
W('---')
W('')

# ---------------------------------------------- 1. repertório principal
W('## 1. Repertório principal')
W('')
W('As músicas efetivamente usadas nos cultos, reunindo cifra, slide e áudio quando existem.')
W('')
W('| Música | Autor / origem | Tema principal | Arquivos | Ouvir |')
W('|---|---|---|---|---|')

principal = [
 ('46 (Salmo 46)', 'Projeto Sola', 'Refúgio em Deus / Fé',
  [('cifra', 'Musicas/contemporaneas/repertorio/46 - Projeto Sola.pdf'), ('cifra tom F', 'Musicas/contemporaneas/repertorio/46 - Projeto Sola - tom F.pdf'),
   ('slide', 'Musicas/contemporaneas/repertorio/46.pptx')],
  'https://www.youtube.com/watch?v=FKqnFftLNx0'),
 ('A frente dois caminhos', 'Voz de Melodia (CD do coral)', 'Decisão / Salvação †',
  [('LOCAL', 'só áudio de ensaio — não versionado')], None),
 ('A Jesus, o Rei da glória', 'Hinário HCC 199', 'Adoração / Cristo Rei',
  [('slide', 'Musicas/hinos/hcc/HCC 199 - A Jesus, o Rei da glória.pptx'), ('partitura', 'Musicas/hinos/hcc/HCCCIF 199.pdf')], None),
 ('Cantai ao Senhor (um cântico novo)', 'Adhemar de Campos', 'Louvor',
  [('cifra tom G', 'Musicas/contemporaneas/repertorio/Cantai ao Senhor - G.pdf')],
  'https://www.youtube.com/watch?v=r_LwJcWKT30'),
 ('Cantai que o Salvador chegou!', 'Hinário HCC 106', 'Natal',
  [('cifra', 'Musicas/hinos/hcc/Cifra Club - HCC - Hinário Para o Culto Cristão - Cantai Que o Salvador Chegou!.pdf'),
   ('partitura', 'Musicas/hinos/hcc/HCCCIF 106 - Cantai que o Salvador chegou.pdf')], None),
 ('Confiança', 'Projeto Sola', 'Fé / Confiança',
  [('ficha', 'Musicas/contemporaneas/repertorio/Confiança - Projeto Sola.md'),
   ('cifra (Cifra Club)', 'https://www.cifraclub.com.br/projeto-sola/confianca/'),
   ('letra', 'https://www.letras.mus.br/projeto-sola/confianca/')],
  'https://www.youtube.com/watch?v=65f5iCbWf1I'),
 ('Colossenses 1', 'Projeto Sola', 'Supremacia de Cristo',
  [('tom A', 'Musicas/contemporaneas/repertorio/Colossenses 1 - Projeto Sola - A.docx'),
   ('tom G# capo 1', 'Musicas/contemporaneas/repertorio/Colossenses 1 - Projeto Sola - G# - Capo 1.docx'),
   ('slide', 'Musicas/contemporaneas/repertorio/Colossenses 1.pptx')],
  'https://www.youtube.com/watch?v=gk7XWCMwO94'),
 ('Coração Igual ao Teu', 'Diante do Trono', 'Quebrantamento / Consagração',
  [('cifra', 'Musicas/contemporaneas/repertorio/Cifra Club - Diante do Trono - Coração Igual Ao Teu.pdf'),
   ('cifrário', 'Musicas/contemporaneas/C/Coração Igual ao Teu.pdf')],
  'https://www.youtube.com/watch?v=YKOU5lqwxHc'),
 ('Creio (This I Believe – The Creed)', 'Hillsong Worship', 'Credo / Confissão de fé',
  [('letra e cifra', 'Musicas/contemporaneas/repertorio/Creio (This I Believe - The Creed).docx')],
  'https://www.youtube.com/watch?v=FtUNQpu2b7Q'),
 ('Cristo Fundamento', '—', 'Cristo, fundamento da Igreja †',
  [('slide', 'Musicas/contemporaneas/repertorio/Musica_Cristo_Fundamento.pptx'), ('slide azul', 'Musicas/contemporaneas/repertorio/Musica_Cristo_Fundamento_Azul.pptx')], None),
 ('Desde os Confins da Terra', 'Don Harris & Gary Oliver (Lord Most High)', 'Adoração',
  [('slide', 'Musicas/contemporaneas/repertorio/Desde_Os_Confins_da_Terra.pptx')],
  'https://www.youtube.com/watch?v=xgns0WO233M'),
 ('Deus quero louvar-te', '—', 'Louvor †',
  [('letra e cifra', 'Musicas/contemporaneas/repertorio/Deus quero louvar-te.docx')], None),
 ('Deus vê o coração', 'Voz de Melodia nº 40', 'Sinceridade de coração †',
  [('slide', 'Musicas/contemporaneas/repertorio/VM 40 - Deus vê o coração.pptx')], None),
 ('Eterno Deus (Everlasting God)', 'Vineyard / Brenton Brown', 'Fé / Renovo das forças',
  [('slide', 'Musicas/contemporaneas/repertorio/Eterno_Deus - Vineyard.pptx')],
  'https://www.youtube.com/watch?v=D67gv66OmFc'),
 ('Eterno Lar', 'Projeto Sola', 'Vida futura / Céu',
  [('slide', 'Musicas/contemporaneas/repertorio/Eterno lar - Projeto Sola.pptx')],
  'https://www.youtube.com/watch?v=Dkx4BtFkSYM'),
 ('Firmado no Senhor', 'Hinos de Louvor 3, nº 76', 'Fé / Segurança',
  [('partitura', 'Musicas/coral/2018/Voz de melodia/Hinos de louvor 3/76 -  Firmado no Senhor (cd 2.16).jpg')], None),
 ('Firme Fundamento (Jamais)', 'Relevans Music feat. João Rinaldi', 'Fé / Fundamento em Cristo',
  [('cifra', 'Musicas/contemporaneas/repertorio/Relevans Music - Firme Fundamento (Jamais) (part. João Rinaldi).PDF.pdf')],
  'https://www.youtube.com/watch?v=CbcYcw9xQUo'),
 ('Firmeza', 'Hinos de Louvor 3, nº 75', 'Fé / Confiança',
  [('partitura', 'Musicas/coral/2018/Voz de melodia/Hinos de louvor 3/75 - Firmeza (cd 2.15).jpg')], None),
 ('Glorificar', 'Projeto Sola', 'Adoração / Glória de Deus',
  [('cifra', 'Musicas/contemporaneas/repertorio/Cifra Club - Projeto Sola - Glorificar.pdf'),
   ('tom D capo 4', 'Musicas/contemporaneas/repertorio/Cifra Club - Projeto Sola - Glorificar - D (CAPO 4).pdf'),
   ('letra', 'Musicas/contemporaneas/repertorio/Glorificar - Projeto Sola.docx'),
   ('tom F', 'Musicas/contemporaneas/repertorio/Glorificar - Projeto Sola - F.docx')],
  'https://www.youtube.com/watch?v=JCZkKzH5Po0'),
 ('Isaías 53', 'Projeto Sola', 'Cruz / Redenção',
  [('letra e cifra', 'Musicas/contemporaneas/repertorio/Isaías 53 - Projeto Sola.docx')],
  'https://www.youtube.com/watch?v=ADLr9pYHDOw'),
 ('Jesus em Tua Presença', 'Asaph Borba (grav. Diante do Trono)', 'Adoração / Presença de Deus',
  [('tom D', 'Musicas/contemporaneas/repertorio/Jesus em tua presença - D.docx'), ('slide', 'Musicas/contemporaneas/repertorio/Jesus em tua presença.pptx')],
  'https://www.youtube.com/watch?v=1och48cCZEw'),
 ('Não temais / Glória a Deus', 'Voz de Melodia (coral)', 'Fé / Louvor †',
  [('LOCAL', 'só áudio de ensaio — não versionado')], None),
 ('Nossa glória é Jesus conhecer', 'Hinos de Louvor 3, nº 85', 'Conhecimento de Cristo',
  [('partitura', 'Musicas/coral/2018/Voz de melodia/Hinos de louvor 3/85 - Nossa gloria é Jesus conhecer (cd 2.25).jpg'),
   ('p. 2', 'Musicas/coral/2018/Voz de melodia/Hinos de louvor 3/85 - Nossa gloria é Jesus conhecer (cd 2.25) p2.jpg')], None),
 ('Nova Jerusalém', 'Quarteto Gileade', 'Vida futura / Céu',
  [('partitura', 'Musicas/coral/2018/Outras/360536029-Nova-Jerusalem-Quarteto-Gileade.pdf')],
  'https://www.youtube.com/watch?v=_vYiiItqNus'),
 ('O Rei Está Voltando', 'Ozéias de Paula', 'Segunda vinda de Cristo',
  [('cifra', 'Musicas/contemporaneas/repertorio/Cifra Club - Ozéias de Paula - O Rei Esta Voltando.pdf'),
   ('letra editada', 'Musicas/contemporaneas/repertorio/O Rei Esta Voltando - EDITADO.docx'),
   ('áudio', 'Musicas/contemporaneas/repertorio/O Rei Est Voltando - Ozias de Paula.mp3'),
   ('CD 1975', 'Musicas/contemporaneas/repertorio/Luiz de Carvalho - O Rei est Voltando Cd Completo Bompastor 1975.mp3')],
  'https://www.youtube.com/watch?v=DtuwdULLdYI'),
 ('Pai, Tu és Santo', 'Rita Springer / Heloisa Rosa', 'Adoração / Santidade',
  [('letra e cifra', 'Musicas/contemporaneas/repertorio/Pai tu és Santo.docx')],
  'https://www.youtube.com/watch?v=In_Vx8LW2UA'),
 ('Perdão e Graça (Sweet Mercies)', 'Vineyard', 'Graça / Perdão',
  [('slide louvor', 'Musicas/contemporaneas/repertorio/Perdao_e_Graca_Vineyard_Louvor.pptx'),
   ('slide acústico', 'Musicas/contemporaneas/repertorio/Perdao_e_Graca_Vineyard_Acustico_Intimista.pptx')],
  'https://www.youtube.com/watch?v=SCxkiyIT2tA'),
 ('Porque Ele Vive', 'Bill & Gloria Gaither', 'Ressurreição',
  [('Harpa Cristã', 'Musicas/hinos/harpa-crista/Harpa Cristã - Porque Ele Vive.pdf'),
   ('cifrário', 'Musicas/contemporaneas/P/Porque Ele Vive.pdf')],
  'https://www.youtube.com/watch?v=zMCEsSvijJ0'),
 ('Porque vivo está', 'Gaither — trad. HCC 137', 'Ressurreição',
  [('áudio c/ introdução', 'Musicas/hinos/hcc/Porque vivo está - HCC 137 (com introdução).mp3'),
   ('partitura', 'Musicas/hinos/hcc/HCCCIF 137.pdf')], None),
 ('Preciso do Senhor', 'Hinos de Louvor 3, nº 86', 'Dependência de Deus',
  [('partitura', 'Musicas/coral/2018/Voz de melodia/Hinos de louvor 3/86 - Preciso do Senhor (cd 2.26).jpg'),
   ('p. 2', 'Musicas/coral/2018/Voz de melodia/Hinos de louvor 3/86 - Preciso do Senhor (cd 2.26) p2.jpg')], None),
 ('Quão Grande É o Meu Deus', 'Chris Tomlin (vers. Soraya Moraes)', 'Adoração / Grandeza de Deus',
  [('cifra', 'Musicas/contemporaneas/repertorio/Cifra Club - Ministério Águia - Quão Grande É o Meu Deus.pdf'),
   ('cifrário', 'Musicas/contemporaneas/Q/Quão Grande é o Meu Deus.pdf')],
  'https://www.youtube.com/watch?v=IT827htf_S8'),
 ('Quebrantado', 'Ministério Vineyard', 'Quebrantamento',
  [('slide', 'Musicas/contemporaneas/repertorio/Quebrantado.pptx'),
   ('partitura coral', 'Musicas/coral/2018/Outras/215625202-Partitura-Quebrantado.pdf'),
   ('cifrário', 'Musicas/contemporaneas/Q/Quebrantado.pdf')],
  'https://www.youtube.com/watch?v=OE3fYrynTzY'),
 ('Redenção', 'Projeto Sola', 'Cruz / Redenção',
  [('cifra', 'Musicas/contemporaneas/repertorio/Redenção - Projeto Sola.pdf'), ('letra', 'Musicas/contemporaneas/repertorio/Projeto Sola - Redenção.txt')],
  'https://www.youtube.com/watch?v=2FQpBK3Mmp8'),
 ('Salmos 121', 'Salmo 121', 'Socorro e proteção de Deus',
  [('slide', 'Musicas/contemporaneas/repertorio/Salmos 121.pptx')], None),
 ('Só em Cristo (In Christ Alone)', 'Keith Getty & Stuart Townend (vers. Rachel Novaes)', 'Salvação / Suficiência de Cristo',
  [('cifra', 'Musicas/contemporaneas/repertorio/Só Em Cristo - Rachel Novaes.pdf')],
  'https://www.youtube.com/watch?v=H3rFuW6cRAQ'),
 ('Solta o Cabo da Nau', 'Luiz de Carvalho', 'Fé / Confiança',
  [('áudio', 'Musicas/contemporaneas/repertorio/Luiz de Carvalho - Solta o Cabo da Nau.mp3')],
  'https://www.youtube.com/watch?v=xGQ2iPhLv9U'),
 ('Teu Povo', 'IPALPHA Música', 'Igreja / Reforma',
  [('letra e cifra', 'Musicas/contemporaneas/repertorio/Teu Povo - Ipalpha.docx'), ('slide', 'Musicas/contemporaneas/repertorio/Teu povo - Ipalpha.pptx')],
  'https://www.youtube.com/watch?v=4GC0uxYbJ-M'),
 ('Vasos Quebrados (Sublime Graça)', 'Hillsong em Português', 'Graça / Cura',
  [('cifra', 'Musicas/contemporaneas/repertorio/Cifra Club - Hillsong Em Português - Vasos Quebrados ( Sublime Graça ).pdf')],
  'https://www.youtube.com/watch?v=IZ1qrlxh1OQ'),
 ('Vim para Adorar-te (Here I Am to Worship)', 'Tim Hughes', 'Adoração',
  [('letra', 'Musicas/contemporaneas/repertorio/Adoração e Adoradores - Vim Para Adorar-Te.txt'),
   ('slide', 'Musicas/contemporaneas/repertorio/Vim para adorar-te.pptx'),
   ('cifrário', 'Musicas/contemporaneas/V/Vim para Adorar-te.pdf')],
  'https://www.youtube.com/watch?v=76mkc0pKD6A'),
 ('Vos Prostrai', 'Ron Hamilton & Cheryl Reid (Hinos de Louvor)', 'Adoração',
  [('partitura', 'Musicas/contemporaneas/repertorio/Vos Prostrai - Hinos de Louvor 3.pdf'),
   ('letra e cifra', 'Musicas/contemporaneas/repertorio/Vos Prostrai - Voz de Melodia.docx')],
  'https://www.youtube.com/watch?v=c3fFzbPfrDg'),
]
principal.sort(key=lambda r: sortkey(r[0]))
for nome, autor, tema, arqs, yt in principal:
    files = ' · '.join(link(l, p) for l, p in arqs)
    ouvir = f'[▶︎]({yt})' if yt else '—'
    W(f'| **{nome}** | {autor or "—"} | {tema} | {files} | {ouvir} |')
W('')
W('---')
W('')

# ---------------------------------------------- 2. cânticos variados
W('## 2. Contemporâneas — cifrário A–W')
W('')
W('Cifrário geral em [`Musicas/contemporaneas/`](Musicas/contemporaneas), uma pasta por letra inicial.')
W('')
rows = {}
for line in dados('variados.tsv'):
    caminho, autor, tema = (line.rstrip('\n').split('\t') + ['', ''])[:3]
    letra = os.path.basename(os.path.dirname(caminho))     # a pasta A/, B/, C/…
    titulo = re.sub(r'\.pdf$', '', os.path.basename(caminho)).strip()
    rows.setdefault(letra, []).append((titulo, autor, tema, caminho))
for letra in sorted(rows, key=sortkey):
    itens = sorted(rows[letra], key=lambda r: sortkey(r[0]))
    W(f'<details>')
    W(f'<summary><strong>{letra}</strong> — {len(itens)} cânticos</summary>')
    W('')
    W('| Música | Autor / origem | Tema principal | Arquivo |')
    W('|---|---|---|---|')
    for titulo, autor, tema, path in itens:
        W(f'| {titulo} | {autor or "—"} | {tema} | {link("cifra", path)} |')
    W('')
    W('</details>')
    W('')
W('---')
W('')

# ---------------------------------------------- 3. HCC
W('## 3. Hinário para o Culto Cristão — HCC')
W('')
W('441 hinos cifrados digitalizados em [`Musicas/hinos/hcc/`](Musicas/hinos/hcc) (JUERP). O tema de cada hino')
W('é a **seção temática do próprio hinário**, lida na página do hino. O hinário completo')
W('também está em ' + link('hcc-cifrado.pdf', 'Musicas/hinos/hcc/hcc-cifrado.pdf') + ' (503 páginas).')
W('')
secoes = {}
ordem = []
for line in dados('hcc_titles.tsv'):
    num, titulo, secao = line.rstrip('\n').split('\t')
    secao = secao.strip()
    if secao not in secoes:
        secoes[secao] = []
        ordem.append(secao)
    secoes[secao].append((num, titulo))
especiais = {'091': 'Musicas/hinos/hcc/HCCCIF 091 - Noite feliz.pdf',
             '106': 'Musicas/hinos/hcc/HCCCIF 106 - Cantai que o Salvador chegou.pdf'}
for secao in ordem:
    itens = secoes[secao]
    titulo_sec = titulo_pt(secao).replace(', ', ' · ')
    W('<details>')
    W(f'<summary><strong>{titulo_sec}</strong> — {len(itens)} hinos</summary>')
    W('')
    W('| Nº | Hino | Partitura cifrada |')
    W('|---:|---|---|')
    for num, titulo in itens:
        path = especiais.get(num, f'Musicas/hinos/hcc/HCCCIF {num}.pdf')
        W(f'| {int(num)} | {titulo} | {link("PDF", path)} |')
    W('')
    W('</details>')
    W('')
W('---')
W('')

# ---------------------------------------------- 4. Cantor Cristão
W('## 4. Cantor Cristão simplificado')
W('')
W('Hinos do Cantor Cristão em arranjo simplificado, em [`Musicas/hinos/cantor-cristao/cc-simplificado/`](Musicas/hinos/cantor-cristao/cc-simplificado).')
W('O hinário cifrado completo está em ' + link('CantorCristoCifradoEMEEditora-1.pdf', 'Musicas/hinos/cantor-cristao/CantorCristoCifradoEMEEditora-1.pdf') + '.')
W('')
W('| Nº | Hino | Tema principal | Arquivos |')
W('|---:|---|---|---|')
ccdir = 'Musicas/hinos/cantor-cristao/cc-simplificado'
reais = os.listdir(os.path.join(ROOT, ccdir))
def acha(num, ext):
    for f in reais:
        if f.endswith(ext) and re.match(rf'^{re.escape(num)}\b', f):
            return f'{ccdir}/{f}'
    return None
for line in dados('cc.tsv'):
    num, titulo, tema = line.rstrip('\n').split('\t')
    partes = []
    p = acha(num, '.pdf')
    if p: partes.append(link('PDF', p))
    d = acha(num, '.docx')
    if d: partes.append(link('DOCX', d))
    if num == '289':
        partes.append(link('slide', f'{ccdir}/cc 289 - Ao pés da cruz_.pptx'))
    W(f'| {num.replace("_", " / ")} | {titulo} | {tema} | {" · ".join(partes)} |')
W('')
W('---')
W('')

# ---------------------------------------------- 5. Maranata
W('## 5. Cânticos Maranata / Vida Nova')
W('')
W('Hinário congregacional inteiro em documentos únicos do Word — não há um arquivo por cântico,')
W('por isso o índice fica dentro dos próprios documentos.')
W('')
W('| Documento | O que é |')
W('|---|---|')
W('| ' + link('Cânticos Maranata C Bom Cifrado.doc', 'Musicas/canticos-maranata/c-bom/Cânticos Maranata C Bom Cifrado.doc') + ' | Hinário completo, cifrado |')
W('| ' + link('Cânticos Maranata C Bom Word 97 Espelho.doc', 'Musicas/canticos-maranata/c-bom/Cânticos Maranata C Bom Word 97 Espelho.doc') + ' | Versão para impressão em espelho |')
W('| ' + link('Índice Numérico Vida Nova.doc', 'Musicas/canticos-maranata/c-bom/Índice Numérico Vida Nova.doc') + ' | Índice nº → título (≈460 cânticos) |')
W('| ' + link('Índice Primeira linha Vida Nova.doc', 'Musicas/canticos-maranata/c-bom/Índice Primeira linha Vida Nova.doc') + ' | Índice pela primeira linha da letra |')
W('| ' + link('Índice Numérico Vida Nova Cifrado.doc', 'Musicas/canticos-maranata/c-bom/Índice Numérico Vida Nova Cifrado.doc') + ' | Índice numérico da versão cifrada |')
W('| ' + link('Índice Primeira linha Vida Nova Cifrado.doc', 'Musicas/canticos-maranata/c-bom/Índice Primeira linha Vida Nova Cifrado.doc') + ' | Índice por primeira linha, versão cifrada |')
W('| ' + link('novos.txt', 'Musicas/canticos-maranata/ibm-nh/novos.txt') + ' | Cânticos novos incluídos no hinário |')
W('')
W('A pasta [`canticos-maranata/ibm-nh/`](Musicas/canticos-maranata/ibm-nh) traz a mesma')
W('coletânea na revisão usada pela igreja, mais as capas.')
W('')
W('---')
W('')

# ---------------------------------------------- 6. Coral
W('## 6. Coral 2018 — Voz de Melodia')
W('')
W('> **Os áudios não estão no repositório.** As 140 faixas de ensaio (~693 MB) ficam só na')
W('> máquina local — veja o [`.gitignore`](.gitignore). O inventário abaixo registra o que existe;')
W('> os mp3 são faixas numeradas (`01 Track 1.mp3`…), sem o título da música no arquivo.')
W('')
W('| Conjunto | Faixas | Pasta local |')
W('|---|---:|---|')
for nome, sub in [('Demo do coral', 'demo coral'), ('Soprano', 'soprano'), ('Contralto', 'contralto'),
                  ('Tenor', 'tenor'), ('Baixo', 'baixo'), ('Playback', 'playback')]:
    d = f'Musicas/coral/2018/Voz de melodia/A frente dois caminhos/{sub}'
    n = len([f for f in os.listdir(os.path.join(ROOT, d)) if f.lower().endswith('.mp3')])
    W(f'| {nome} — *A frente dois caminhos* | {n} | `{sub}/` |')
for faixa in ['1-30', '61-90', '91-120']:
    d = f'Musicas/coral/2018/Voz de melodia/Hinos de louvor 3/Hinos de louvor 3/{faixa}'
    n = len([f for f in os.listdir(os.path.join(ROOT, d)) if f.lower().endswith('.mp3')])
    W(f'| Hinos de Louvor 3 — hinos {faixa} | {n} | `Hinos de louvor 3/{faixa}/` |')
W('')
W('As partituras avulsas do coral (*Firmeza*, *Firmado no Senhor*, *Nossa glória é Jesus conhecer*,')
W('*Preciso do Senhor*, *Quebrantado*, *Nova Jerusalém*) estão indexadas no')
W('[repertório principal](' + anchor('1. Repertório principal') + ').')
W('')
W('---')
W('')

# ---------------------------------------------- 7. Apoio
W('## 7. Material de apoio')
W('')
W('Arquivos da pasta que **não são músicas**.')
W('')
W('| Arquivo | O que é |')
W('|---|---|')
apoio = [
 ('Musicas/material-de-apoio/Caderno de Cifras PV-Sul 09.docx', 'Caderno de cifras do PV-Sul 2009'),
 ('Musicas/material-de-apoio/Dicionário de Acordes de Violão 1.pdf', 'Dicionário de acordes de violão (1)'),
 ('Musicas/material-de-apoio/Dicionário de Acordes de Violão 2.pdf', 'Dicionário de acordes de violão (2)'),
 ('Musicas/material-de-apoio/DADGAD-Acordes.pdf', 'Acordes em afinação DADGAD'),
 ('Musicas/material-de-apoio/DADGAD-Acordes-2.pdf', 'Acordes em afinação DADGAD (2)'),
 ('Musicas/material-de-apoio/Adoração através da Música_02.pdf', 'Apostila “Adoração através da Música” — parte 2'),
 ('Musicas/material-de-apoio/Adoração através da Música_04.pdf', 'Apostila “Adoração através da Música” — parte 4'),
 ('Musicas/material-de-apoio/ESCALA LIDERANÇA MUSICA 2018.docx', 'Escala de liderança de música — 2018'),
 ('Musicas/material-de-apoio/escala-de-liderança-de-musica-2017.docx', 'Escala de liderança de música — 2017'),
 ('Musicas/material-de-apoio/escala-de-liderança-de-musica-2017(1).docx', 'Escala de liderança de música — 2017 (cópia)'),
 ('Musicas/material-de-apoio/Dirigentes Culto 2017.xlsx', 'Escala de dirigentes de culto — 2017'),
 ('Musicas/material-de-apoio/musicas-louvor-domingo.xlsx', 'Registro de hinos cantados por culto (dirigente, data, hinário, número)'),
 ('Musicas/material-de-apoio/Multiplication-Flashcards-1.2.pdf', 'Não pertence ao acervo musical (flashcards de multiplicação)'),
]
for p, d in apoio:
    W(f'| {link(os.path.basename(p), p)} | {d} |')
W('')

texto = '\n'.join(out) + '\n'

quebrados = []
for rotulo, alvo in re.findall(r'\[([^\]]*)\]\(([^)]+)\)', texto):
    if alvo.startswith(('http', '#')):
        continue
    if not os.path.exists(os.path.join(ROOT, urllib.parse.unquote(alvo))):
        quebrados.append(f'{rotulo} -> {alvo}')
if quebrados:
    raise SystemExit('LINK QUEBRADO no README:\n  ' + '\n  '.join(quebrados))

open(os.path.join(ROOT, 'README.md'), 'w', encoding='utf-8').write(texto)
print('README.md gerado —', len(out), 'linhas')
