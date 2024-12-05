import flet as ft
from peewee import *

# Configurar la base de datos SQLite
db = SqliteDatabase('usuarios.db')

# Definir modelo de usuario
class Usuario(Model):
    id = AutoField()
    nombre = CharField()
    edad = IntegerField()
    sexo = CharField()

    class Meta:
        database = db

# Crear la tabla si no existe
db.connect()
db.create_tables([Usuario])

def main(page: ft.Page):
    page.title = "Gestión de Usuarios"
    page.scroll = "auto"

    # Input fields
    nombre = ft.TextField(label="Nombre", width=300)
    edad = ft.TextField(label="Edad", width=300, keyboard_type="number")
    sexo = ft.Dropdown(
        label="Sexo",
        options=[
            ft.dropdown.Option("Masculino"),
            ft.dropdown.Option("Femenino"),
        ],
        width=300,
    )

    # Feedback
    feedback = ft.Text(value="", color="green")

    # Tabla para mostrar usuarios
    usuarios_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Nombre")),
            ft.DataColumn(ft.Text("Edad")),
            ft.DataColumn(ft.Text("Sexo")),
            ft.DataColumn(ft.Text("Acciones")),
        ],
        rows=[],
    )

    # Función para cargar usuarios desde SQLite
    def cargar_usuarios():
        try:
            usuarios_table.rows.clear()
            for user in Usuario.select():
                usuarios_table.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(str(user.id))),
                            ft.DataCell(ft.Text(user.nombre)),
                            ft.DataCell(ft.Text(str(user.edad))),
                            ft.DataCell(ft.Text(user.sexo)),
                            ft.DataCell(
                                ft.Row(
                                    [
                                        ft.IconButton(
                                            icon=ft.icons.EDIT,
                                            on_click=lambda e, user=user: editar_usuario(user),
                                        ),
                                        ft.IconButton(
                                            icon=ft.icons.DELETE,
                                            on_click=lambda e, user=user: eliminar_usuario(user),
                                        ),
                                    ]
                                )
                            ),
                        ]
                    )
                )
            feedback.value = "Usuarios cargados correctamente."
            feedback.color = "green"
        except Exception as ex:
            feedback.value = f"Error al cargar usuarios: {str(ex)}"
            feedback.color = "red"
        page.update()

    # Función para agregar usuario
    def agregar_usuario(e):
        if not nombre.value or not edad.value or not sexo.value:
            feedback.value = "Todos los campos son obligatorios."
            feedback.color = "red"
            page.update()
            return

        try:
            Usuario.create(nombre=nombre.value, edad=int(edad.value), sexo=sexo.value)
            feedback.value = "Usuario agregado correctamente."
            feedback.color = "green"
            nombre.value = ""
            edad.value = ""
            sexo.value = None
            cargar_usuarios()
        except Exception as ex:
            feedback.value = f"Error al agregar usuario: {str(ex)}"
            feedback.color = "red"
        page.update()

    # Función para eliminar usuario
    def eliminar_usuario(user):
        try:
            Usuario.delete_by_id(user.id)
            feedback.value = f"Usuario con ID {user.id} eliminado correctamente."
            feedback.color = "green"
            cargar_usuarios()
        except Exception as ex:
            feedback.value = f"Error al eliminar usuario: {str(ex)}"
            feedback.color = "red"
        page.update()

    # Función para editar usuario
    def editar_usuario(user):
        nombre.value = user.nombre
        edad.value = str(user.edad)
        sexo.value = user.sexo

        # Reemplazar el botón de agregar con el botón de actualizar
        def actualizar_usuario(e):
            try:
                user.nombre = nombre.value
                user.edad = int(edad.value)
                user.sexo = sexo.value
                user.save()
                feedback.value = f"Usuario con ID {user.id} actualizado correctamente."
                feedback.color = "green"
                nombre.value = ""
                edad.value = ""
                sexo.value = None
                agregar_button.text = "Agregar Usuario"
                agregar_button.on_click = agregar_usuario
                cargar_usuarios()
            except Exception as ex:
                feedback.value = f"Error al actualizar usuario: {str(ex)}"
                feedback.color = "red"
            page.update()

        agregar_button.text = "Actualizar Usuario"
        agregar_button.on_click = actualizar_usuario
        page.update()

    # Botón para agregar o actualizar usuario
    agregar_button = ft.ElevatedButton("Agregar Usuario", on_click=agregar_usuario)

    # Agregar componentes a la página
    page.add(
        ft.Column(
            [
                ft.Text("Registro de Usuarios", size=24, weight="bold"),
                nombre,
                edad,
                sexo,
                agregar_button,
                feedback,
                ft.Text("Usuarios Registrados", size=20, weight="bold"),
                usuarios_table,
            ],
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )

    # Cargar usuarios al inicio
    cargar_usuarios()

# Ejecutar la app
if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.WEB_BROWSER)
