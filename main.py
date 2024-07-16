from flask import Flask, request, jsonify
from datetime import datetime #Importar librería para determinar la fecha

app = Flask(__name__)

#Definiciones de las clases
class CuentaUsuario:
    def __init__(self, numero, nombre, saldo, numeros_contacto):
        self.numero = numero
        self.nombre = nombre
        self.saldo = saldo
        self.numeros_contacto = numeros_contacto
        self.historial = []

    def historial_operaciones(self):
        return self.historial

    def transferir_dinero(self, destino, valor):
        if destino.numero in self.numeros_contacto and self.saldo >= valor:
            operacion = Operacion(self, destino, valor)
            self.historial.append(operacion)
            destino.historial.append(operacion)
            self.saldo -= valor
            destino.saldo += valor
            return True, operacion
        return False, None

class Operacion:
    def __init__(self, origen, destino, valor):
        self.origen = origen.numero
        self.destino = destino.numero
        self.valor = valor
        self.fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

#Base de datos utilizada: se basó en el ejemplo del documento
BD = [
    CuentaUsuario("21345", "Arnaldo", 200, ["123", "456"]),
    CuentaUsuario("123", "Luisa", 400, ["456"]),
    CuentaUsuario("456", "Andrea", 300, ["21345"])
]

def encontrar_cuenta(numero):
    for cuenta in BD:
        if cuenta.numero == numero:
            return cuenta
    return None

@app.route('/billetera/contactos', methods=['GET'])
def contactos():
    numero = request.args.get('minumero')
    cuenta = encontrar_cuenta(numero)
    if cuenta:
        contactos_info = {contacto: encontrar_cuenta(contacto).nombre for contacto in cuenta.numeros_contacto}
        return jsonify(contactos_info), 200
    else:
        return jsonify({"error": "Cuenta not found"}), 404

@app.route('/billetera/pagar', methods=['POST'])
def pagar():
    numero_origen = request.args.get('minumero')
    numero_destino = request.args.get('numerodestino')
    valor = float(request.args.get('valor'))

    cuenta_origen = encontrar_cuenta(numero_origen)
    cuenta_destino = encontrar_cuenta(numero_destino)

    if not cuenta_origen or not cuenta_destino:
        return jsonify({"error": "Cuenta not found"}), 404

    success, operacion = cuenta_origen.transferir_dinero(cuenta_destino, valor)
    if success:
        return jsonify({"message": "Se realizó la transferencia", "fecha": operacion.fecha}), 200
    else:
        return jsonify({"error": "Error en realizar la transferencia"}), 400

@app.route('/billetera/historial', methods=['GET'])
def historial():
    numero = request.args.get('minumero')
    cuenta = encontrar_cuenta(numero)
    if cuenta:
        historial = [{"origen": op.origen, "destino": op.destino, "valor": op.valor, "fecha": op.fecha} for op in cuenta.historial_operaciones()]
        return jsonify({"saldo": cuenta.saldo, "historial": historial}), 200
    else:
        return jsonify({"error": "Cuenta not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
