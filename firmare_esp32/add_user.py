# =============================================================================
# PROYECTO   : Vision Guard
# ARCHIVO    : add_user.py
# DESCRIPCIÓN: Script de utilidad para crear usuarios en Firestore.
#             
#              MEJORAS:
#                - Función update_user() para cambiar contraseña
#                - Función list_users() para listar usuarios existentes
#                - Función delete_user() para eliminar usuarios
#                - Modo interactivo con menú de opciones
# EJECUTAR:  python add_user.py
# =============================================================================

from firebase_init import db
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ─────────────────────────────────────────────────────────────────────────────
# FUNCIONES CRUD DE USUARIOS
# ─────────────────────────────────────────────────────────────────────────────

def add_user(username: str, password: str) -> bool:
    """
    Crea un nuevo usuario en la colección 'users' de Firestore.
    RECICLADO de add_user.py del SmartCap.

    Devuelve True si se creó, False si ya existía.
    """
    users_ref = db.collection('users')
    # Verificar si ya existe
    existente = list(users_ref.where('username', '==', username).stream())
    if existente:
        print(f"[add_user] El usuario '{username}' ya existe.")
        return False

    password_hash = pwd_context.hash(password)
    users_ref.add({
        'username'      : username,
        'password_hash' : password_hash,
        'created_at'    : __import__('time').time(),
    })
    print(f"[add_user] Usuario '{username}' creado exitosamente.")
    return True


def update_user(username: str, nueva_password: str) -> bool:
    """
    Actualiza la contraseña de un usuario existente.
    NUEVO respecto al original.
    """
    docs = list(db.collection('users').where('username', '==', username).stream())
    if not docs:
        print(f"[update_user] Usuario '{username}' no encontrado.")
        return False
    nuevo_hash = pwd_context.hash(nueva_password)
    docs[0].reference.update({'password_hash': nuevo_hash})
    print(f"[update_user] Contraseña de '{username}' actualizada.")
    return True


def delete_user(username: str) -> bool:
    """
    Elimina un usuario de Firestore.
    NUEVO respecto al original.
    """
    docs = list(db.collection('users').where('username', '==', username).stream())
    if not docs:
        print(f"[delete_user] Usuario '{username}' no encontrado.")
        return False
    docs[0].reference.delete()
    print(f"[delete_user] Usuario '{username}' eliminado.")
    return True


def list_users() -> list:
    """
    Lista todos los usuarios registrados (sin mostrar contraseñas).
    NUEVO respecto al original.
    """
    docs = list(db.collection('users').stream())
    if not docs:
        print("[list_users] No hay usuarios registrados.")
        return []
    print(f"\n{'─'*40}")
    print(f"  {'#':<4} {'Usuario':<20} {'Creado':<20}")
    print(f"{'─'*40}")
    usuarios = []
    for i, doc in enumerate(docs, 1):
        d = doc.to_dict()
        import time, datetime
        ts = d.get('created_at', 0)
        fecha = (datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')
                 if ts else 'N/A')
        print(f"  {i:<4} {d.get('username','?'):<20} {fecha:<20}")
        usuarios.append(d.get('username'))
    print(f"{'─'*40}\n")
    return usuarios


# ─────────────────────────────────────────────────────────────────────────────
# MODO INTERACTIVO
# ─────────────────────────────────────────────────────────────────────────────
def menu():
    opciones = {
        '1': ('Crear usuario',      lambda: _crear()),
        '2': ('Cambiar contraseña', lambda: _cambiar()),
        '3': ('Eliminar usuario',   lambda: _eliminar()),
        '4': ('Listar usuarios',    lambda: list_users()),
        '5': ('Salir',              None),
    }
    while True:
        print("\n=== Safe-Path AI — Gestión de Usuarios ===")
        for k, (desc, _) in opciones.items():
            print(f"  {k}. {desc}")
        opcion = input("Opción: ").strip()
        if opcion == '5':
            break
        if opcion in opciones:
            opciones[opcion][1]()
        else:
            print("Opción inválida.")


def _crear():
    u = input("Nombre de usuario: ").strip()
    p = input("Contraseña:        ").strip()
    if u and p:
        add_user(u, p)
    else:
        print("Usuario y contraseña no pueden estar vacíos.")


def _cambiar():
    u = input("Nombre de usuario: ").strip()
    p = input("Nueva contraseña:  ").strip()
    if u and p:
        update_user(u, p)
    else:
        print("Campos requeridos.")


def _eliminar():
    u = input("Nombre de usuario a eliminar: ").strip()
    confirmar = input(f"¿Confirmar eliminar '{u}'? (s/n): ").strip().lower()
    if confirmar == 's':
        delete_user(u)
    else:
        print("Cancelado.")


if __name__ == "__main__":
    menu()
