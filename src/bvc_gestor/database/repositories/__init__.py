from .cuenta_repository import CuentaRepository
from .orden_repository import OrdenRepository
from sqlalchemy.orm import Session

class RepositoryFactory:
    _repos = {
        'cuenta': CuentaRepository,
        'orden': OrdenRepository
    }

    @staticmethod
    def get_repository(session: Session, name: str):
        repo_class = RepositoryFactory._repos.get(name.lower())
        if not repo_class:
            raise ValueError(f"El repositorio '{name}' no existe en la fábrica.")
        return repo_class(session)