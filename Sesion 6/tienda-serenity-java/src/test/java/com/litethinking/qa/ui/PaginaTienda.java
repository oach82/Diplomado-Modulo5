package com.litethinking.qa.ui;

import net.serenitybdd.screenplay.targets.Target;

/**
 * Localizadores (Targets) de la Tienda, centralizados en un solo lugar.
 *
 * DEMO DE SELF-HEALING (ejercicio del Dia 6):
 * El escenario correcto NO es cambiar el selector aqui (eso crearia un selector
 * nuevo sin historial). El escenario es: un desarrollador cambia el HTML de la
 * app (ej. renombra data-testid='filtro-categoria' a 'selector-categoria' en
 * app-tienda/public/index.html). Este Target SIGUE buscando 'filtro-categoria',
 * que ya no existe. Con Healenium activo (via hlm-proxy), el proxy encuentra el
 * elemento mas parecido por similitud del arbol DOM (el <select> sigue ahi, solo
 * cambio su data-testid), sana el test y lo deja en verde, registrando el nuevo
 * localizador sugerido (ej. 'select#filtro-categoria', score ~0.96).
 *
 * Verificado: tras cambiar el data-testid en la app, el E2E sigue en verde y la
 * tabla healenium.healing_result registra success_healing=true, score=0.964.
 */
public class PaginaTienda {

    public static final Target FILTRO_CATEGORIA =
            Target.the("selector de categoria").locatedBy("[data-testid='filtro-categoria']");

    public static final Target GRID_PRODUCTOS =
            Target.the("grid de productos").locatedBy("[data-testid='grid-productos']");

    public static final Target TARJETAS_PRODUCTO =
            Target.the("tarjetas de producto").locatedBy("[data-testid^='producto-']");

    public static final Target CONTADOR_CARRITO =
            Target.the("contador del carrito").locatedBy("[data-testid='contador-carrito']");

    public static final Target SIN_RESULTADOS =
            Target.the("mensaje sin resultados").locatedBy("[data-testid='sin-resultados']");

    /** Boton 'Agregar al carrito' de un producto por su id. */
    public static Target botonAgregar(int productoId) {
        return Target.the("boton agregar producto " + productoId)
                .locatedBy("[data-testid='agregar-" + productoId + "']");
    }

    /** Atributo data-categoria de cada tarjeta, para verificar el filtro. */
    public static final Target TARJETAS_VISIBLES_CATEGORIA =
            Target.the("tarjetas con su categoria").locatedBy("[data-testid^='producto-']");
}
