package com.litethinking.qa.questions;

import net.serenitybdd.screenplay.Actor;
import net.serenitybdd.screenplay.Question;
import net.serenitybdd.screenplay.questions.Text;

import static com.litethinking.qa.ui.PaginaTienda.CONTADOR_CARRITO;

/** Devuelve el numero que muestra el contador del carrito. */
public class ContadorCarrito implements Question<Integer> {

    @Override
    public Integer answeredBy(Actor actor) {
        String valor = Text.of(CONTADOR_CARRITO).answeredBy(actor).trim();
        return valor.isEmpty() ? 0 : Integer.parseInt(valor);
    }

    public static ContadorCarrito valor() {
        return new ContadorCarrito();
    }
}
