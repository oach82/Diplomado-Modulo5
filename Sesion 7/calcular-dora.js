// ============================================================
// DIA 7 - Calculadora de metricas DORA (Node, sin dependencias)
// ============================================================
// Lee un historial de despliegues (deployments.json) y calcula las 4
// metricas DORA sobre una ventana de tiempo. Es la version "a mano" de lo
// que hacen herramientas como DORA dashboards, Sleuth o LinearB.
//
// Uso como CLI (imprime el reporte):
//   podman run --rm dora
// Uso como modulo (lo importa el servidor de metricas para Grafana):
//   const { calcularDora } = require('./calcular-dora');
// ============================================================

const fs = require("fs");
const path = require("path");

const ARCHIVO = process.env.DEPLOYMENTS_FILE || path.join(__dirname, "deployments.json");

// ------------------------------------------------------------
// Clasificacion segun los niveles de referencia DORA
// ------------------------------------------------------------
function nivelFrecuencia(porDia) {
    if (porDia >= 1) return "Elite";
    if (porDia >= 1 / 7) return "Alto";      // al menos 1/semana
    if (porDia >= 1 / 30) return "Medio";    // al menos 1/mes
    return "Bajo";
}
function nivelLeadTime(horas) {
    if (horas < 24) return "Elite";
    if (horas < 24 * 7) return "Alto";
    if (horas < 24 * 30) return "Medio";
    return "Bajo";
}
function nivelCFR(pct) {
    if (pct <= 15) return "Elite";
    if (pct <= 30) return "Alto";
    return "Bajo";
}
function nivelMTTR(horas) {
    if (horas < 1) return "Elite";
    if (horas < 24) return "Alto";
    if (horas < 24 * 7) return "Medio";
    return "Bajo";
}

function horasEntre(a, b) {
    return (new Date(b) - new Date(a)) / 1000 / 60 / 60;
}

// ------------------------------------------------------------
// Calculo puro: recibe la ruta del JSON de deployments y devuelve
// un objeto con las 4 metricas DORA + su nivel. Reutilizable por el
// servidor de metricas (Grafana) y por el CLI.
// ------------------------------------------------------------
function calcularDora(archivo = ARCHIVO) {
    const deployments = JSON.parse(fs.readFileSync(archivo, "utf8"));
    if (!Array.isArray(deployments) || deployments.length === 0) {
        throw new Error("deployments.json debe ser una lista con al menos un despliegue.");
    }

    deployments.sort((a, b) => new Date(a.deployed_at) - new Date(b.deployed_at));

    const primero = new Date(deployments[0].deployed_at);
    const ultimo = new Date(deployments[deployments.length - 1].deployed_at);
    const diasVentana = Math.max(1, (ultimo - primero) / 1000 / 60 / 60 / 24);

    const totalDeploys = deployments.length;
    const frecuenciaPorDia = totalDeploys / diasVentana;

    const leadTimes = deployments
        .filter((d) => d.committed_at && d.deployed_at)
        .map((d) => horasEntre(d.committed_at, d.deployed_at));
    const leadTimeProm = leadTimes.reduce((s, x) => s + x, 0) / (leadTimes.length || 1);

    const fallidos = deployments.filter((d) => d.failed === true).length;
    const cfr = (fallidos / totalDeploys) * 100;

    const recuperaciones = deployments
        .filter((d) => d.failed === true && d.restored_at && d.deployed_at)
        .map((d) => horasEntre(d.deployed_at, d.restored_at));
    const mttr = recuperaciones.length
        ? recuperaciones.reduce((s, x) => s + x, 0) / recuperaciones.length
        : 0;

    return {
        ventana_dias: Number(diasVentana.toFixed(1)),
        total_deploys: totalDeploys,
        deploys_fallidos: fallidos,
        // Las 4 metricas DORA (valor numerico + nivel de rendimiento)
        frecuencia_deploy_por_dia: Number(frecuenciaPorDia.toFixed(2)),
        frecuencia_nivel: nivelFrecuencia(frecuenciaPorDia),
        lead_time_horas: Number(leadTimeProm.toFixed(1)),
        lead_time_nivel: nivelLeadTime(leadTimeProm),
        change_failure_rate_pct: Number(cfr.toFixed(1)),
        change_failure_rate_nivel: nivelCFR(cfr),
        mttr_horas: Number(mttr.toFixed(1)),
        mttr_nivel: nivelMTTR(mttr),
    };
}

// ------------------------------------------------------------
// CLI: imprime el reporte por consola
// ------------------------------------------------------------
function reporteConsola() {
    if (!fs.existsSync(ARCHIVO)) {
        console.error(`ERROR: no se encontro ${ARCHIVO}.`);
        process.exit(1);
    }
    let m;
    try {
        m = calcularDora(ARCHIVO);
    } catch (e) {
        console.error("ERROR:", e.message);
        process.exit(1);
    }

    const linea = "=".repeat(60);
    console.log(linea);
    console.log("  METRICAS DORA - app Tienda");
    console.log(`  Ventana: ${m.ventana_dias} dias | ${m.total_deploys} despliegues`);
    console.log(linea);
    console.log(`\n1) Frecuencia de despliegue : ${m.frecuencia_deploy_por_dia} deploys/dia  [${m.frecuencia_nivel}]`);
    console.log(`2) Lead time for changes    : ${m.lead_time_horas} h promedio       [${m.lead_time_nivel}]`);
    console.log(`3) Change failure rate      : ${m.change_failure_rate_pct}%  (${m.deploys_fallidos}/${m.total_deploys})        [${m.change_failure_rate_nivel}]`);
    console.log(`4) MTTR                      : ${m.mttr_horas} h promedio       [${m.mttr_nivel}]`);
    console.log(`\n${linea}`);
    console.log("  Lectura: 1-2 miden VELOCIDAD, 3-4 miden ESTABILIDAD.");
    console.log("  Un equipo sano mejora las cuatro a la vez, no una a costa de otra.");
    console.log(linea);
}

module.exports = { calcularDora };

// Si se ejecuta directo (node calcular-dora.js), corre el reporte CLI.
if (require.main === module) {
    reporteConsola();
}
