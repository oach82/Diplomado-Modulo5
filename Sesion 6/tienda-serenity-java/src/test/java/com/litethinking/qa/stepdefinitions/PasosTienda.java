package com.litethinking.qa.stepdefinitions;

import com.litethinking.qa.questions.CategoriasVisibles;
import com.litethinking.qa.questions.ContadorCarrito;
import com.litethinking.qa.questions.ProductosVisibles;
import com.litethinking.qa.tasks.AbrirLaHome;
import com.litethinking.qa.tasks.AgregarProductoAlCarrito;
import com.litethinking.qa.tasks.FiltrarPorCategoria;
import io.cucumber.java.es.Cuando;
import io.cucumber.java.es.Dado;
import io.cucumber.java.es.Entonces;
import net.serenitybdd.screenplay.Actor;
import net.serenitybdd.screenplay.actors.OnStage;
import net.serenitybdd.screenplay.actors.OnlineCast;

import java.util.List;

import static net.serenitybdd.screenplay.GivenWhenThen.seeThat;
import static org.assertj.core.api.Assertions.assertThat;
import static org.hamcrest.Matchers.equalTo;
import static org.hamcrest.Matchers.greaterThan;

/** Steps de Cucumber mapeados a tareas/preguntas Screenplay. */
public class PasosTienda {

    @Dado("que {actor} abre la home de la tienda")
    public void abreLaHome(Actor actor) {
        actor.attemptsTo(AbrirLaHome.laHome());
    }

    @Cuando("{actor} filtra el catálogo por la categoría {string}")
    public void filtraPorCategoria(Actor actor, String categoria) {
        actor.attemptsTo(FiltrarPorCategoria.llamada(categoria));
    }

    @Cuando("{actor} agrega el producto {int} al carrito")
    public void agregaProducto(Actor actor, int productoId) {
        actor.attemptsTo(AgregarProductoAlCarrito.conId(productoId));
    }

    @Entonces("{actor} solo ve productos de la categoría {string}")
    public void soloVeCategoria(Actor actor, String categoria) {
        List<String> categorias = actor.asksFor(CategoriasVisibles.lista());
        assertThat(categorias)
                .as("todas las tarjetas visibles deben ser de la categoria '%s'", categoria)
                .isNotEmpty()
                .allMatch(c -> c.equalsIgnoreCase(categoria));
    }

    @Entonces("la cantidad de productos visibles es mayor que cero")
    public void hayProductosVisibles() {
        OnStage.theActorInTheSpotlight().should(
                seeThat("cantidad de productos", a -> a.asksFor(ProductosVisibles.cantidad()), greaterThan(0))
        );
    }

    @Entonces("el contador del carrito muestra {int}")
    public void elContadorMuestra(int esperado) {
        OnStage.theActorInTheSpotlight().should(
                seeThat("contador del carrito", a -> a.asksFor(ContadorCarrito.valor()), equalTo(esperado))
        );
    }
}
