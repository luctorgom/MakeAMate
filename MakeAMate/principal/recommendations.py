PONDERACION_TAGS = 0.5
PONDERACION_AFICIONES = 0.2
PONDERACION_PREMIUM = 0.3

def rs_score(us_entrada,us_salida):
    tags_entrada = us_entrada.tags.all()
    tags_salida = us_salida.tags.all()
    similitud_tags = dice_coefficient(set(tags_entrada),set(tags_salida))

    gustos_entrada = us_entrada.aficiones.all()
    gustos_salida = us_salida.aficiones.all()
    similitud_gustos = dice_coefficient(set(gustos_entrada),set(gustos_salida))

    es_premium = 0 if us_salida.es_premium else 1

    score =  similitud_tags*PONDERACION_TAGS + similitud_gustos*PONDERACION_AFICIONES + es_premium*PONDERACION_PREMIUM

    score = score if score<=1.0 else 1.0
    #print(us_entrada.usuario.username + " - " + us_salida.usuario.username +": " + str(score) +","+str(es_premium))

    return score


def dice_coefficient(set1, set2):
    return 2 * len(set1.intersection(set2)) / (len(set1) + len(set2))