package com.litethinking.qa.stepdefinitions;

import io.cucumber.java.Before;
import net.serenitybdd.screenplay.abilities.BrowseTheWeb;
import net.serenitybdd.screenplay.actors.OnStage;
import net.serenitybdd.screenplay.actors.OnlineCast;

/**
 * Prepara el "escenario" Screenplay antes de cada escenario Cucumber.
 * El cast online dota a cada actor de la habilidad BrowseTheWeb con el
 * WebDriver gestionado por Serenity (que a su vez usa Healenium si esta activo).
 */
public class EscenarioHooks {

    @Before
    public void prepararEscenario() {
        OnStage.setTheStage(new OnlineCast());
    }
}
