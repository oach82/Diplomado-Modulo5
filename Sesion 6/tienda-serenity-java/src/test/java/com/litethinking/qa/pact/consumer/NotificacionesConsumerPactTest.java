package com.litethinking.qa.pact.consumer;

import au.com.dius.pact.consumer.MockServer;
import au.com.dius.pact.consumer.dsl.PactDslJsonBody;
import au.com.dius.pact.consumer.dsl.PactDslWithProvider;
import au.com.dius.pact.consumer.junit5.PactConsumerTestExt;
import au.com.dius.pact.consumer.junit5.PactTestFor;
import au.com.dius.pact.core.model.PactSpecVersion;
import au.com.dius.pact.core.model.RequestResponsePact;
import au.com.dius.pact.core.model.annotations.Pact;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * CONSUMER side de Pact (servicio 'notificaciones').
 *
 * Declara el CONTRATO: "cuando pida GET /api/productos/1, espero un 200 con un
 * cuerpo que tenga id (entero), nombre (texto), categoria (texto), precio
 * (decimal) y stock (entero)". Pact levanta un mock provider, corre el cliente
 * real contra el mock y, si pasa, ESCRIBE el contrato en build/pacts/.
 *
 * Aqui NO se toca el provider real. El provider se verifica despues
 * (TiendaApiProviderPactTest).
 */
@ExtendWith(PactConsumerTestExt.class)
@PactTestFor(providerName = "tienda-api", pactMethod = "productoUno", pactVersion = PactSpecVersion.V3)
public class NotificacionesConsumerPactTest {

    @Pact(consumer = "notificaciones", provider = "tienda-api")
    public RequestResponsePact productoUno(PactDslWithProvider builder) {
        PactDslJsonBody cuerpo = new PactDslJsonBody()
                .integerType("id", 1)
                .stringType("nombre", "Tasty Concrete Chair")
                .stringType("categoria", "hogar")
                .decimalType("precio", 106.25)
                .integerType("stock", 5);

        return builder
                .given("existe el producto 1")
                .uponReceiving("una peticion del producto 1")
                .path("/api/productos/1")
                .method("GET")
                .willRespondWith()
                .status(200)
                .headers(java.util.Map.of("Content-Type", "application/json; charset=utf-8"))
                .body(cuerpo)
                .toPact();
    }

    @Test
    void obtieneElProductoConLaFormaEsperada(MockServer mockServer) throws Exception {
        ClienteProductos cliente = new ClienteProductos(mockServer.getUrl());

        String json = cliente.obtenerProductoJson(1);

        // El cliente funciona con la respuesta del mock => el contrato es valido.
        assertThat(json).contains("\"nombre\"").contains("\"precio\"");
    }
}
