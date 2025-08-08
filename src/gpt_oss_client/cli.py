from __future__ import annotations
import typer
from rich.console import Console
from rich.markdown import Markdown
from typing import Optional

from .client import LLMClient
from .providers import Provider
from .schema import GenerationParams

app = typer.Typer(add_completion=False, no_args_is_help=True)
console = Console()


@app.callback()
def main() -> None:
    """CLI для gpt-oss-client"""
    return None


@app.command()
def serve(
    host: str = typer.Option("127.0.0.1", "--host"),
    port: int = typer.Option(8001, "--port"),
    reload: bool = typer.Option(False, "--reload"),
):
    """Запуск REST-сервера (FastAPI) для интеграции (например, n8n)."""
    import uvicorn

    uvicorn.run("gpt_oss_client.server:app", host=host, port=port, reload=reload)


@app.command()
def chat(
    message: str = typer.Option(..., "-m", "--message", help="Пользовательское сообщение"),
    provider: Provider = typer.Option(Provider.OPENAI_COMPAT, "--provider", case_sensitive=False),
    base_url: str = typer.Option("http://localhost:1234/v1", "--base-url", help="Базовый URL API"),
    model: str = typer.Option("gpt-oss-20b", "--model", help="Имя модели"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="API ключ для OpenAI-совместимого сервера"),
    show_raw: bool = typer.Option(False, "--show-raw", help="Показать сырой JSON ответа"),
    stream: bool = typer.Option(False, "--stream", help="Стримить ответ и разделять каналы рассуждений/финала"),
    temperature: Optional[float] = typer.Option(None, "--temperature", min=0.0, max=2.0),
    top_p: Optional[float] = typer.Option(None, "--top-p", min=0.0, max=1.0),
    max_tokens: Optional[int] = typer.Option(None, "--max-tokens"),
    json_output: bool = typer.Option(False, "--json-output/--no-json-output"),
    strict_json: bool = typer.Option(False, "--strict-json/--no-strict-json"),
):
    if provider == Provider.OLLAMA and base_url.endswith("/v1"):
        base_url = base_url[:-3]

    client = LLMClient(provider=provider, base_url=base_url, model=model, api_key=api_key)
    gen = GenerationParams(
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens,
        json_output=json_output,
        strict_json=strict_json,
    )

    if stream:
        console.rule("Стрим: рассуждения → финал")
        try:
            for channel, text in client.stream_chat(message, gen=gen):
                if not text:
                    continue
                if channel == "reasoning":
                    console.print(f"[dim]{text}[/dim]", end="")
                else:
                    console.print(f"[bold]{text}[/bold]", end="")
            console.print()
        except KeyboardInterrupt:
            console.print("\n[red]Прервано пользователем[/red]")
        return

    result = client.chat(message, gen=gen)

    if result.reasoning:
        console.rule("Рассуждения")
        console.print(Markdown(result.reasoning))
    console.rule("Финальный ответ")
    console.print(result.final_answer or "(пусто)")

    if show_raw and result.raw is not None:
        console.rule("Raw JSON")
        console.print_json(data=result.raw)


if __name__ == "__main__":
    app()
