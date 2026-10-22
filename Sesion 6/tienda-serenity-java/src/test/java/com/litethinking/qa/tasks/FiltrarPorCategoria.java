package com.litethinking.qa.tasks;

import net.serenitybdd.screenplay.Actor;
import net.serenitybdd.screenplay.Performable;
import net.serenitybdd.screenplay.Task;
import net.serenitybdd.screenplay.actions.SelectFromOptions;

import static com.litethinking.qa.ui.PaginaTienda.FILTRO_CATEGORIA;

/** Selecciona una categoria en el filtro del catalogo. */
public class FiltrarPorCategoria implements Performable {

    private final String categoria;

    public FiltrarPorCategoria(String categoria) {
        this.categoria = categoria;
    }

    @Override
    public <T extends Actor> void performAs(T actor) {
        actor.attemptsTo(
                SelectFromOptions.byValue(categoria).from(FILTRO_CATEGORIA)
        );
    }

    public static Performable llamada(String categoria) {
        return Task.where("{0} filtra por la categoria '" + categoria + "'",
                new FiltrarPorCategoria(categoria));
    }
}
