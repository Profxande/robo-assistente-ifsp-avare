import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from brain import answer


ROOT = Path(__file__).resolve().parents[1]
WEB_ROOT = ROOT / "web"


class RobotHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_ROOT), **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/api/ask":
            params = parse_qs(parsed.query)
            question = params.get("q", [""])[0].strip()
            self.send_json(build_answer(question))
            return

        if parsed.path == "/api/health":
            self.send_json({"status": "ok", "service": "robo-assistente"})
            return

        super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/api/ask":
            self.send_error(404)
            return

        length = int(self.headers.get("Content-Length", "0"))
        payload = self.rfile.read(length).decode("utf-8")
        data = json.loads(payload or "{}")
        question = str(data.get("question", "")).strip()
        self.send_json(build_answer(question))

    def send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def build_answer(question):
    if not question:
        return {
            "question": question,
            "tema": "entrada vazia",
            "resposta": "Digite uma pergunta para eu consultar minha base.",
            "setor_responsavel": "Equipe do projeto",
            "status": "rascunho",
            "fonte": None,
        }

    result = answer(question)
    return {
        "question": question,
        "id": result.get("id"),
        "tema": result.get("tema"),
        "resposta": result.get("resposta"),
        "setor_responsavel": result.get("setor_responsavel"),
        "status": result.get("status"),
        "fonte": result.get("fonte"),
    }


def main():
    server = ThreadingHTTPServer(("127.0.0.1", 8765), RobotHandler)
    print("Servidor da robo em http://127.0.0.1:8765")
    server.serve_forever()


if __name__ == "__main__":
    main()

