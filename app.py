import os
from flask import render_template, request, redirect, url_for, Flask
from werkzeug import secure_filename
import json
from tqdm import tqdm
import pandas as pd
from haystack import Finder
from haystack.preprocessor.cleaning import clean_wiki_text
from haystack.preprocessor.utils import convert_files_to_dicts, fetch_archive_from_http
from haystack.reader.farm import FARMReader
from haystack.reader.transformers import TransformersReader
from haystack.utils import print_answers
from haystack.document_store.memory import InMemoryDocumentStore
from haystack.retriever.sparse import TfidfRetriever
from transformers import AutoModelForQuestionAnswering, AutoTokenizer, pipeline
from haystack.document_store.elasticsearch import ElasticsearchDocumentStore
from haystack.retriever.sparse import ElasticsearchRetriever


app = Flask(__name__)
model_path = "deepset/roberta-base-squad2"
uploads_dir = os.path.join('uploads')
document_store = InMemoryDocumentStore()
gpu = -1 #False
document_store_type = "InMemory"
gpu_check=""
model_selected_1 = "selected"
model_selected_2 = ""
model_selected_3 = ""

doc_checked_1 = ""
doc_checked_2 = "checked"
doc_checked_3 = ""

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}


def pre_process():
	dicts = convert_files_to_dicts(dir_path=uploads_dir, clean_func=clean_wiki_text, split_paragraphs=True)
	document_store.write_documents(dicts)


def set_finder():

	print("\n\n\n",model_path)
	print("\n\n")
	print(gpu)
	print("\n\n\n",document_store_type)
	print("\n\n\n",document_store)
	if(document_store_type == "InMemory"):
		retriever = TfidfRetriever(document_store=document_store)
	elif(document_store_type == "ElasticSearch"):
		retriever = ElasticsearchRetriever(document_store=document_store)
	try: 
		reader = TransformersReader(model_name_or_path=model_path,tokenizer=model_path,use_gpu = gpu)
	except:
		print("\n\nInference on CPU, as GPU is not available.\n\n")
		reader = TransformersReader(model_name_or_path=model_path,tokenizer=model_path,use_gpu = -1)
	finder = Finder(reader, retriever)
	return finder

@app.route('/context',methods = ['POST'])
def add_context():
	if request.method == 'POST':
		context_input = request.form['context_input']
		print("\n ----------------------- \n")
		return render_template('index.html',answer1="context added")

@app.route('/settings', methods = ['POST'])
def settings():
	global model_path, gpu, document_store, document_store_type, gpu_check, model_selected_1, model_selected_2, model_selected_3, doc_checked_1, doc_checked_2, doc_checked_3
	if request.method == 'POST':
		try: 
			if(request.form['gpu'] == "on"):
				gpu = 0 #True
				gpu_check = "checked"
		except:
			gpu = -1 # False
			gpu_check = ""

		pre_trained_model = request.form['pre_trained_model']
		if (pre_trained_model == "1"):
			model_path = "deepset/roberta-base-squad2"
			model_selected_1 = "selected"
			model_selected_2 = ""
			model_selected_3 = ""


		elif(pre_trained_model == "2"):
			model_path = "deepset/bert-large-uncased-whole-word-masking-squad2"
			model_selected_2 = "selected"
			model_selected_1 = ""
			model_selected_3 = ""


		elif(pre_trained_model == "3"):
			model_path = "distilbert-base-uncased-distilled-squad"
			model_selected_3 = "selected"
			model_selected_2 = ""
			model_selected_1 = ""


		else:
			model_path = "deepset/roberta-base-squad2"
			model_selected_1 = "selected"
			model_selected_2 = ""
			model_selected_3 = ""




		document_store_type = request.form['gridRadios']
		if(document_store_type == "ElasticSearch"):
			document_store = ElasticsearchDocumentStore(host="localhost", username="", password="", index="document")
			doc_checked_1 = "checked"
			doc_checked_2 = ""
			doc_checked_3 = ""

			pre_process()
			print(document_store)
		elif(document_store_type == "InMemory"):
			document_store = InMemoryDocumentStore()
			doc_checked_1 = ""
			doc_checked_2 = "checked"
			doc_checked_3 = ""

			pre_process()
			print(document_store)

		else:
			document_store = InMemoryDocumentStore()
			doc_checked_1 = ""
			doc_checked_2 = "checked"
			doc_checked_3 = ""

			pre_process()


		return render_template('index.html', answer1 = "settings changed",gpu_check=gpu_check, selected_1= model_selected_1,selected_2= model_selected_2,selected_3= model_selected_3, doc_checked_1 = doc_checked_1, doc_checked_2 = doc_checked_2, doc_checked_3 = doc_checked_3)


@app.route('/question', methods = ['POST'])
def answer():
	ans1 = ""
	if request.method == 'POST':
		print("\n\n\n",model_path)
		print("\n\n")

		finder = set_finder()
		question = request.form['question_input']
		prediction = finder.get_answers(question=question, top_k_retriever=5, top_k_reader=5)
		#ans1 = prediction['answers'][1]['answer']
		for i in range(4):
			if(prediction['answers'][i]['answer'] != None):
				ans1 = prediction['answers'][i]['answer']

		print(prediction['answers'])
		return render_template('index.html', answer1 = ans1, gpu_check=gpu_check, selected_1= model_selected_1,selected_2= model_selected_2,selected_3= model_selected_3, doc_checked_1 = doc_checked_1, doc_checked_2 = doc_checked_2, doc_checked_3 = doc_checked_3)




def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
@app.route('/', methods = ['GET', 'POST'])
def upload_file():

	if request.method == 'POST':

		if(request.files['file'] and request.form['context_input']):
				f = request.files['file']
				f.save(os.path.join(uploads_dir, secure_filename(f.filename)))
				context_input = request.form['context_input']
				context_file = open("./uploads/context_file.txt", "w")
				context_file.write(context_input)
				context_file.close()
				pre_process()

		elif(request.files['file']):
				f = request.files['file']
				f.save(os.path.join(uploads_dir, secure_filename(f.filename)))
				pre_process()

		elif(request.form['context_input']):
			context_input = request.form['context_input']
			context_file = open("./uploads/context_file.txt", "w")
			context_file.write(context_input)
			context_file.close()
			pre_process()





		return render_template('index.html', file=" Context was added",gpu_check=gpu_check,selected_1= model_selected_1,selected_2= model_selected_2,selected_3= model_selected_3, doc_checked_1 = doc_checked_1, doc_checked_2 = doc_checked_2, doc_checked_3 = doc_checked_3)

	if request.method == 'GET':
		return render_template('index.html', file="Choose PDF", gpu_check=gpu_check, selected_1= model_selected_1,selected_2= model_selected_2,selected_3= model_selected_3, doc_checked_1 = doc_checked_1, doc_checked_2 = doc_checked_2, doc_checked_3 = doc_checked_3)

if __name__ == '__main__':
	print("\n\n\n",model_path)
	print("\n\n")

	app.debug = True
	app.run(host='0.0.0.0',port=8087)







# Configure Flask app and the logo uploa