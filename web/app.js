const form = document.querySelector("#ask-form");
const questionInput = document.querySelector("#question");
const answerEl = document.querySelector("#answer");
const topicEl = document.querySelector("#topic");
const sectorEl = document.querySelector("#sector");
const sourceEl = document.querySelector("#source");
const statusEl = document.querySelector("#status");
const quickButtons = document.querySelectorAll("[data-question]");
let localKnowledgePromise;

function normalize(text) {
  return String(text)
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9\s-]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function tokens(text) {
  return new Set(normalize(text).split(" ").filter(Boolean));
}

function scoreEntry(questionTokens, entry) {
  const searchable = [
    entry.tema || "",
    ...(entry.palavras_chave || []),
    ...(entry.perguntas_exemplo || []),
  ];
  const entryTokens = tokens(searchable.join(" "));
  let score = 0;

  for (const token of questionTokens) {
    if (entryTokens.has(token)) score += 1;
  }

  const normalizedQuestion = normalize([...questionTokens].join(" "));
  for (const keyword of entry.palavras_chave || []) {
    const normalizedKeyword = normalize(keyword);
    if (!normalizedKeyword) continue;
    if (normalizedKeyword.includes(" ") && normalizedQuestion.includes(normalizedKeyword)) {
      score += 2;
    } else if (questionTokens.has(normalizedKeyword)) {
      score += 2;
    }
  }

  return score;
}

function sectorEntries(sectors) {
  const aliases = {
    CRA: ["secretaria", "registros academicos", "documentos academicos", "matricula", "historico", "declaracao"],
    CBI: ["biblioteca", "livro", "emprestimo"],
    CTI: ["tecnologia", "informatica", "wifi", "internet"],
    SSP: ["assistencia estudantil", "sociopedagogica", "auxilio", "permanencia"],
    NAPNE: ["acessibilidade", "inclusao", "necessidades educacionais"],
    CCM: ["mecatronica", "curso de mecatronica"],
    CME: ["mecanica", "curso de mecanica"],
    CCA: ["agroindustria", "curso de agroindustria"],
    CCL: ["lazer", "curso de lazer"],
    CBEB: ["biossistemas", "engenharia de biossistemas"],
    CCB: ["biologicas", "ciencias biologicas"],
    CLL: ["letras", "portugues", "espanhol"],
    CTAG: ["agronegocio", "gestao do agronegocio"],
    CTG: ["gastronomia", "curso de gastronomia"],
  };

  return sectors.map((sector) => ({
    id: `setor-${normalize(sector.sigla).replaceAll(" ", "-")}`,
    tema: "setores e contatos",
    perguntas_exemplo: [
      `Quem é responsável por ${sector.setor}?`,
      `Qual o e-mail de ${sector.setor}?`,
      `Como falar com ${sector.sigla}?`,
    ],
    resposta: `${sector.sigla} - ${sector.setor}. Responsável: ${sector.responsavel}. E-mail: ${sector.email}.`,
    palavras_chave: [
      sector.sigla,
      sector.setor,
      sector.responsavel,
      sector.email,
      "setor",
      "coordenador",
      "responsavel",
      "responsável",
      "email",
      "e-mail",
      ...(aliases[sector.sigla] || []),
    ],
    setor_responsavel: sector.setor,
    fonte: "https://avr.ifsp.edu.br/fale-conosco-contato",
    status: "publicado",
  }));
}

function sitePageEntries(pages) {
  return pages.map((page, index) => {
    const title = page.title || page.url;
    const headings = page.headings || [];
    const emails = page.emails || [];
    const phones = page.phones || [];
    const details = [];

    if (page.summary) details.push(page.summary);
    if (emails.length) details.push(`E-mails encontrados: ${emails.join(", ")}`);
    if (phones.length) details.push(`Telefones encontrados: ${phones.join(", ")}`);

    let resposta = `Encontrei uma página oficial relacionada: ${title}. Acesse: ${page.url}.`;
    if (details.length) resposta += ` ${details.join(" ")}`;

    return {
      id: `site-page-${index + 1}`,
      tema: "indice do site",
      perguntas_exemplo: [title, ...headings.slice(0, 6)],
      resposta: resposta.slice(0, 1800),
      palavras_chave: [title, ...headings.slice(0, 8), ...emails, page.url || ""],
      setor_responsavel: "Site oficial do IFSP Avaré",
      fonte: page.url,
      status: "publicado",
    };
  });
}

async function loadJson(path) {
  const response = await fetch(path);
  if (!response.ok) throw new Error(`Falha ao carregar ${path}`);
  return response.json();
}

async function loadLocalKnowledge() {
  if (!localKnowledgePromise) {
    localKnowledgePromise = Promise.all([
      loadJson("data/base_conhecimento.json"),
      loadJson("data/setores.json").catch(() => []),
      loadJson("data/site_pages.json").catch(() => ({ pages: [] })),
    ]).then(([knowledge, sectors, sitePayload]) => ({
      knowledge,
      sectors: sectorEntries(sectors),
      sitePages: sitePageEntries(sitePayload.pages || []),
    }));
  }

  return localKnowledgePromise;
}

async function askLocal(question) {
  const { knowledge, sectors, sitePages } = await loadLocalKnowledge();
  const questionTokens = tokens(question);
  const fallback = knowledge.find((item) => item.id === "nao-encontrado");
  const sectorIntentWords = new Set(["quem", "coordena", "coordenador", "coordenadora", "responsavel", "email", "e-mail", "contato", "falar"]);
  const manualIntentWords = new Set(["manual", "manuais", "tutorial", "tutoriais", "pdf"]);
  const hasSectorIntent = [...questionTokens].some((token) => sectorIntentWords.has(token));
  const hasManualIntent = [...questionTokens].some((token) => manualIntentWords.has(token));

  if (hasSectorIntent && !hasManualIntent) {
    const [bestSector] = sectors
      .map((entry) => [scoreEntry(questionTokens, entry), entry])
      .sort((a, b) => b[0] - a[0]);
    if (bestSector && bestSector[0] > 2) return bestSector[1];
  }

  const candidates = [...knowledge, ...sectors, ...sitePages].filter((item) => item.id !== "nao-encontrado");
  const [best] = candidates
    .map((entry) => [scoreEntry(questionTokens, entry), entry])
    .sort((a, b) => b[0] - a[0]);

  if (!best || best[0] <= 0) return fallback;
  return best[1];
}

function sourceMarkup(source) {
  if (!source) return "-";

  const urls = source.match(/https?:\/\/[^\s]+/g);
  if (!urls) return escapeHtml(source);

  let output = escapeHtml(source);
  for (const url of urls) {
    const cleanUrl = url.replace(/[.,)]$/, "");
    output = output.replace(
      escapeHtml(url),
      `<a href="${cleanUrl}" target="_blank" rel="noreferrer">${cleanUrl}</a>`
    );
  }
  return output;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function setLoading() {
  answerEl.textContent = "Consultando a base de conhecimento...";
  topicEl.textContent = "-";
  sectorEl.textContent = "-";
  sourceEl.textContent = "-";
  statusEl.textContent = "buscando";
  statusEl.className = "status";
}

function renderResult(data) {
  answerEl.textContent = data.resposta || "Não encontrei uma resposta.";
  topicEl.textContent = data.tema || "-";
  sectorEl.textContent = data.setor_responsavel || "-";
  sourceEl.innerHTML = sourceMarkup(data.fonte);
  statusEl.textContent = data.status || "-";
  statusEl.className = `status ${data.status === "rascunho" ? "rascunho" : ""}`;
}

async function ask(question) {
  const cleanQuestion = question.trim();
  if (!cleanQuestion) return;
  setLoading();

  try {
    const response = await fetch("/api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: cleanQuestion }),
    });

    if (response.ok) {
      renderResult(await response.json());
      return;
    }
  } catch (error) {
    // No GitHub Pages nao existe API Python; nesse caso usamos a base JSON local.
  }

  renderResult(await askLocal(cleanQuestion));
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    await ask(questionInput.value);
  } catch (error) {
    answerEl.textContent = "Não consegui consultar a base agora. Verifique se os arquivos de dados foram publicados junto com a página.";
    statusEl.textContent = "erro";
    statusEl.className = "status rascunho";
  }
});

quickButtons.forEach((button) => {
  button.addEventListener("click", () => {
    questionInput.value = button.dataset.question;
    form.requestSubmit();
  });
});
