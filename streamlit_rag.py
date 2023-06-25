import streamlit as st

from weaviatedb import WeaviateClient


def q_and_a_transformer(client: WeaviateClient, question: str):
    ask = {
        "question": question,
        "properties": ["question", "antwoord"],
        "rerank": True
    }

    return (
        client.client.query
        .get("RijksoverheidVac", [
            "question",
            "antwoord",
            "_additional {answer {hasAnswer certainty property result startPosition endPosition} }"
        ])
        .with_ask(content=ask)
        .with_limit(1)
        .do()
    )


def q_and_a_openai(client: WeaviateClient, question: str):
    ask = {
        "question": question,
        "properties": ["question", "antwoord"]
    }

    return (
        client.client.query
        .get("RijksoverheidVac", [
            "question",
            "antwoord",
            "_additional {answer {hasAnswer property result startPosition endPosition} }"])
        .with_ask(content=ask)
        .with_limit(1)
        .do()
    )


def generative_openai(client: WeaviateClient, query: str = "enter your query"):
    prompt = f"""Use the following pieces of context to answer the question at the end. If you don't know the 
    answer, just say that you don't know, don't try to make up an answer.

    {{antwoord}}

    Question: {query}
    Answer in Dutch:"""

    return (
        client.client.query
        .get("RijksoverheidVac", ["question", "antwoord"])
        .with_generate(single_prompt=prompt)
        .with_near_text({
            "concepts": [query]
        })
        .with_limit(5)
        .do()
    )


def write_q_and_a_response(answer_response):
    st.header("Question asked")
    st.write(the_query)
    print(answer_response)
    if answer_response["data"]["Get"]["RijksoverheidVac"]:

        st.header("Created answer")
        found_answer = answer_response["data"]["Get"]["RijksoverheidVac"][0]["_additional"]["answer"]
        if found_answer["hasAnswer"]:
            st.write(found_answer["result"])
        else:
            st.write("""*No answer found from text*""")

        write_expand_section(answer_response["data"]["Get"]["RijksoverheidVac"][0])
    else:
        st.write("No matching questions found")


def write_generative_response(answer_response):
    st.header("Question asked")
    st.write(the_query)
    print(answer_response)
    if answer_response["data"]["Get"]["RijksoverheidVac"]:

        st.header("Created answer")
        found_answer = answer_response["data"]["Get"]["RijksoverheidVac"][0]["_additional"]["generate"]
        if not found_answer["error"]:
            st.write(found_answer["singleResult"])
        else:
            st.write(f"""*Error*
            
            {found_answer["error"]}
            """)

        write_expand_section(answer_response["data"]["Get"]["RijksoverheidVac"][0])

    else:
        st.write("No matching questions found")


def write_expand_section(response_item):
    with st.expander("Open found question and answer"):
        st.header("Stored question and answer")
        st.subheader("Question")
        st.write(response_item["question"])
        st.subheader("Answer")
        st.write(response_item["antwoord"])


if __name__ == '__main__':
    local_client = WeaviateClient(overrule_weaviate_url="http://localhost:8080")
    remote_client = WeaviateClient()  # Uses the default url read from the environment variable WEAVIATE_URL

    st.title("Find me an answer to my question")

    which_solution = st.sidebar.radio("Which Weaviate module do you want to use?",
                                      ('QnA Custom', 'QnA OpenAI', 'Generative OpenAI'))

    preselect_query = st.selectbox('Select the sentence to use', [
        "Kan ik met iemand praten over dementie?",
        "hoeveel mag ik drinken als ik moet rijden?",
        "Met hoeveel alcohol mag ik deelnemen aan het verkeer",
        "what should I do to get my drivers license",
        "-- Your own --"
    ])

    if preselect_query == "-- Your own --":
        the_query = st.text_input('Your own question')
    else:
        the_query = preselect_query

    if the_query and which_solution == 'QnA Custom':
        write_q_and_a_response(
            q_and_a_transformer(client=local_client, question=the_query)
        )
    elif the_query and which_solution == 'QnA OpenAI':
        write_q_and_a_response(
            q_and_a_openai(client=remote_client, question=the_query)
        )
    elif the_query and which_solution == 'Generative OpenAI':
        write_generative_response(
            generative_openai(client=remote_client, query=the_query)
        )
    else:
        st.write("""Cannot select the right execution path, check the code.""")