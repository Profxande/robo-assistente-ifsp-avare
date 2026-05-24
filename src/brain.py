import argparse
import json
import re
import unicodedata
from pathlib import Path


BASE_PATH = Path(__file__).resolve().parents[1] / "data" / "base_conhecimento.json"
SETORES_PATH = Path(__file__).resolve().parents[1] / "data" / "setores.json"
SITE_PAGES_PATH = Path(__file__).resolve().parents[1] / "data" / "site_pages.json"
FALLBACK_ID = "nao-encontrado"


def normalize(text):
    text = unicodedata.normalize("NFKD", text.lower())
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = re.sub(r"[^a-z0-9\s-]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def tokens(text):
    return set(normalize(text).split())


def load_knowledge(path=BASE_PATH):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_sectors(path=SETORES_PATH):
    if not path.exists():
        return []

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_site_pages(path=SITE_PAGES_PATH):
    if not path.exists():
        return []

    with open(path, "r", encoding="utf-8") as file:
        payload = json.load(file)
    return payload.get("pages", [])


def site_page_entries(pages=None):
    pages = pages if pages is not None else load_site_pages()
    entries = []

    for index, page in enumerate(pages):
        title = page.get("title") or page.get("url")
        headings = page.get("headings") or []
        summary = page.get("summary") or ""
        emails = page.get("emails") or []
        phones = page.get("phones") or []
        details = []

        if summary:
            details.append(summary)
        if emails:
            details.append("E-mails encontrados: " + ", ".join(emails))
        if phones:
            details.append("Telefones encontrados: " + ", ".join(phones))

        answer_text = f"Encontrei uma página oficial relacionada: {title}. Acesse: {page.get('url')}."
        if details:
            answer_text += " " + " ".join(details)

        entries.append(
            {
                "id": f"site-page-{index + 1}",
                "tema": "indice do site",
                "perguntas_exemplo": [title, *headings[:6]],
                "resposta": answer_text[:1800],
                "palavras_chave": [
                    title,
                    *headings[:8],
                    *emails,
                    page.get("url", ""),
                ],
                "setor_responsavel": "Site oficial do IFSP Avaré",
                "fonte": page.get("url"),
                "status": "publicado",
            }
        )

    return entries


def sector_entries(sectors=None):
    sectors = sectors if sectors is not None else load_sectors()
    entries = []

    for sector in sectors:
        label = f"{sector['sigla']} - {sector['setor']}"
        extra_keywords = []
        if sector["sigla"] == "CRA":
            extra_keywords = [
                "secretaria",
                "registros academicos",
                "registro academico",
                "documentos academicos",
                "matricula",
                "historico",
                "declaracao",
            ]
        elif sector["sigla"] == "CBI":
            extra_keywords = ["biblioteca", "livro", "emprestimo"]
        elif sector["sigla"] == "CTI":
            extra_keywords = ["tecnologia", "informatica", "informacao", "wifi", "internet"]
        elif sector["sigla"] == "SSP":
            extra_keywords = ["assistencia estudantil", "sociopedagogica", "auxilio", "permanencia"]
        elif sector["sigla"] == "NAPNE":
            extra_keywords = ["acessibilidade", "inclusao", "necessidades educacionais"]
        elif sector["sigla"] == "CCM":
            extra_keywords = ["mecatronica", "curso de mecatronica"]
        elif sector["sigla"] == "CME":
            extra_keywords = ["mecanica", "curso de mecanica"]
        elif sector["sigla"] == "CCA":
            extra_keywords = ["agroindustria", "curso de agroindustria"]
        elif sector["sigla"] == "CCL":
            extra_keywords = ["lazer", "curso de lazer"]
        elif sector["sigla"] == "CBEB":
            extra_keywords = ["biossistemas", "engenharia de biossistemas"]
        elif sector["sigla"] == "CCB":
            extra_keywords = ["biologicas", "ciencias biologicas"]
        elif sector["sigla"] == "CLL":
            extra_keywords = ["letras", "portugues", "espanhol"]
        elif sector["sigla"] == "CTAG":
            extra_keywords = ["agronegocio", "gestao do agronegocio"]
        elif sector["sigla"] == "CTG":
            extra_keywords = ["gastronomia", "curso de gastronomia"]

        entries.append(
            {
                "id": f"setor-{normalize(sector['sigla']).replace(' ', '-')}",
                "tema": "setores e contatos",
                "perguntas_exemplo": [
                    f"Quem é responsável por {sector['setor']}?",
                    f"Qual o e-mail de {sector['setor']}?",
                    f"Como falar com {sector['sigla']}?"
                ],
                "resposta": f"{label}. Responsável: {sector['responsavel']}. E-mail: {sector['email']}.",
                "palavras_chave": [
                    sector["sigla"],
                    sector["setor"],
                    sector["responsavel"],
                    sector["email"],
                    "setor",
                    "coordenador",
                    "responsavel",
                    "responsável",
                    "email",
                    "e-mail"
                ] + extra_keywords,
                "setor_responsavel": sector["setor"],
                "fonte": "https://avr.ifsp.edu.br/fale-conosco-contato",
                "status": "publicado",
            }
        )

    return entries


def score_entry(question_tokens, entry):
    searchable = []
    searchable.append(entry.get("tema", ""))
    searchable.extend(entry.get("palavras_chave", []))
    searchable.extend(entry.get("perguntas_exemplo", []))

    entry_tokens = tokens(" ".join(searchable))
    overlap = question_tokens & entry_tokens

    keyword_bonus = 0
    normalized_question = normalize(" ".join(question_tokens))
    for keyword in entry.get("palavras_chave", []):
        normalized_keyword = normalize(keyword)
        if not normalized_keyword:
            continue
        if " " in normalized_keyword and normalized_keyword in normalized_question:
            keyword_bonus += 2
        elif normalized_keyword in question_tokens:
            keyword_bonus += 2

    return len(overlap) + keyword_bonus


def answer(question, knowledge=None):
    knowledge = knowledge or load_knowledge()
    question_tokens = tokens(question)
    sectors = sector_entries()
    site_pages = site_page_entries()

    sector_intent_words = {
        "quem",
        "coordena",
        "coordenador",
        "coordenadora",
        "responsavel",
        "email",
        "e-mail",
        "contato",
        "falar",
    }
    manual_intent_words = {"manual", "manuais", "tutorial", "tutoriais", "pdf"}
    if question_tokens & sector_intent_words and not question_tokens & manual_intent_words:
        ranked_sectors = sorted(
            ((score_entry(question_tokens, item), item) for item in sectors),
            key=lambda pair: pair[0],
            reverse=True,
        )
        if ranked_sectors and ranked_sectors[0][0] > 2:
            return ranked_sectors[0][1]

    knowledge = knowledge + sectors + site_pages

    fallback = next((item for item in knowledge if item["id"] == FALLBACK_ID), None)
    candidates = [item for item in knowledge if item["id"] != FALLBACK_ID]
    ranked = sorted(
        ((score_entry(question_tokens, item), item) for item in candidates),
        key=lambda pair: pair[0],
        reverse=True,
    )

    best_score, best_entry = ranked[0] if ranked else (0, None)
    if best_score <= 0 or best_entry is None:
        return fallback

    return best_entry


def format_answer(entry):
    lines = [
        f"Tema: {entry['tema']}",
        f"Resposta: {entry['resposta']}",
        f"Setor responsavel: {entry['setor_responsavel']}",
        f"Status: {entry['status']}",
    ]
    if entry.get("fonte"):
        lines.append(f"Fonte: {entry['fonte']}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Consulta a base de conhecimento da robo.")
    parser.add_argument("pergunta", help="Pergunta feita pelo usuario")
    args = parser.parse_args()

    result = answer(args.pergunta)
    print(format_answer(result))


if __name__ == "__main__":
    main()
