//ClienteCalc.java

import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.net.Socket;
import java.nio.charset.StandardCharsets;

public class ClienteCalc {

    static final String DEFAULT_HOST = "localhost";
    static final int DEFAULT_PORT = 12349;
    static boolean debugMessages = false;

    static class ComplexNumber {
        double real;
        double imag;

        ComplexNumber(double real, double imag) {
            this.real = real;
            this.imag = imag;
        }

        String toMessage() {
            return "{\"real\":" + formatNumber(real) + ",\"imag\":" + formatNumber(imag) + "}";
        }

        static ComplexNumber fromString(String s) {
            String text = s.replace(" ", "").toLowerCase();

            if (!text.contains("i")) {
                double real = Double.parseDouble(text);
                return new ComplexNumber(real, 0);
            }

            text = text.replace("i", "");

            if (text.equals("")) return new ComplexNumber(0, 1);
            if (text.equals("+")) return new ComplexNumber(0, 1);
            if (text.equals("-")) return new ComplexNumber(0, -1);

            int splitPos = -1;
            for (int i = 1; i < text.length(); i++) {
                char c = text.charAt(i);
                if (c == '+' || c == '-') {
                    splitPos = i;
                }
            }

            if (splitPos == -1) {
                double imag = Double.parseDouble(text);
                return new ComplexNumber(0, imag);
            }

            String realPart = text.substring(0, splitPos);
            String imagPart = text.substring(splitPos);

            double real = Double.parseDouble(realPart);
            double imag;

            if (imagPart.equals("+") || imagPart.equals("")) {
                imag = 1;
            } else if (imagPart.equals("-")) {
                imag = -1;
            } else {
                imag = Double.parseDouble(imagPart);
            }

            return new ComplexNumber(real, imag);
        }

        @Override
        public String toString() {
            if (imag == 0) {
                return formatNumber(real);
            } else if (real == 0) {
                return formatNumber(imag) + "i";
            } else if (imag > 0) {
                return formatNumber(real) + " + " + formatNumber(imag) + "i";
            } else {
                return formatNumber(real) + " - " + formatNumber(Math.abs(imag)) + "i";
            }
        }
    }

    static class ParsedOperand {
        boolean isComplex;
        int intValue;
        double doubleValue;
        ComplexNumber complexValue;
        boolean isInteger;
    }

    static String formatNumber(double n) {
        if (n == Math.rint(n)) {
            return String.valueOf((long) n);
        }
        return String.valueOf(n);
    }

    static ParsedOperand parseOperand(String s) {
        ParsedOperand result = new ParsedOperand();

        try {
            if (!s.contains("i")) {
                if (s.contains(".")) {
                    result.isComplex = false;
                    result.isInteger = false;
                    result.doubleValue = Double.parseDouble(s);
                    return result;
                } else {
                    result.isComplex = false;
                    result.isInteger = true;
                    result.intValue = Integer.parseInt(s);
                    return result;
                }
            }
        } catch (NumberFormatException ignored) {
        }

        result.isComplex = true;
        result.complexValue = ComplexNumber.fromString(s);
        return result;
    }

    static String operandToMessage(ParsedOperand operand) {
        if (operand.isComplex) {
            return operand.complexValue.toMessage();
        }
        if (operand.isInteger) {
            return String.valueOf(operand.intValue);
        }
        return formatNumber(operand.doubleValue);
    }

    static String buildRequest(String operand1, String operation, String operand2) {
        ParsedOperand op1 = parseOperand(operand1);
        ParsedOperand op2 = parseOperand(operand2);

        return "{"
                + "\"operation\":\"" + escapeText(operation) + "\","
                + "\"operand1\":" + operandToMessage(op1) + ","
                + "\"operand2\":" + operandToMessage(op2)
                + "}";
    }

    static String escapeText(String s) {
        return s.replace("\\", "\\\\").replace("\"", "\\\"");
    }

    static String sendRequest(String host, int port, String requestText) throws IOException {
        try (Socket socket = new Socket(host, port)) {
            DataOutputStream out = new DataOutputStream(socket.getOutputStream());
            DataInputStream in = new DataInputStream(socket.getInputStream());

            byte[] requestBytes = requestText.getBytes(StandardCharsets.UTF_8);

            if (debugMessages) {
                System.out.println("Sending: " + requestText);
            }

            out.writeInt(requestBytes.length);
            out.write(requestBytes);
            out.flush();

            int responseSize = in.readInt();
            byte[] responseBytes = new byte[responseSize];
            in.readFully(responseBytes);

            String responseText = new String(responseBytes, StandardCharsets.UTF_8);

            if (debugMessages) {
                System.out.println("Received: " + responseText);
            }

            return responseText;
        }
    }

   static void displayResult(String responseText) {
    System.out.println("\n==================================================");

    if (responseText.contains("\"status\": \"success\"") || responseText.contains("\"status\":\"success\"")) {
        String resultDisplay = extractStringField(responseText, "display");
        if (resultDisplay != null) {
            System.out.println("Resultado: " + resultDisplay);
        } else {
            System.out.println("Resposta: " + responseText);
        }
    } else {
        String message = extractStringField(responseText, "message");
        if (message != null) {
            System.out.println("ERRO: " + message);
        } else {
            System.out.println("ERRO: " + responseText);
        }
    }

    System.out.println("==================================================\n");
}

static String extractStringField(String text, String fieldName) {
    int pos = text.indexOf("\"" + fieldName + "\"");
    if (pos == -1) return null;

    pos = text.indexOf(":", pos);
    if (pos == -1) return null;

    pos++;
    while (pos < text.length() && Character.isWhitespace(text.charAt(pos))) {
        pos++;
    }

    if (pos >= text.length() || text.charAt(pos) != '"') return null;
    pos++;

    StringBuilder sb = new StringBuilder();
    boolean escaping = false;

    while (pos < text.length()) {
        char c = text.charAt(pos);

        if (escaping) {
            sb.append(c);
            escaping = false;
        } else if (c == '\\') {
            escaping = true;
        } else if (c == '"') {
            return sb.toString();
        } else {
            sb.append(c);
        }

        pos++;
    }

    return null;
}

    static void usage() {
        System.out.println("ClienteCalc.java [--port <server port>] [--name <server name>] [--debug] <operando1> <operador> <operando2>");
        System.out.println();
        System.out.println("Operações suportadas:");
        System.out.println("  Soma: +");
        System.out.println("  Subtração: -");
        System.out.println("  Multiplicação: *");
        System.out.println();
        System.out.println("Números complexos podem ser representados como:");
        System.out.println("  \"3+2i\", \"3-2i\", \"-3+2i\", \"-3-2i\", \"5i\"");
        System.out.println("Ou números reais simples:");
        System.out.println("  \"5\", \"3.14\"");
        System.out.println();
        System.out.println("Exemplos:");
        System.out.println("  java ClienteCalc 5 + 3");
        System.out.println("  java ClienteCalc \"3+2i\" + \"1-4i\"");
        System.out.println("  java ClienteCalc --port 12350 10 - 4");
        System.out.println("  java ClienteCalc \"2+3i\" * \"4-1i\"");
    }

    public static void main(String[] args) {
        String host = DEFAULT_HOST;
        int port = DEFAULT_PORT;

        int i = 0;
        while (i < args.length && args[i].startsWith("--")) {
            switch (args[i]) {
                case "--help":
                    usage();
                    return;
                case "--debug":
                    debugMessages = true;
                    i++;
                    break;
                case "--port":
                    if (i + 1 >= args.length) {
                        System.out.println("Missing value for --port");
                        return;
                    }
                    port = Integer.parseInt(args[i + 1]);
                    i += 2;
                    break;
                case "--name":
                    if (i + 1 >= args.length) {
                        System.out.println("Missing value for --name");
                        return;
                    }
                    host = args[i + 1];
                    i += 2;
                    break;
                default:
                    System.out.println("Unknown option: " + args[i]);
                    usage();
                    return;
            }
        }

        if (args.length - i != 3) {
            System.out.println("Error: Need 3 arguments: <operand1> <operator> <operand2>");
            usage();
            return;
        }

        String operand1 = args[i];
        String operator = args[i + 1];
        String operand2 = args[i + 2];

        if (!operator.equals("+") && !operator.equals("-") && !operator.equals("*")) {
            System.out.println("Error: Operator '" + operator + "' not supported. Use +, - or *");
            return;
        }

        try {
            System.out.println("Starting client for " + host + " at port " + port);
            System.out.println("Connecting to " + host + " at port " + port);

            String requestText = buildRequest(operand1, operator, operand2);
            String responseText = sendRequest(host, port, requestText);
            displayResult(responseText);

        } catch (Exception e) {
            System.out.println("Error: " + e.getMessage());
            e.printStackTrace();
        }
    }
}