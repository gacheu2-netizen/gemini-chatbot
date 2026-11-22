import sys

from rich.console import Console
from rich.panel import Panel

from gemini_chatbot.client import GeminiChatClient
from gemini_chatbot.config import load_settings

EXIT_COMMANDS = {"/exit", "exit", "quit"}
HELP_TEXT = (
    "사용 가능한 명령어:\n"
    "  /help          도움말 보기\n"
    "  /exit, quit    챗봇 종료\n"
    "\n"
    "참고: 이 챗봇은 메모리 기능이 없어 매 질문을 독립적으로 처리합니다."
)


def main() -> None:
    console = Console()

    try:
        settings = load_settings()
    except ValueError as exc:
        console.print(f"[bold red]설정 오류:[/bold red] {exc}")
        sys.exit(1)

    chat_client = GeminiChatClient(settings)

    console.print(
        Panel.fit(
            f"[bold green]Gemini 터미널 챗봇[/bold green]\n"
            f"모델: [cyan]{chat_client.model}[/cyan] | 모드: [yellow]무상태(메모리 없음)[/yellow]\n"
            f"도움말: [bold]/help[/bold] | 종료: [bold]/exit[/bold]",
            border_style="green",
        )
    )

    while True:
        try:
            user_input = console.input("\n[bold cyan]You>[/bold cyan] ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]챗봇을 종료합니다.[/dim]")
            break

        if not user_input:
            continue

        lowered = user_input.lower()
        if lowered in EXIT_COMMANDS:
            console.print("[dim]챗봇을 종료합니다.[/dim]")
            break

        if lowered == "/help":
            console.print(Panel(HELP_TEXT, title="도움말", border_style="cyan"))
            continue

        console.print("[bold magenta]Gemini>[/bold magenta] ", end="")
        try:
            has_output = False
            for chunk in chat_client.send_message_stream(user_input):
                has_output = True
                console.print(chunk, end="", markup=False, highlight=False)
            if not has_output:
                console.print("[dim](응답 텍스트가 비어 있습니다)[/dim]", end="")
            console.print()
        except Exception as exc:  # noqa: BLE001
            console.print(f"\n[bold red]API 호출 오류:[/bold red] {exc}")


if __name__ == "__main__":
    main()
