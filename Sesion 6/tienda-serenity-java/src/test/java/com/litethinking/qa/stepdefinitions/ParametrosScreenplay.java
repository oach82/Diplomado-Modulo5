package com.litethinking.qa.stepdefinitions;

import io.cucumber.java.ParameterType;
import net.serenitybdd.screenplay.Actor;
import net.serenitybdd.screenplay.actors.OnStage;

/**
 * Define el parameter type {actor} que usan los steps en Gherkin.
 *
 * Sin esto, Cucumber lanza UndefinedParameterTypeException al ver '{actor}' en
 * las anotaciones de los steps. Aqui convertimos el NOMBRE escrito en el
 * escenario (ej. "Ana") en un Actor de Screenplay, tomandolo del escenario
 * (OnStage) que preparamos en EscenarioHooks.
 */
public class ParametrosScreenplay {

    @ParameterType(".*")
    public Actor actor(String nombre) {
        return OnStage.theActorCalled(nombre);
    }
}
