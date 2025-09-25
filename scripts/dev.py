import os
import signal
import subprocess
import sys
from contextlib import suppress

from dotenv import load_dotenv


def start_uvicorn(host: str, port: int, reload: bool) -> subprocess.Popen:
    args = [
        sys.executable,
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        host,
        "--port",
        str(port),
    ]
    if reload:
        args.append("--reload")
    return subprocess.Popen(args)


def start_ngrok(port: int):
    try:
        from pyngrok import conf, ngrok  # type: ignore
    except Exception:
        print("pyngrok not installed; skipping ngrok setup.")
        return None, None

    authtoken = os.getenv("NGROK_AUTHTOKEN")
    region = os.getenv("NGROK_REGION", "us")

    if not authtoken:
        print("NGROK_AUTHTOKEN not set; skipping ngrok setup.")
        return None, None

    conf.get_default().auth_token = authtoken
    conf.get_default().region = region

    try:
        tunnel = ngrok.connect(addr=port, proto="http", bind_tls=True)
        public_url = tunnel.public_url
        print(f"ngrok tunnel active: {public_url} -> http://127.0.0.1:{port}")
        return tunnel, public_url
    except Exception as exc:
        print(f"Failed to start ngrok tunnel: {exc}")
        return None, None


def main() -> None:
    load_dotenv()

    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", "8000"))
    enable_reload = os.getenv("RELOAD", "1") not in {"0", "false", "False"}

    tunnel, _ = start_ngrok(port)

    uvicorn_proc = start_uvicorn(host, port, reload=enable_reload)

    def handle_signal(signum, frame):  # type: ignore[unused-ignore]
        with suppress(Exception):
            uvicorn_proc.terminate()
        if tunnel is not None:
            try:
                from pyngrok import ngrok  # type: ignore

                ngrok.kill()
            except Exception:
                pass

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    try:
        uvicorn_proc.wait()
    finally:
        if tunnel is not None:
            try:
                from pyngrok import ngrok  # type: ignore

                ngrok.kill()
            except Exception:
                pass


if __name__ == "__main__":
    main()
