import re

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from app.config import settings
from app.models.schemas import DiagnoseResponse, IncidentSummary, Severity
from app.services import skills_repo
from app.services.new_deployment import check_k8s_deployment_exists, perform_k8s_deployment

_VALID_K8S_NAME = re.compile(r"^[a-z0-9]([-a-z0-9]*[a-z0-9])?$")

# In-memory store standing in for a real datastore in this POC.
_incidents: list[IncidentSummary] = []

_ERROR_PATTERNS: list[tuple[str, Severity, str, list[str]]] = [
    ("outofmemory", Severity.critical, "Process exceeded available memory (OOM kill)",
     ["Check container/pod memory limits", "Inspect for memory leaks in recent deploys", "Scale up memory requests"]),
    ("connection refused", Severity.high, "Downstream service is unreachable",
     ["Verify the downstream service is running", "Check network policies / security groups", "Confirm DNS resolution"]),
    ("timeout", Severity.medium, "A dependent call exceeded its time budget",
     ["Check latency on downstream dependencies", "Review recent timeout/retry configuration changes"]),
    ("5xx", Severity.high, "Upstream service returned server errors",
     ["Check upstream service health and error logs", "Roll back the most recent deploy if correlated"]),
    ("disk", Severity.critical, "Host or volume is low on disk space",
     ["Free up disk space or expand the volume", "Check log rotation settings"]),
]


def diagnose(source: str, logs: str) -> DiagnoseResponse:
    lowered = logs.lower()
    for pattern, severity, root_cause, actions in _ERROR_PATTERNS:
        if pattern in lowered:
            response = DiagnoseResponse(
                severity=severity,
                root_cause=root_cause,
                recommended_actions=actions,
            )
            break
    else:
        response = DiagnoseResponse(
            severity=Severity.low,
            root_cause="No known failure pattern matched; manual review recommended",
            recommended_actions=["Review the raw logs for anomalies", "Check recent deploys and config changes"],
        )

    _incidents.append(
        IncidentSummary(
            incident_id=response.incident_id,
            source=source,
            severity=response.severity,
            root_cause=response.root_cause,
            timestamp=response.timestamp,
        )
    )
    return response


def list_incidents() -> list[IncidentSummary]:
    return list(_incidents)


def _fallback_chat(message: str) -> str:
    lowered = message.lower()
    if any(word in lowered for word in ("down", "outage", "incident")):
        return "It sounds like a service may be impacted. Share the relevant logs with /diagnose and I'll suggest a root cause."
    if any(word in lowered for word in ("hello", "hi", "hey")):
        return "Hi, I'm the SRE agent. Describe an issue or send logs to /diagnose and I'll help triage it."
    return "Got it. This is a scaffolded response — wire up real reasoning (e.g. an LLM call) in app/services/agent_service.py."


def _build_context(question: str) -> str:
    matched = skills_repo.match_skills(question)
    skills_context = skills_repo.render_context(matched or None)

    recent = _incidents[-20:]
    if recent:
        incidents_context = "\n".join(
            f"- [{i.timestamp.isoformat()}] ({i.severity.value}) {i.source}: "
            f"{i.root_cause} (id: {i.incident_id})"
            for i in reversed(recent)
        )
    else:
        incidents_context = "No incidents recorded yet."

    return (
        f"KNOWN SRE SKILLS / RUNBOOKS:\n{skills_context}\n\n"
        f"RECENT INCIDENTS:\n{incidents_context}"
    )


_CHATBOT_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are an SRE operations assistant.

Answer only from the supplied context (skill repo runbooks and recorded incidents).
Do not invent incidents, metrics, causes, timestamps, or remedies.
If the answer is not available, say that clearly.

Be concise, operational, and useful to an SRE engineer.
""",
        ),
        (
            "human",
            """
CONTEXT:
{context}

QUESTION:
{question}
""",
        ),
    ]
)


async def ask_sre_chatbot(question: str) -> str:
    if not settings.openai_api_key:
        return (
            "OPENAI_API_KEY is not configured. The operational data is being "
            "stored correctly, but AI chatbot responses require an LLM key."
        )

    llm = ChatOpenAI(
        model=settings.openai_model,
        temperature=0,
        api_key=settings.openai_api_key,
    )

    response = await (_CHATBOT_PROMPT | llm).ainvoke(
        {
            "context": _build_context(question),
            "question": question,
        }
    )

    return response.content


async def chat(message: str) -> str:
    if not settings.openai_api_key:
        return _fallback_chat(message)
    return await ask_sre_chatbot(message)

async def spread_deployment_dto(message: str) -> dict:
    ...


def _validate_deployment_dto(deployment_dto: dict | None) -> str | None:
    """Returns an error message if the deployment can't be created, else None."""
    if not deployment_dto:
        return "Could not extract deployment details from the message."

    deployment_name = deployment_dto.get("deployment_name")
    image = deployment_dto.get("image")
    if not deployment_name or not image:
        return "Missing required 'deployment_name' or 'image'."
    if not _VALID_K8S_NAME.match(deployment_name):
        return f"'{deployment_name}' is not a valid Kubernetes resource name."
    if check_k8s_deployment_exists(deployment_name):
        return f"A deployment named '{deployment_name}' already exists."

    return None


async def create_new_deployment(message: str) -> str:
    deployment_dto = await spread_deployment_dto(message)

    error = _validate_deployment_dto(deployment_dto)
    if error:
        return f"Cannot create deployment: {error}"

    perform_k8s_deployment(
        deployment_name=deployment_dto["deployment_name"],
        image=deployment_dto["image"],
        replicas=deployment_dto.get("replicas", 1),
        container_port=deployment_dto.get("container_port", 80),
        service_port=deployment_dto.get("service_port", 80),
        ingress_host=deployment_dto.get("ingress_host"),
        envorinment_variables=deployment_dto.get("envorinment_variables"),
        secret_variables=deployment_dto.get("secret_variables"),
    )
    return f"Deployment '{deployment_dto['deployment_name']}' created."
