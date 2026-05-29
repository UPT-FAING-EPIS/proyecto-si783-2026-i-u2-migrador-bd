import os
from github import Github


def upload_file_to_github(repo_full_name: str, path_in_repo: str, local_file_path: str, commit_message: str, github_token: str = None):
    """Sube o actualiza un archivo en un repositorio de GitHub usando la API.

    - `repo_full_name`: 'owner/repo'
    - `path_in_repo`: ruta dentro del repo, por ejemplo 'backups/miarchivo.sql'
    - `local_file_path`: ruta local al archivo en disco
    - `commit_message`: mensaje del commit
    - `github_token`: token personal; si None se usa GITHUB_TOKEN env var

    Devuelve dict con keys: exito(bool), mensaje(str), url(str|None)
    """
    token = github_token or os.getenv('GITHUB_TOKEN')
    if not token:
        return {'exito': False, 'mensaje': 'Falta GITHUB_TOKEN en variables de entorno', 'url': None}

    if not os.path.exists(local_file_path):
        return {'exito': False, 'mensaje': f'Archivo local no encontrado: {local_file_path}', 'url': None}

    try:
        gh = Github(token)
        repo = gh.get_repo(repo_full_name)

        with open(local_file_path, 'rb') as f:
            content = f.read()

        # Comprobar si el archivo ya existe en la ruta indicada
        try:
            existing = repo.get_contents(path_in_repo)
            # Actualizar
            repo.update_file(path_in_repo, commit_message, content, existing.sha)
            url = f'https://github.com/{repo_full_name}/blob/main/{path_in_repo}'
            return {'exito': True, 'mensaje': 'Archivo actualizado en GitHub', 'url': url}
        except Exception:
            # Crear nuevo archivo
            repo.create_file(path_in_repo, commit_message, content)
            url = f'https://github.com/{repo_full_name}/blob/main/{path_in_repo}'
            return {'exito': True, 'mensaje': 'Archivo subido a GitHub', 'url': url}

    except Exception as e:
        return {'exito': False, 'mensaje': f'Error subiendo a GitHub: {str(e)}', 'url': None}
