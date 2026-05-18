import logging
import xml.etree.ElementTree as ET

def xml_fix(content: str) -> str:
    """
    Nettoyage XML basé sur règles indépendantes et réutilisables.

    Objectif :
    - appliquer plusieurs transformations XML de manière lisible
    - éviter les regex fragiles sur structure XML

    Règles :
    1) supprimer le contenu entre QUERY et REQUEST (frères XML)
    2) supprimer les blocs MACADDRPXE
    """

    root = ET.fromstring(content)

    # =========================================================
    # RÈGLE 1 : QUERY -> REQUEST
    # =========================================================
    def rule_query_request(parent):
        children = list(parent)
        i = 0

        while i < len(children):
            if children[i].tag == "QUERY":
                j = i + 1

                while j < len(children) and children[j].tag != "REQUEST":
                    parent.remove(children[j])
                    j += 1

                i = j
            else:
                rule_query_request(children[i])
                i += 1

    # =========================================================
    # RÈGLE 2 : SUPPRESSION MACADDRPXE
    # =========================================================
    def rule_macaddrpxe(parent):
        children = list(parent)

        for child in children:
            if child.tag == "MACADDRPXE":
                parent.remove(child)
            else:
                rule_macaddrpxe(child)

    # =========================================================
    # PIPELINE D'APPLICATION
    # =========================================================
    rule_query_request(root)
    rule_macaddrpxe(root)

    return ET.tostring(root, encoding="unicode")