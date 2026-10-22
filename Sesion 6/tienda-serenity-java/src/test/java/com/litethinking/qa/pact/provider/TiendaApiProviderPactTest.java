package com.litethinking.qa.pact.provider;

import au.com.dius.pact.provider.junit5.HttpTestTarget;
import au.com.dius.pact.provider.junit5.PactVerificationContext;
import au.com.dius.pact.provider.junit5.PactVerificationInvocationContextProvider;
import au.com.dius.pact.provider.junitsupport.Provider;
import au.com.dius.pact.provider.junitsupport.State;
import au.com.dius.pact.provider.junitsupport.loader.PactFolder;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.TestTemplate;
import org.junit.jupiter.api.extension.ExtendWith;

import java.net.URI;
import java.net.URL;

/**
 * PROVIDER side de Pact (servicio 'tienda-api').
 *
 * Toma el contrato que genero el consumer (build/pacts/) y lo verifica contra
 * el PROVIDER REAL corriendo (la app-tienda en contenedor). Para cada
 * interaccion hace la peticion real y comprueba que la respuesta CUMPLE la
 * forma que el consumer declaro.
 *
 * Si la API cambiara su respuesta (ej. renombrar 'precio'), esta verificacion
 * FALLA: contract testing atrapando una ruptura antes de produccion.
 *
 * URL del provider: -Dprovider.base.url=http://localhost:3000 (o app-tienda:3000)
 * Carpeta de pacts: -Dpact.rootDir=build/pacts
 */
@Provider("tienda-api")
@PactFolder("build/pacts")
@ExtendWith(PactVerificationInvocationContextProvider.class)
public class TiendaApiProviderPactTest {

    @BeforeEach
    void destino(PactVerificationContext context) throws Exception {
        String base = System.getProperty("provider.base.url",
                System.getenv().getOrDefault("PROVIDER_BASE_URL", "http://localhost:3000"));
        URL url = URI.create(base).toURL();
        int port = url.getPort() != -1 ? url.getPort() : (url.getProtocol().equals("https") ? 443 : 80);
        context.setTarget(new HttpTestTarget(url.getHost(), port, "/"));
    }

    @TestTemplate
    void verificarContrato(PactVerificationContext context) {
        context.verifyInteraction();
    }

    // Provider state declarado por el consumer. Como los datos son
    // deterministas (semilla fija), no hay que sembrar nada; basta con
    // reconocer el estado para que la verificacion sea robusta.
    @State("existe el producto 1")
    void existeElProducto1() {
        // no-op: el producto 1 siempre existe (semilla fija).
    }
}
