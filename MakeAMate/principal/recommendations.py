# La ponderación de los gustos en la puntuación respecto a las tags.
# Menor que uno: Los gustos se consideran menos importantes que las tags. Mayor que uno: Se consideran más.
PONDERACION_AFICIONES = 0.5

# El bonus por el que se multiplica la puntuación de un usuario si es premium.
# Debe ser mayor que uno.
BONUS_PREMIUM = 1.2

def rs_score(us_entrada,us_salida):
    tags_entrada = set(us_entrada.tags.all())
    tags_salida = set(us_salida.tags.all())

    aficiones_entrada = set(us_entrada.aficiones.all())
    aficiones_salida = set(us_salida.aficiones.all())

    es_premium = us_salida.es_premium()
    similitud = dice_coefficient(tags_entrada,tags_salida,aficiones_entrada,aficiones_salida)

    score =  similitud*BONUS_PREMIUM if es_premium else similitud
    #print(us_entrada.usuario.username + " - " + us_salida.usuario.username +": " + str(score) +","+str(es_premium))

    return score


def dice_coefficient(tag1, tag2, pref1, pref2):
    aficiones_comunes = len(pref1.intersection(pref2))
    aficiones_total = len(pref1) + len(pref2)

    tags_comunes  = len(tag1.intersection(tag2))
    tags_total = len(tag1) + len(tag2)

    interseccion_total = tags_comunes + PONDERACION_AFICIONES*aficiones_comunes
    suma_total = tags_total + PONDERACION_AFICIONES*aficiones_total

    #Si ninguno de los dos usuarios tiene gustos o preferencias, se devuelve por defecto 0.
    if(suma_total == 0):
        return 0

    return 2 * (interseccion_total) / (suma_total)