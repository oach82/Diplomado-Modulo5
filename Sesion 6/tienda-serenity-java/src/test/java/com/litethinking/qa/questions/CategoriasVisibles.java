package com.litethinking.qa.questions;

import net.serenitybdd.core.pages.WebElementFacade;
import net.serenitybdd.screenplay.Actor;
import net.serenitybdd.screenplay.Question;

import java.util.List;
import java.util.stream.Collectors;

import static com.litethinking.qa.ui.PaginaTienda.TARJETAS_VISIBLES_CATEGORIA;

/**
 * Devuelve la categoria (atributo data-categoria) de cada tarjeta visible.
 * Sirve para verificar que el filtro dejo SOLO productos de una categoria.
 */
public class CategoriasVisibles implements Question<List<String>> {

    @Override
    public List<String> answeredBy(Actor actor) {
        List<WebElementFacade> tarjetas = TARJETAS_VISIBLES_CATEGORIA.resolveAllFor(actor);
        return tarjetas.stream()
                .map(e -> e.getAttribute("data-categoria"))
                .collect(Collectors.toList());
    }

    public static CategoriasVisibles lista() {
        return new CategoriasVisibles();
    }
}
