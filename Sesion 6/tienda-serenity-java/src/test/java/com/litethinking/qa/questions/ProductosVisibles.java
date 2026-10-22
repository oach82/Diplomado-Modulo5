package com.litethinking.qa.questions;

import net.serenitybdd.screenplay.Actor;
import net.serenitybdd.screenplay.Question;

import static com.litethinking.qa.ui.PaginaTienda.TARJETAS_PRODUCTO;

/** Cuenta cuantas tarjetas de producto hay visibles en el grid. */
public class ProductosVisibles implements Question<Integer> {

    @Override
    public Integer answeredBy(Actor actor) {
        return TARJETAS_PRODUCTO.resolveAllFor(actor).size();
    }

    public static ProductosVisibles cantidad() {
        return new ProductosVisibles();
    }
}
