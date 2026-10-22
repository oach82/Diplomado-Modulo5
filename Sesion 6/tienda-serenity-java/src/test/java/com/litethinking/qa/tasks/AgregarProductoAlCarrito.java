package com.litethinking.qa.tasks;

import net.serenitybdd.screenplay.Actor;
import net.serenitybdd.screenplay.Performable;
import net.serenitybdd.screenplay.Task;
import net.serenitybdd.screenplay.actions.Click;

import static com.litethinking.qa.ui.PaginaTienda.botonAgregar;

/** Hace clic en 'Agregar al carrito' del producto indicado. */
public class AgregarProductoAlCarrito implements Performable {

    private final int productoId;

    public AgregarProductoAlCarrito(int productoId) {
        this.productoId = productoId;
    }

    @Override
    public <T extends Actor> void performAs(T actor) {
        actor.attemptsTo(
                Click.on(botonAgregar(productoId))
        );
    }

    public static Performable conId(int productoId) {
        return Task.where("{0} agrega el producto " + productoId + " al carrito",
                new AgregarProductoAlCarrito(productoId));
    }
}
