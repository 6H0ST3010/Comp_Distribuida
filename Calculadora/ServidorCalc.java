#ClienteCalc.py

import sys, getopt
import socket
import json
import struct

DefaultHostName = "localhost"
DefaultPort = 12349
DefaultOperation = "+"
DefaultOperand1 = "5"
DefaultOperand2 = "3"
DebugMessages = False

class ComplexNumber:
    """Classe para números complexos"""
    def __init__(self, real, imag):
        self.real = real
        self.imag = imag
    
    def to_dict(self):
        return {"real": self.real, "imag": self.imag}
    
    @staticmethod
    def from_dict(data):
        return ComplexNumber(data["real"], data["imag"])
    
    @staticmethod
    def from_string(s):
        s = s.replace(' ', '').lower()
        
        if 'i' not in s:
            try:
                return ComplexNumber(float(s), 0)
            except:
                raise ValueError(f"Formato inválido: {s}")
        
        s = s.replace('i', '')
        
        if s == '':
            return ComplexNumber(0, 1)
        if s == '-':
            return ComplexNumber(0, -1)
        
        if '+' in s:
            real_str, imag_str = s.split('+')
            real = float(real_str) if real_str else 0
            imag = float(imag_str) if imag_str else 1
        elif '-' in s:
            if s[0] == '-':
                parts = s[1:].split('-')
                if len(parts) > 1:
                    real_str = '-' + parts[0]
                    imag_str = '-' + parts[1]
                else:
                    real_str = '-' + parts[0]
                    imag_str = ''
                real = float(real_str) if real_str else 0
                imag = float(imag_str) if imag_str else -1
            else:
                parts = s.split('-')
                real_str = parts[0]
                imag_str = '-' + parts[1] if len(parts) > 1 else ''
                real = float(real_str) if real_str else 0
                imag = float(imag_str) if imag_str else -1
        else:
            return ComplexNumber(0, float(s))
        
        return ComplexNumber(real, imag)
    
    def __str__(self):
        if self.imag == 0:
            return str(self.real)
        elif self.real == 0:
            return f"{self.imag}i"
        elif self.imag > 0:
            return f"{self.real} + {self.imag}i"
        else:
            return f"{self.real} - {abs(self.imag)}i"

def send_request(hostName, portNumber, request):
    print("Connecting to {} at port {}".format(hostName, portNumber))
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((hostName, portNumber))
        
        request_text = json.dumps(request)
        request_bytes = request_text.encode('utf-8')
        
        if DebugMessages:
            print("Sending: {}".format(request_text))
        
        s.sendall(struct.pack("!I", len(request_bytes)))
        s.sendall(request_bytes)
        
        size_data = s.recv(4)
        if not size_data:
            raise Exception("No response from server")
        
        response_size = struct.unpack("!I", size_data)[0]
        
        response_data = b""
        while len(response_data) < response_size:
            chunk = s.recv(min(1024, response_size - len(response_data)))
            if not chunk:
                raise Exception("Incomplete response")
            response_data += chunk
        
        response = json.loads(response_data.decode('utf-8'))
        
        if DebugMessages:
            print("Received: {}".format(response))
        
        return response

def display_result(response):
    if response.get("status") == "success":
        result = response.get("result")
        op = response.get("operation")
        op1 = response.get("operand1")
        op2 = response.get("operand2")
        
        def format_operand(op):
            if isinstance(op, dict):
                if "real" in op and "imag" in op:
                    c = ComplexNumber.from_dict(op)
                    return str(c)
            return str(op)
        
        op1_str = format_operand(op1)
        op2_str = format_operand(op2)
        
        if result.get("type") == "complex":
            if "value" in result:
                c = ComplexNumber.from_dict(result["value"])
                result_str = str(c)
            else:
                result_str = result.get("display", str(result))
        else:
            result_str = str(result["value"])
        
        print("\n" + "=" * 50)
        print("Resultado: {} {} {} = {}".format(op1_str, op, op2_str, result_str))
        print("=" * 50 + "\n")
    
    else:
        print("\n" + "=" * 50)
        print("ERRO: {}".format(response.get('message', 'Unknown error')))
        print("=" * 50 + "\n")

def parse_operand(s):
    try:
        if '.' in s:
            return float(s)
        else:
            try:
                return int(s)
            except:
                c = ComplexNumber.from_string(s)
                return c.to_dict()
    except ValueError:
        c = ComplexNumber.from_string(s)
        return c.to_dict()

def startClient(hostName, portNumber, operand1_str, operator, operand2_str):
    print("Starting client for {} at port {}".format(hostName, portNumber))
    
    try:
        operand1 = parse_operand(operand1_str)
        operand2 = parse_operand(operand2_str)
        
        request = {
            "operation": operator,
            "operand1": operand1,
            "operand2": operand2
        }
        
        response = send_request(hostName, portNumber, request)
        display_result(response)
    
    except Exception as e:
        print("Error: {}".format(e))
        sys.exit(1)

def usage():
    print("ClienteCalc.py [--port <server port number>] [--name <server name>] [--debug] <operando1> <operador> <operando2>")
    print("\nOperações suportadas:")
    print("  Soma: +")
    print("  Subtração: -")
    print("  Multiplicação: *")
    print("\nExemplos:")
    print("  python ClienteCalc.py 5 + 3")
    print("  python ClienteCalc.py '3+2i' + '1-4i'")

def parseArguments(argv):
    print("Parsing arguments...")
    global DebugMessages
    
    try:
        opts, args = getopt.getopt(argv, "h", ["help", "port=", "name=", "debug"])
    except getopt.GetoptError as err:
        print(err)
        sys.exit(2)
    
    hostPort = DefaultPort
    hostName = DefaultHostName
    
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("--port"):
            hostPort = int(arg)
        elif opt in ("--name"):
            hostName = arg
        elif opt in ("--debug"):
            DebugMessages = True
            print("Debug messages active.")
    
    if len(args) != 3:
        print("Error: Need 3 arguments: <operand1> <operator> <operand2>")
        print("Example: python ClienteCalc.py 5 + 3")
        print("Example: python ClienteCalc.py '3+2i' + '1-4i'")
        usage()
        sys.exit(1)
    
    operand1_str = args[0]
    operator = args[1]
    operand2_str = args[2]
    
    if operator not in ['+', '-', '*']:
        print("Error: Operator '{}' not supported. Use +, - or *".format(operator))
        sys.exit(1)
    
    startClient(hostName, hostPort, operand1_str, operator, operand2_str)

if __name__ == "__main__":
    parseArguments(sys.argv[1:])