// ============================================================
// DIA 7 - Servidor de metricas DORA (para Grafana)
// ============================================================
// Expone las 4 metricas DORA como JSON por HTTP, para que Grafana las
// consuma con el datasource Infinity (lee JSON de una URL).
//
// Sin dependencias: solo Node nativo. Recalcula en cada peticion, asi que
// si editas deployments.json y recargas Grafana, ves los valores nuevos.
//
// Endpoints:
//   GET /metricas  -> objeto con las 4 metricas (frecuencia, lead time, CFR, MTTR)
//   GET /health    -> {"ok":true}
//
// Puerto: 8900 (configurable con PORT).
// ============================================================

const http = require("http");
const { calcularDora } = require("./calcular-dora");

const PORT = process.env.PORT || 8900;

const server = http.createServer((req, res) => {
    res.setHeader("Access-Control-Allow-Origin", "*");       // Grafana lo consume
    res.setHeader("Content-Type", "application/json; charset=utf-8");

    if (req.url === "/health") {
        res.end(JSON.stringify({ ok: true }));
        return;
    }

    if (req.url === "/metricas") {
        try {
            const m = calcularDora();
            // Lo devolvemos como ARRAY de una fila: asi Grafana (Infinity) lo
            // mapea facil a columnas de una tabla/paneles.
            res.end(JSON.stringify([m]));
        } catch (e) {
            res.statusCode = 500;
            res.end(JSON.stringify({ error: e.message }));
        }
        return;
    }

    res.statusCode = 404;
    res.end(JSON.stringify({ error: "usa /metricas o /health" }));
});

server.listen(PORT, "0.0.0.0", () => {
    console.log(`Servidor de metricas DORA en http://0.0.0.0:${PORT}/metricas`);
});
