from fastapi import FastAPI


_app = None


def set_global_app(app: FastAPI):
    global _app
    _app = app


def get_current_app() -> FastAPI:
    if not _app:
        raise RuntimeError("Application not initialized!")
    return _app