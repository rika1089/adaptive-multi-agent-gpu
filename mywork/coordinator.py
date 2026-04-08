from metrics import add_query

routing_table = {
"text":"nlp",
"vision":"vision",
"logic":"reasoning"
}

def route_query(q):

    agent = routing_table[q["type"]]

    add_query(agent,q["query"])

    return agent