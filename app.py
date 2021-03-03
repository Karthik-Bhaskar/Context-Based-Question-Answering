import os
import threading
import shutil
from datetime import timedelta, datetime
from flask import Flask, render_template, request, session, jsonify, url_for, redirect
from haystack.document_store.elasticsearch import *
from haystack.preprocessor.utils import convert_files_to_dicts
from haystack.preprocessor.cleaning import clean_wiki_text
from haystack import Finder
from haystack.retriever.sparse import ElasticsearchRetriever
from haystack.reader.transformers import TransformersReader
from elasticsearch import Elasticsearch

es = (
    Elasticsearch()
)  # Replace with Elasticsearch(["http://elasticsearch:9200/"], verify_certs=True) to build docker image
session_time = 60  # Session Timeout in Minutes
app = Flask(__name__)
app.secret_key = "cbqa_123"
app.permanent_session_lifetime = timedelta(minutes=session_time)
user_id = 0  # User ID to keep track w.r.t sessions and context data
current_users = dict()  # Used to store user id with time of login
user_doc_store = dict()  # Document store object of the user id
user_settings = dict()  # User settings for GPU and Pre-trained models choice

# Handles pre-processing the context and uploads the pre-processed context to Elasticsearch
# Each user is assigned with a separate Elasticsearch index starting with "user_{user_id}"
# Documents & textual context are deleted from them temp folder named with user_id under users dir after uploading to Es
def pre_process(user_id_key):
    uploads_dir = "users/" + str(user_id_key) + "/uploads/"
    try:
        es_result = es.search(
            index="user_" + str(user_id_key), body={"query": {"match_all": {}}}
        )
        no_docs = len(es_result["hits"]["hits"])

    except Exception as e:
        print(e)
        print("\n no documents in es")

    processed = convert_files_to_dicts(
        dir_path=uploads_dir, clean_func=clean_wiki_text, split_paragraphs=True
    )

    for doc in range(len(processed)):
        try:
            # print("\n Checking for duplicate docs ..")
            add_doc = True
            for each_doc in range(no_docs):
                doc_text = es_result["hits"]["hits"][each_doc]["_source"]["text"]
                doc_name = es_result["hits"]["hits"][each_doc]["_source"]["name"]
                doc_id = es_result["hits"]["hits"][each_doc]["_id"]
                if (
                    processed[doc]["meta"]["name"] == "context_file.txt"
                    and doc_name == "context_file.txt"
                ):
                    # print("Deleting context file to update with new changes ..")
                    es.delete(
                        index="user_" + str(user_id_key), doc_type="_doc", id=doc_id
                    )

                if processed[doc]["text"] == doc_text:
                    # print("\n There is a duplicate, So this document is not added ..")
                    add_doc = False
                    os.remove(uploads_dir + str(processed[doc]["meta"]["name"]))
                    break
            if add_doc:
                # print("\n No duplicates found, so adding this to es..")
                processed_lst = [processed[doc]]
                user_doc_store[user_id_key].write_documents(processed_lst)
                os.remove(uploads_dir + str(processed[doc]["meta"]["name"]))

        except Exception as e:
            print(e)
            # print("\n no documents in es")
            processed_lst = [processed[doc]]
            user_doc_store[user_id_key].write_documents(processed_lst)
            os.remove(uploads_dir + str(processed[doc]["meta"]["name"]))


# Handles setting up reader and retriever
def set_finder(user_id_key):
    if user_settings[user_id_key]["model"] == "roberta":
        model_path = (
            "deepset/roberta-base-squad2"  # Path of the models hosted in Hugging Face
        )
    elif user_settings[user_id_key]["model"] == "bert":
        model_path = "deepset/bert-large-uncased-whole-word-masking-squad2"
    elif user_settings[user_id_key]["model"] == "distilbert":
        model_path = "distilbert-base-uncased-distilled-squad"
    else:
        model_path = "illuin/camembert-base-fquad"

    retriever = ElasticsearchRetriever(document_store=user_doc_store[user_id_key])

    if user_settings[user_id_key]["gpu"] == "on":
        try:
            reader = TransformersReader(
                model_name_or_path=model_path, tokenizer=model_path, use_gpu=0
            )
        except Exception as e:
            print(e)
            print("GPU not available. Inferencing on CPU")
            reader = TransformersReader(
                model_name_or_path=model_path, tokenizer=model_path, use_gpu=-1
            )

    else:
        reader = TransformersReader(
            model_name_or_path=model_path, tokenizer=model_path, use_gpu=-1
        )

    finder = Finder(reader, retriever)

    return finder


# Handles deletion of context data completely from the server after the session time ends and deletes user id from dict
def user_session_timer():
    global current_users, session_time
    seconds_in_day = 24 * 60 * 60
    print("\n User tracker thread started @ ", datetime.now())
    while True:
        for user_id_key in current_users.copy():
            current_time = datetime.now()
            user_time = current_users[user_id_key]
            difference = current_time - user_time
            time_diff = divmod(
                difference.days * seconds_in_day + difference.seconds, 60
            )
            if time_diff[0] >= session_time:
                try:
                    del current_users[user_id_key]
                    del user_doc_store[user_id_key]
                    del user_settings[user_id_key]
                    shutil.rmtree("users/" + str(user_id_key))
                    es.indices.delete(
                        index="user_" + str(user_id_key), ignore=[400, 404]
                    )
                except OSError as e:
                    print("Error: %s - %s." % (e.filename, e.strerror))
                # print("\n Deleted user:", user_id_key, " @", datetime.now())


session_timer = threading.Thread(target=user_session_timer)
session_timer.start()


# Handles users w.r.t new session or already in session
@app.route("/")
def home():
    global user_id, current_users, session_time
    logging.info(
        "User connected at "
        + str(datetime.now())
        + " with IP: "
        + str(request.environ["REMOTE_ADDR"])
    )

    if "user" in session and session["user"] in current_users:
        user_id = session["user"]
        logged_on = current_users[user_id]
        current_time = datetime.now()
        diff_min_sec = (
            int(datetime.strftime(current_time, "%M"))
            - int(datetime.strftime(logged_on, "%M"))
        ) * 60
        diff_sec = int(datetime.strftime(current_time, "%S")) - int(
            datetime.strftime(logged_on, "%S")
        )
        diff_time = diff_min_sec + diff_sec
        time_left = (
            session_time * 60
        ) - diff_time  # For session timeout on client side
        return render_template("index.html", time_left=time_left)

    else:
        session.permanent = True
        current_time = datetime.now()
        user_id += 1
        current_users[user_id] = current_time
        session["user"] = user_id
        # print(current_users)
        if not os.path.exists("users/"):  # Creating user temp dir for uploading context
            os.makedirs("users/" + str(user_id))
            os.makedirs("users/" + str(user_id) + "/uploads")
        else:
            os.makedirs("users/" + str(user_id))
            os.makedirs("users/" + str(user_id) + "/uploads")
        user_doc_store[user_id] = ElasticsearchDocumentStore(
            host="localhost", index="user_" + str(user_id)
        )  # Change host = "elasticsearch" to build docker image
        user_settings[user_id] = {
            "gpu": "off",
            "model": "roberta",
        }  # Initial user settings

        logged_on = current_users[user_id]
        current_time = datetime.now()
        diff_min_sec = (
            int(datetime.strftime(current_time, "%M"))
            - int(datetime.strftime(logged_on, "%M"))
        ) * 60
        diff_sec = int(datetime.strftime(current_time, "%S")) - int(
            datetime.strftime(logged_on, "%S")
        )
        diff_time = diff_min_sec + diff_sec
        time_left = (
            session_time * 60
        ) - diff_time  # For session timeout on client side

        return render_template("index.html", time_left=time_left)


# Handles context documents uploads
@app.route("/upload_file", methods=["GET", "POST"])
def upload_file():
    global current_users

    if "user" in session:
        user_id_key = session["user"]
        if user_id_key in current_users:
            for f in request.files.getlist("file"):
                f.save(
                    os.path.join("users/" + str(user_id_key) + "/uploads", f.filename)
                )

            pre_process(user_id_key)

            return render_template("index.html")

        else:
            return redirect(url_for("session_timeout"))

    else:
        return redirect(url_for("session_timeout"))


# Handles context added through the textbox
@app.route("/context", methods=["POST"])
def context():
    if "user" in session:
        user_id_key = session["user"]
        if user_id_key in current_users:
            text_context = request.form["context"]
            context_file = open(
                "users/" + str(user_id_key) + "/uploads/context_file.txt", "w"
            )
            context_file.write(text_context)
            context_file.close()
            pre_process(user_id_key)
            return jsonify({"output": "" + text_context})

        else:
            return render_template("session_out.html")

    else:
        return redirect(url_for("session_timeout"))


# Provides extracted answers for the posted question
@app.route("/question", methods=["POST"])
def question():
    if "user" in session:
        user_id_key = session["user"]
        if user_id_key in current_users:
            query_question = request.form["question"]
            es_stats = es.indices.stats(index="user_" + str(user_id_key))
            user_index_size = es_stats["_all"]["primaries"]["store"]["size_in_bytes"]
            if (
                user_index_size == 208
            ):  # To check if index in Es is empty. 208 bytes is default index size without docs
                return jsonify({"error": "add context"})

            finder = set_finder(user_id_key)
            answers_dict = finder.get_answers(
                question=query_question, top_k_retriever=5, top_k_reader=5
            )
            unique_answers = list()
            output = list()
            if len(answers_dict["answers"]) > 0:
                for i in range(len(answers_dict["answers"])):
                    if (
                        answers_dict["answers"][i]["answer"] is not None
                        and answers_dict["answers"][i]["answer"] not in unique_answers
                    ):
                        temp_dict = answers_dict["answers"][i]
                        remove = (
                            "score",
                            "probability",
                            "offset_start",
                            "offset_end",
                            "document_id",
                        )
                        unique_answers.append(temp_dict["answer"])
                        if temp_dict["meta"]["name"] == "context_file.txt":
                            temp_dict["meta"]["name"] = "Textual Context"
                        temp_dict["meta"] = temp_dict["meta"]["name"]
                        output.append(temp_dict)
                        for key in remove:
                            if key in temp_dict:
                                del temp_dict[key]

            else:
                output = [
                    {"answer": "No Answers found ..", "context": " ", "meta": " "},
                ]

            return jsonify({"output": output})

        else:
            return render_template("session_out.html")


# Handles GPU setting changes.
@app.route("/gpu", methods=["POST"])
def gpu():
    if "user" in session:
        user_id_key = session["user"]
        if user_id_key in current_users:
            if user_settings[user_id_key]["gpu"] == "on":
                user_settings[user_id_key]["gpu"] = "off"
            else:
                user_settings[user_id_key]["gpu"] = "on"
    return jsonify({"output": "gpu status changed"})


# Handles pre-trained model choice setting changes.
@app.route("/models", methods=["POST"])
def models():
    if "user" in session:
        user_id_key = session["user"]
        if user_id_key in current_users:
            user_settings[user_id_key]["model"] = request.form["model"]
    return jsonify({"output": "model changed"})


# Handles session timeout redirection
@app.route("/session_timeout")
def session_timeout():
    return render_template("session_out.html")


# Handles removing of session identifier from session dict, This works only when app tab is open until session completes
@app.route("/session_out", methods=["POST"])
def session_out():
    session.pop("user", None)
    return redirect(url_for("session_timeout"))


# Comment the below block in case of building a docker image or running on WSGI server like gunicorn
if __name__ == "__main__":
    app.run(host="0.0.0.0")
