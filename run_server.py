import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
import uvicorn


def main() -> None:
    project_root = Path(__file__).parent.resolve()
    backend_dir = project_root / "backend"

    # Ensure we can import the "app" package inside backend/
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))

    # Load environment variables from backend/.env if present
    env_path = backend_dir / ".env"
    if env_path.exists():
        load_dotenv(env_path)

    parser = argparse.ArgumentParser(description="Run FastAPI server")
    parser.add_argument("--host", default=os.getenv("HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int,
                        default=int(os.getenv("PORT", "8000")))
    parser.add_argument("--reload", action="store_true", default=True)
    args = parser.parse_args()

    # Run uvicorn; module path resolved thanks to sys.path tweak
    uvicorn.run(
        "app.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        reload_dirs=[str(backend_dir)],
    )


if __name__ == "__main__":
    main()
