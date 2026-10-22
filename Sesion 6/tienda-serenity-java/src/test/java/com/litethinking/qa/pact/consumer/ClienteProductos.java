package com.litethinking.qa.pact.consumer;

import org.apache.hc.client5.http.classic.methods.HttpGet;
import org.apache.hc.client5.http.impl.classic.CloseableHttpClient;
import org.apache.hc.client5.http.impl.classic.HttpClients;
import org.apache.hc.core5.http.io.entity.EntityUtils;

/**
 * CONSUMER — cliente HTTP minimo del servicio de Notificaciones.
 *
 * Su unica dependencia con la Tienda es la FORMA de la respuesta de
 * GET /api/productos/:id (necesita id, nombre y precio). Esa expectativa es el
 * contrato que Pact va a asegurar. El consumer NO sabe como esta hecha la API
 * por dentro.
 */
public class ClienteProductos {

    private final String baseUrl;

    public ClienteProductos(String baseUrl) {
        this.baseUrl = baseUrl.endsWith("/") ? baseUrl.substring(0, baseUrl.length() - 1) : baseUrl;
    }

    /** GET /api/productos/:id -> cuerpo JSON como String. Lanza si no es 200. */
    public String obtenerProductoJson(int id) throws Exception {
        try (CloseableHttpClient http = HttpClients.createDefault()) {
            HttpGet get = new HttpGet(baseUrl + "/api/productos/" + id);
            return http.execute(get, response -> {
                int status = response.getCode();
                String body = EntityUtils.toString(response.getEntity());
                if (status != 200) {
                    throw new RuntimeException("Esperaba 200 y vino " + status + ": " + body);
                }
                return body;
            });
        }
    }
}
