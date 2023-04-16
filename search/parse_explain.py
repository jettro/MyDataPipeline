import re

SPACER = "   "


def parse_explain(explain, level: int = 0):
    desc = explain["description"]
    prepend = SPACER * level
    if desc in ["max of:", "sum of:"]:
        print(f'{prepend}{explain["value"]} is the {desc}')
        # Loop over all items to take the maximum from
        for max_details in explain["details"]:
            parse_explain(explain=max_details, level=level + 1)
    elif desc.startswith("weight"):
        print(f'{prepend}{explain["value"]} for {parse_weight(desc)}')
        parse_weight_details(explain["details"], level)
    else:
        print(f'{prepend}No handler yet for {desc}')
        for details in explain["details"]:
            parse_explain(explain=details, level=level + 1)


def parse_weight(weight_desc: str):
    # weight(description:dress in 1) [PerFieldSimilarity], result of:
    return re.search(r'(?<=\().+(?= in \d+\))', weight_desc, ).group(0)


def parse_weight_details(weight_details, level: int = 0):
    boost = weight_details[0]["details"][0]["value"]
    idf = weight_details[0]["details"][1]
    tf = weight_details[0]["details"][2]

    prepend = SPACER * (level + 1)
    print(f'{prepend}BOOST: {boost}')
    idf_in_docs = idf["details"][0]["value"]
    idf_num_docs = idf["details"][1]["value"]
    print(f'{prepend}IDF: {idf["value"]} - {idf_in_docs} out of {idf_num_docs} docs')

    tf_freq_in_doc = tf["details"][0]["value"]
    tf_k1 = tf["details"][1]["value"]
    tf_b = tf["details"][2]["value"]
    tf_length_of_field = tf["details"][3]["value"]
    tf_avg_length_of_field = tf["details"][4]["value"]
    print(f'{prepend}TF: {tf["value"]} - {tf_freq_in_doc} times in field, with {tf_length_of_field} length to '
          f'{tf_avg_length_of_field} average')
