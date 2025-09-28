# src/integrations/ollama_client.py
import json
from datetime import datetime, date, timedelta
from calendar import monthrange
from ollama import chat
from ollama import ChatResponse

INTENTS = ["agendar_consulta", "geral"]

SYSTEM_INTENT = (
    "Você é um classificador de intenção.\n"
    "Analise a ÚLTIMA mensagem do usuário considerando no máximo 10 mensagens de histórico.\n"
    "Saída OBRIGATÓRIA: JSON válido exatamente assim: {\"intent\":\"agendar_consulta\"} ou {\"intent\":\"geral\"}.\n"
    "Regra:\n"
    "- Retorne \"agendar_consulta\" SOMENTE se a última mensagem indicar claramente agendamento de consulta "
    "(agendar, marcar, consulta, médico, doutor, especialidade, horário, data) ou se o histórico sinaliza esse fluxo.\n"
    "- Caso contrário, retorne \"geral\".\n"
    "Não explique, não adicione campos além de \"intent\"."
)

# 1) Extrai specialty e city (e preferência de período opcional)
SYSTEM_EXTRACT = (
    "Você extrai dados para agendamento de consultas.\n"
    "Com base no histórico e na última mensagem, extraia POSSIVELMENTE:\n"
    "- specialty (TEXT), city (TEXT), period (TEXT: YYYY-MM-DD).\n"
    "Se não souber, use null.\n"
    "SAÍDA OBRIGATÓRIA (JSON EXATO):\n"
    "{\n"
    "  \"specialty\": null,\n"
    "  \"city\": null,\n"
    "  \"period\": null\n"
    "}\n"
    "Não escreva nada fora do JSON."
)

# 2) Gera nomes de médicos e datas (sem BD)
SYSTEM_GENERATE = (
    "Você gera OPÇÕES para o usuário agendar consultas.\n"
    "Regras para GERAR:\n"
    "- Gere entre 3 e 5 médicos NOMEADOS que atendam a SPECIALTY na CITY.\n"
    "- Use nomes brasileiros plausíveis, misture 'Dr.' e 'Dra.' e NUNCA repita.\n"
    "- Gere entre 3 e 5 DATAS futuras no formato YYYY-MM-DD, SOMENTE no mês atual ou no próximo.\n"
    "- Evite datas no passado.\n"
    "SAÍDA OBRIGATÓRIA (JSON EXATO):\n"
    "{\n"
    "  \"doctors\": [{\"id\": 1, \"name\": \"Dr. Nome Sobrenome\", \"specialty\": \"...\", \"city\": \"...\"}],\n"
    "  \"dates\": [\"YYYY-MM-DD\", \"YYYY-MM-DD\"]\n"
    "}\n"
    "Não escreva nada fora do JSON."
)

def _safe_json_loads(text: str):
    try:
        return json.loads(text)
    except Exception:
        return None

def _month_window(today: date) -> tuple[date, date]:
    """Janela: hoje até o último dia do PRÓXIMO mês."""
    y, m = today.year, today.month
    # fim do mês atual
    _, last_day_curr = monthrange(y, m)
    end_curr = date(y, m, last_day_curr)
    # fim do próximo mês
    if m == 12:
        y2, m2 = y + 1, 1
    else:
        y2, m2 = y, m + 1
    _, last_day_next = monthrange(y2, m2)
    end_next = date(y2, m2, last_day_next)
    return (today, end_next)

def _clamp_dates(dates: list[str]) -> list[str]:
    """Mantém apenas datas válidas no mês atual/próximo (>= hoje)."""
    today = datetime.now().date()
    start, end = _month_window(today)
    valid = []
    for s in dates:
        try:
            d = datetime.strptime(s, "%Y-%m-%d").date()
            if start <= d <= end:
                valid.append(s)
        except Exception:
            continue
    # remove duplicadas preservando ordem
    seen = set()
    dedup = []
    for x in valid:
        if x not in seen:
            seen.add(x)
            dedup.append(x)
    return dedup[:5]

def _renumber_doctors(doctors: list[dict], specialty: str, city: str) -> list[dict]:
    """Garante id sequencial a partir de 1 e preenche specialty/city."""
    out = []
    used_names = set()
    for i, d in enumerate(doctors[:5], start=1):
        name = (d.get("name") or "").strip()
        if not name or name.lower() in used_names:
            continue
        used_names.add(name.lower())
        out.append({
            "id": i,
            "name": name,
            "specialty": specialty,
            "city": city
        })
    return out

class OllamaClient:
    model = 'llama3.1:8b-instruct-q4_K_M'

    def __init__(self):
        with open('src/integrations/configs/contexto.txt', "r", encoding="utf-8") as f:
            contexto = f.read().strip()
        self.messages = [{"role": "system", "content": contexto}]

    # ————————————————————————— intent
    def classify_intent(self, prompt: str, extra_messages=None) -> str:
        messages = [{"role": "system", "content": SYSTEM_INTENT}]
        if extra_messages:
            messages.extend(extra_messages)
        messages.append({"role": "user", "content": prompt})

        resp = chat(
            model=self.model,
            messages=messages,
            format="json",
            options={"temperature": 0, "top_p": 1}
        )
        data = _safe_json_loads(resp["message"]["content"]) or {}
        intent = data.get("intent")
        return intent if intent in INTENTS else "geral"

    # ————————————————————————— core: extrai e gera opções
    def generate_options(self, prompt: str, extra_messages=None):
        """
        Pipeline:
          1) Extrai specialty + city
          2) Gera até 5 médicos e 5 datas (hoje → fim do próximo mês)
          3) Valida/filtra e retorna contrato único para o front
        Retorno:
        {
          "answer": "<frase curta>",
          "state": {
            "intent": "agendar_consulta",
            "collected": {"specialty": "...", "city": "...", "period": null},
            "options": {"doctors":[...], "dates":[...]}
          }
        }
        """
        # 1) EXTRAÇÃO
        extract_msgs = [{"role": "system", "content": SYSTEM_EXTRACT}]
        if extra_messages:
            extract_msgs.extend(extra_messages)
        extract_msgs.append({"role": "user", "content": prompt})

        r1 = chat(
            model=self.model,
            messages=extract_msgs,
            format="json",
            options={"temperature": 0, "top_p": 1, "num_ctx": 2048}
        )
        info = _safe_json_loads(r1["message"]["content"]) or {}
        specialty = (info.get("specialty") or "").strip()
        city = (info.get("city") or "").strip()
        period = info.get("period")

        if not specialty or not city:
            # peça o que falta, sem inventar
            missing = []
            if not specialty: missing.append("especialidade")
            if not city:       missing.append("cidade")
            ask = " e ".join(missing)
            return {
                "answer": f"Para continuar, informe {ask} (ex.: 'Cardiologia em São Paulo').",
                "state": {
                    "intent": "agendar_consulta",
                    "collected": {"specialty": specialty or None, "city": city or None, "period": period or None},
                    "options": {"doctors": [], "dates": []}
                }
            }

        # 2) GERAÇÃO (nomes + datas)
        gen_prompt = (
            f"SPECIALTY: {specialty}\n"
            f"CITY: {city}\n"
            "Gere entre 3 e 5 médicos e 3 a 5 datas (YYYY-MM-DD) dentro do mês atual ou do próximo."
        )
        gen_msgs = [{"role": "system", "content": SYSTEM_GENERATE},
                    {"role": "user", "content": gen_prompt}]

        r2 = chat(
            model=self.model,
            messages=gen_msgs,
            format="json",
            options={"temperature": 0, "top_p": 1, "num_ctx": 2048}
        )
        raw2 = _safe_json_loads(r2["message"]["content"]) or {}
        doctors = raw2.get("doctors") or []
        dates = raw2.get("dates") or []

        # 3) VALIDAÇÃO/normalização no back
        dates_ok = _clamp_dates(dates)
        doctors_ok = _renumber_doctors(doctors, specialty, city)

        # fallback seguro se vier vazio
        if not doctors_ok:
            doctors_ok = _renumber_doctors(
                [{"name": f"Dr. {specialty} {i}"} for i in ["Silva","Santos","Souza","Lima","Oliveira"]],
                specialty, city
            )[:3]
        if not dates_ok:
            today = datetime.now().date()
            start, end = _month_window(today)
            # gera 3 datas espaçadas (D+3, D+10, D+17) dentro da janela
            seeds = [3, 10, 17, 24, 27]
            dates_ok = []
            for s in seeds:
                d = today + timedelta(days=s)
                if start <= d <= end:
                    dates_ok.append(d.strftime("%Y-%m-%d"))
                if len(dates_ok) >= 3:
                    break

        # resposta curta
        doc_list = "; ".join([f"#{d['id']} {d['name']}" for d in doctors_ok])
        first_dates = ", ".join(dates_ok[:3])
        answer = (
            f"Encontrei {len(doctors_ok)} médico(s) de {specialty} em {city}: {doc_list}. "
            f"Datas sugeridas: {first_dates}. "
            f"Responda com o código do médico (ex.: #1) e uma das datas."
        )

        return {
            "answer": answer,
            "state": {
                "intent": "agendar_consulta",
                "collected": {"specialty": specialty, "city": city, "period": period or None},
                "options": {"doctors": doctors_ok, "dates": dates_ok}
            }
        }

    # (opcional) seu generate normal permanece igual
    def generate(self, prompt: str, as_json=False, extra_messages=None):
        if extra_messages is None:
            extra_messages = []
        opts = {
            'temperature': 0.2,
            'top_p': 0.9,
            'repeat_penalty': 1.05,
            'num_ctx': 8192
        }
        kwargs = {
            'model': self.model,
            'messages': [
                {"role": "system", "content": self.messages[0]['content']},
                *extra_messages,
                {"role": "user", "content": prompt}
            ],
            'options': opts
        }
        if as_json:
            kwargs['as_json'] = True

        response: ChatResponse = chat(**kwargs)
        return response['message']['content']


ollama_client = OllamaClient()
