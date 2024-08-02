import unittest
from app import app, db, Usuarios, Temas, Respuestas, Transaccion, Factura

class TestApp(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_registro_usuario(self):
        response = self.app.post('/registro', data=dict(
            username='testuser',
            email='test@example.com',
            password='password123'
        ), follow_redirects=True)
        self.assertIn(b'Registro exitoso', response.data)

    def test_login_usuario(self):
        usuario = Usuarios(nombre_usuario='testuser', email='test@example.com', contraseña='password123')
        db.session.add(usuario)
        db.session.commit()

        response = self.app.post('/login', data=dict(
            username='testuser',
            password='password123'
        ), follow_redirects=True)
        self.assertIn(b'Inicio de sesión exitoso', response.data)

    def test_realizar_pago(self):
        usuario = Usuarios(nombre_usuario='testuser', email='test@example.com', contraseña='password123')
        db.session.add(usuario)
        db.session.commit()
        with self.app:
            self.app.post('/login', data=dict(
                username='testuser',
                password='password123'
            ), follow_redirects=True)
            response = self.app.post('/pago', data=dict(
                monto='10.00'
            ), follow_redirects=True)
            self.assertIn(b'Pago realizado con éxito', response.data)

if __name__ == '__main__':
    unittest.main()
