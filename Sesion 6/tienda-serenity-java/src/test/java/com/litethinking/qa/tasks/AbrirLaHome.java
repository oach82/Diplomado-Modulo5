package com.litethinking.qa.tasks;

import net.serenitybdd.screenplay.Actor;
import net.serenitybdd.screenplay.Performable;
import net.serenitybdd.screenplay.Task;
import net.serenitybdd.screenplay.actions.Open;
import net.serenitybdd.screenplay.waits.WaitUntil;

import static com.litethinking.qa.ui.PaginaTienda.GRID_PRODUCTOS;
import static net.serenitybdd.screenplay.matchers.WebElementStateMatchers.isVisible;

/** Abre la home de la Tienda y espera a que el catalogo este cargado. */
public class AbrirLaHome implements Performable {

    @Override
    public <T extends Actor> void performAs(T actor) {
        actor.attemptsTo(
                Open.url(System.getProperty("baseUrl", "http://localhost:3000") + "/"),
                WaitUntil.the(GRID_PRODUCTOS, isVisible()).forNoMoreThan(15).seconds()
        );
    }

    public static Performable laHome() {
        return Task.where("{0} abre la home de la tienda", new AbrirLaHome());
    }
}
