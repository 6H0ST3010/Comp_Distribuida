import java.io.*;
import java.net.ServerSocket;
import java.net.Socket;
import java.nio.charset.StandardCharsets;

public class ServidorCalc {

    static final int DEFAULT_PORT = 12349;
    static boolean debugMessages = false;

    public static void main(String[] args) {
        int port = DEFAULT_PORT;

        for (int i = 0; i < args.length; i++) {
            if (args[i].equals("--port") && i + 1 < args.length) {
                port = Integer.parseInt(args[i + 1]);
                i++;
            }
            if (args[i].equals("--debug")) {
                debugMessages = true;
            }
        }

        startServer(port);
    }

    static void startServer(int port) {
        System.out.println("Starting server on port " + port);

        try (ServerSocket serverSocket = new ServerSocket(port)) {

            while (true) {
                Socket client = serverSocket.accept();
                System.out.println("New connection: " + client.getInetAddress());

                new Thread(() -> handleClient(client)).start();
            }

        } catch (IOException e) {
            System.out.println("Server error: " + e.getMessage());
        }
    }

    static void handleClient(Socket client) {
        try (DataInputStream in = new DataInputStream(client.getInputStream());
             DataOutputStream out = new DataOutputStream(client.getOutputStream())) {

            while (true) {
                // ler tamanho
                int size;
                try {
                    size = in.readInt();
                } catch (EOFException e) {
                    break;
                }

                byte[] data = new byte[size];
                in.readFully(data);

                String request = new String(data, StandardCharsets.UTF_8);

                if (debugMessages) {
                    System.out.println("Received: " + request);
                }

                String response = processRequest(request);

                byte[] responseBytes = response.getBytes(StandardCharsets.UTF_8);

                out.writeInt(responseBytes.length);
                out.write(responseBytes);
                out.flush();

                if (debugMessages) {
                    System.out.println("Sent: " + response);
                }
            }

        } catch (IOException e) {
            System.out.println("Client error: " + e.getMessage());
        }
    }

    static String processRequest(String json) {
        try {
            String op = extractString(json, "operation");
            String op1 = extractValue(json, "operand1");
            String op2 = extractValue(json, "operand2");

            if (op == null || op1 == null || op2 == null) {
                return error("Missing fields");
            }

            boolean isComplex = op1.contains("real") || op2.contains("real");

            if (isComplex) {
                Complex c1 = parseComplex(op1);
                Complex c2 = parseComplex(op2);

                Complex result;

                switch (op) {
                    case "+":
                        result = c1.add(c2);
                        break;
                    case "-":
                        result = c1.sub(c2);
                        break;
                    case "*":
                        result = c1.mul(c2);
                        break;
                    default:
                        return error("Operação inválida");
                }

                return "{"
                        + "\"status\":\"success\","
                        + "\"result\":{"
                        + "\"type\":\"complex\","
                        + "\"value\":{"
                        + "\"real\":" + result.real + ","
                        + "\"imag\":" + result.imag
                        + "},"
                        + "\"display\":\"" + result + "\""
                        + "}"
                        + "}";

            } else {
                double n1 = Double.parseDouble(op1);
                double n2 = Double.parseDouble(op2);
                double result;

                switch (op) {
                    case "+":
                        result = n1 + n2;
                        break;
                    case "-":
                        result = n1 - n2;
                        break;
                    case "*":
                        result = n1 * n2;
                        break;
                    default:
                        return error("Operação inválida");
                }

                return "{"
                        + "\"status\":\"success\","
                        + "\"result\":{"
                        + "\"type\":\"real\","
                        + "\"value\":" + result + ","
                        + "\"display\":\"" + result + "\""
                        + "}"
                        + "}";
            }

        } catch (Exception e) {
            return error("Erro: " + e.getMessage());
        }
    }

    static String error(String msg) {
        return "{ \"status\":\"error\", \"message\":\"" + msg + "\" }";
    }


    static String extractString(String json, String field) {
        String key = "\"" + field + "\"";
        int i = json.indexOf(key);
        if (i == -1) return null;

        i = json.indexOf(":", i) + 1;

        while (json.charAt(i) == ' ') i++;

        if (json.charAt(i) != '"') return null;
        i++;

        int end = json.indexOf("\"", i);
        return json.substring(i, end);
    }

    static String extractValue(String json, String field) {
        String key = "\"" + field + "\"";
        int i = json.indexOf(key);
        if (i == -1) return null;

        i = json.indexOf(":", i) + 1;

        while (json.charAt(i) == ' ') i++;

        if (json.charAt(i) == '{') {
            int braces = 1;
            int j = i + 1;
            while (braces > 0) {
                if (json.charAt(j) == '{') braces++;
                if (json.charAt(j) == '}') braces--;
                j++;
            }
            return json.substring(i, j);
        } else {
            int j = i;
            while (j < json.length() && ",}".indexOf(json.charAt(j)) == -1) j++;
            return json.substring(i, j).trim();
        }
    }

    // numeros complexos

    static class Complex {
        double real, imag;

        Complex(double r, double i) {
            real = r;
            imag = i;
        }

        Complex add(Complex o) {
            return new Complex(real + o.real, imag + o.imag);
        }

        Complex sub(Complex o) {
            return new Complex(real - o.real, imag - o.imag);
        }

        Complex mul(Complex o) {
            return new Complex(
                    real * o.real - imag * o.imag,
                    real * o.imag + imag * o.real
            );
        }

        public String toString() {
            if (imag >= 0) return real + " + " + imag + "i";
            return real + " - " + Math.abs(imag) + "i";
        }
    }

    static Complex parseComplex(String json) {
        double real = Double.parseDouble(extractValue(json, "real"));
        double imag = Double.parseDouble(extractValue(json, "imag"));
        return new Complex(real, imag);
    }
}