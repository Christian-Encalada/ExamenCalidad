# Sistema de Gestión de Usuarios y Tareas

Este proyecto es un sistema de gestión de usuarios y tareas, construido con **Flask** para el backend y **Selenium** para las pruebas automatizadas. El sistema permite la creación y gestión de usuarios y tareas, así como la realización de pruebas de funcionalidad para asegurar el correcto funcionamiento de las funcionalidades principales.

## Contenido del Proyecto

- **Backend**: Implementado con Flask, SQLAlchemy y Marshmallow.
- **Frontend**: HTML y CSS básicos para la visualización de la interfaz de usuario.
- **Pruebas**: Automatizadas con Selenium para verificar la funcionalidad del login y el registro de usuarios.

## Instalación

### Prerequisitos

- Python 3.8 o superior
- Pip (gestor de paquetes de Python)
- Navegador web compatible (Chrome, Firefox, etc.)
- WebDriver correspondiente al navegador (por ejemplo, ChromeDriver para Chrome)

### Pasos para la Instalación

1. **Clonar el Repositorio**

   ```bash
   git clone https://github.com/tu_usuario/tu_repositorio.git

2. **Instala dependencias:**

pip install -r requirements.txt


3. **Configurar las Variables de Entorno**

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:12345@localhost:5432/gestion_viajes'

4. **ejecutar:**

python app.py
