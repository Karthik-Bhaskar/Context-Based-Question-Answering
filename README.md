## Context Based Question Answering 
[![Project Status: Active – The project has reached a stable, usable state and is being actively developed.](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active) [![GitHub license](https://img.shields.io/github/license/Karthik-Bhaskar/Context-Based-Question-Answering)](https://github.com/Karthik-Bhaskar/Context-Based-Question-Answering/blob/main/LICENSE)


**Context-Based Question Answering** is an easy-to-use **Extractive QA** search engine, which extracts answers to the question based on the provided context.


![](./docs_resources/CBQA_demo.gif)


### Table of contents
---

* [Introduction](#introduction) 
* [Motivation](#motivation)
* [Technologies](#technologies)
* [Languages](#languages)
* [Installation](#installation)
* [Demo](#demo)
* [Features](#features)
* [Status](#status)
* [License](#license)
* [Credits](#credits)
* [Citations](#citations)
* [Community Contribution](#community-contribution)
* [Contact](#contact)

### Introduction
---

>**Question answering**  (**QA**) is a computer science discipline within the fields of  [information retrieval](https://en.wikipedia.org/wiki/Information_retrieval "Information retrieval")  and  [natural language processing](https://en.wikipedia.org/wiki/Natural_language_processing "Natural language processing")  (NLP), which is concerned with building systems that automatically answer questions posed by humans in a  [natural language](https://en.wikipedia.org/wiki/Natural_language "Natural language").
>
>Source: [Wikipedia](https://en.wikipedia.org/wiki/Question_answering)

>**Extractive QA** is a popular task for natural language processing (NLP) research, where models must extract a short snippet from a document in order to answer a natural language question.
>
>  Source: [Facebook AI](https://ai.facebook.com/blog/research-in-brief-unsupervised-question-answering-by-cloze-translation/)



**Context-Based Question Answering (CBQA)** is an inference web-based Extractive QA search engine, mainly dependent on [Haystack](https://github.com/deepset-ai/haystack) and [Transformers](https://github.com/huggingface/transformers) library.

The CBQA application allows the user to add context and perform Question Answering(QA) in that context.

The main components in this application use [Haystack's](https://github.com/deepset-ai/haystack) core components,

> - **FileConverter**: Extracts pure text from files (pdf, docx, pptx, html and many more).
> -  **PreProcessor**: Cleans and splits texts into smaller chunks.
> -   **DocumentStore**: Database storing the documents, metadata and vectors for our search. We recommend Elasticsearch or FAISS, but have also more light-weight options for fast prototyping (SQL or In-Memory).
>   - **Retriever**: Fast algorithms that identify candidate documents for a given query from a large collection of documents. Retrievers narrow down the search space significantly and are therefore key for scalable QA. Haystack supports sparse methods (TF-IDF, BM25, custom Elasticsearch queries) and state of the art dense methods (e.g. sentence-transformers and Dense Passage Retrieval)
> - **Reader**: Neural network (e.g. BERT or RoBERTA) that reads through texts in detail to find an answer. The Reader takes multiple passages of text as input and returns top-n answers. Models are trained via  [FARM](https://github.com/deepset-ai/FARM)  or [Transformers](https://github.com/huggingface/transformers)  on SQuAD like tasks. You can just load a pretrained model from  [Hugging Face's model hub](https://huggingface.co/models)  or fine-tune it on your own domain data.
>
>Source: [Haystack's Key Components docs](https://github.com/deepset-ai/haystack/#key-components)

In CBQA the allowed formats for adding the context are,

 - Textual Context (Using the TextBox field)
 - File Uploads (.pdf, .txt, and .docx)

These contexts are uploaded to a temporary directory for each user for pre-processing and deletes after uploading them to **Elasticsearch,** which is the only **DocumentStore type** used in this system.

Each user has a separate Elasticsearch index to store the context documents. Using the **PreProcessor** and the **FileConverter** modules from [Haystack](https://github.com/deepset-ai/haystack), the pre-processing and the extraction of text from context files is done.

**Elasticsearcher Retriever** is used in CBQA to retrieve relevant documents based on the search query.

**Transformers-based Readers** are used to extracting answers from the retrieved documents. The Readers used in CBQA are the pre-trained Transformers models hosted on the [Hugging Face's model hub](https://huggingface.co/models) .

Currently, CBQA provides the interface to perform QA in **English** and **French**, using four Transformers based models,

 - BERT
 - RoBERTa
 - DistilBERT
 - CamemBERT

The interface provides an option to choose the inference device between CPU and GPU.

The output is in a tabular form containing the following headers,

-   **Answers** (Extracted answers based on the question and context)
-   **Context** (Specifies the context window, related to the answer)
-   **Document Title** (Specifies the title of context file, related to the answer)

### Motivation
---

The motivation to implement the CBQA project is to make an easy-to-use interface to perform Question Answering (QA) in multiple languages, with the option for using different pre-trained models.  Also, to enable organizations to use this project locally with minimal modifications or none.

### Technologies
---

* Python (version 3.7)
* Haystack  (version 0.7.0)
* Transformers (version 4.3.1)
* Elasticsearch (version 7.10)
* Flask  (version 1.1.2)
* Gunicorn (version 20.0.4)
* Bootstrap (version 4.5.3)
* jQuery (version 3.5.1)
* HTML, CSS, and JavaScript
* Docker

### Languages
---

``en: English``

``fr: French``

### Installation
---

Before starting the installation, clone this repository using the following commands in the terminal.

```console
$ git clone https://github.com/Karthik-Bhaskar/Context-Based-Question-Answering.git
````

```console
$ cd Context-Based-Question-Answering/
```

You can get started using one of the two options,

 1. [Installation using pip](#installation-using-pip)
 2. [Running as a docker container ](#running-as-a-docker-container )

#### Installation using pip
---


The main dependencies required to run the CBQA application is in the  [requirements.txt](./requirements.txt)

To install the dependencies,

1.  Create a Python virtual environment with Python version 3.7 and activate it
2.  Install dependency libraries using the following command in the terminal.
```console  
$ pip install -r requirements.txt
```

Before executing the CBQA application, please start the Elasticsearch server. Elasticsearch is the DocumentStore type used in this application. To download and install the Elasticsearch, please check [here](https://www.elastic.co/downloads/elasticsearch).

In case you are using the docker environment, run Elasticsearch on docker using the following commands in the terminal. If you want to install the docker engine on your machine, please check [here](https://docs.docker.com/get-docker/).
```console
$ docker pull docker.elastic.co/elasticsearch/elasticsearch:7.10.0
````
```console
$ docker run -p 9200:9200 -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch:7.10.0
```

Make sure the Elasticsearch server is running using the following command in the new terminal.
```console
$ curl http://localhost:9200
```
 You should get a response like the one below.
```console
{
"name" : "facddac422e8",
"cluster_name" : "docker-cluster",
"cluster_uuid" : "a4A3-yBhQdKBlpSDkpRelg",
"version" : {
"number" : "7.10.0",
"build_flavor" : "default",
"build_type" : "docker",
"build_hash" : "51e9d6f22758d0374a0f3f5c6e8f3a7997850f96",
"build_date" : "2020-11-09T21:30:33.964949Z",
"build_snapshot" : false,
"lucene_version" : "8.7.0",
"minimum_wire_compatibility_version" : "6.8.0",
"minimum_index_compatibility_version" : "6.0.0-beta1"
},
"tagline" : "You Know, for Search"
}
```


After installing the dependency libraries and starting the Elasticsearch server, you are good to go.

- _To run the application using a WSGI server like [Gunicorn](https://gunicorn.org)._ Use the following command in the new terminal.
  ```console
  $ gunicorn -w 1 --threads 4 app:app
  ```

  This runs the application in Gunicorn server on [http://localhost:8000](http://localhost:8000/) with a single worker and 4 threads.

- _To run the application in the [flask](https://flask.palletsprojects.com/en/1.1.x/) development server (Not recommended using this in production)_. Use the following command in the new terminal.
  ```console
  $ python app.py
  ```

  Now the application will be running in the flask development server on [http://localhost/5000](http://localhost/5000).

In the application execution cases above, you should see the below statement (date and time will be different) in the terminal after the application has started.
```console
User tracker thread started @  2021-03-04 18:25:20.803277
```

The above statement means that the thread handling the user connection has started, and the application is ready to accept users.


**Note**: When performing QA using pre-trained models, at first use, the selected model gets downloaded from the [Hugging Face's model hub](https://huggingface.co/models) this may take a while depending on your internet speed. If you are re-starting the application while you are testing, make sure to remove the auto-created temporary user directories in the project and the user index on Elasticsearch (Will be fixed soon)


#### Running as a docker container
---



To install the docker engine on your machine, please check [here](https://docs.docker.com/get-docker/).

This project includes the [docker-compose.yml](./docker-compose.yml) file describing the services to get started quickly. The specified services in the file are Elasticsearch, Kibana, and the CBQA application.

**Note**: Make sure to increase the resources (Memory) in your docker engine in case you are facing 137 exit code (out of memory).

The [docker image](https://hub.docker.com/repository/docker/karthikbhaskar/context-based-question-answering) for the CBQA application has already been built and hosted on [the docker hub](https://hub.docker.com/).

To start the complete package that includes Elasticsearch, Kibana, and CBQA application as a docker container.

Use the following command in the terminal from the root of this project directory to start the container.
```
$ docker-compose up
```

Please wait until all the services have started after pulling the images.

Make sure the Elasticsearch server is running using the following command in the new terminal.
```console
$ curl http://localhost:9200
```

You should get a response like the one below.
```console
{
"name" : "facddac422e8",
"cluster_name" : "docker-cluster",
"cluster_uuid" : "a4A3-yBhQdKBlpSDkpRelg",
"version" : {
"number" : "7.10.0",
"build_flavor" : "default",
"build_type" : "docker",
"build_hash" : "51e9d6f22758d0374a0f3f5c6e8f3a7997850f96",
"build_date" : "2020-11-09T21:30:33.964949Z",
"build_snapshot" : false,
"lucene_version" : "8.7.0",
"minimum_wire_compatibility_version" : "6.8.0",
"minimum_index_compatibility_version" : "6.0.0-beta1"
},
"tagline" : "You Know, for Search"
}
```

The CBQA application service in the docker container runs on [http://localhost:5000](http://localhost:5000/), the container name of the application will be **web-app**.

Elasticsearch service will be running on [http://localhost:9200](http://localhost:9200/), and Kibana service will be running on [http://localhost:5601](http://localhost:5601/).

**Note**: When performing QA using pre-trained models, at first use, the selected model gets downloaded from the [Hugging Face's model hub](https://huggingface.co/models) this may take a while depending on your internet speed. If you are re-starting the application while you are testing, make sure to remove the auto-created temporary user directories in the project and the user index on Elasticsearch (Will be fixed soon)

To stop the container, use the following command in the new terminal.
```console
$ docker-compose down
```

### Demo
---
*Full demo video on YouTube.*

[![Alt text](https://img.youtube.com/vi/vqy5XmDwKMQ/0.jpg)](https://youtu.be/vqy5XmDwKMQ)

### Features
---

Ready:
* Easy to use UI to perform QA
* Pre-trained models selection
* QA Language support (English and French)
* Simultaneous user handling support (While using WSGI server)

Future development:
* Ability to plugin large scale document corpus for the QA engine
* Generative QA support
* Additional QA Language support
* Improvising UI

### Status
---

[![Project Status: Active – The project has reached a stable, usable state and is being actively developed.](https://www.repostatus.org/badges/latest/active.svg)](https://www.repostatus.org/#active)

### License
---


[![GitHub license](https://img.shields.io/github/license/Karthik-Bhaskar/Context-Based-Question-Answering)](https://github.com/Karthik-Bhaskar/Context-Based-Question-Answering/blob/main/LICENSE)

### Credits
---

 - [Haystack](https://github.com/deepset-ai/haystack) ([deepset](https://deepset.ai))
 - [Transformers](https://github.com/huggingface/transformers) ([Hugging Face](https://huggingface.co))
 - Pre-trained Transformers Models on [Hugging Face's model hub](https://huggingface.co/models) 	
    - [roberta-base-squad2](https://huggingface.co/deepset/roberta-base-squad2) (deepset)
	- [bert-large-uncased-whole-word-masking-squad2](https://huggingface.co/deepset/bert-large-uncased-whole-word-masking-squad2)(deepset)
	- [distilbert-base-cased-distilled-squad](https://huggingface.co/distilbert-base-cased-distilled-squad)
	- [camembert-base-fquad](https://huggingface.co/illuin/camembert-base-fquad) (illuin)
- [Elasticsearch and Kibana](https://www.elastic.co)
- [Flask](https://flask.palletsprojects.com/en/1.1.x/)
- [Gunicorn](https://gunicorn.org)
- [Bootstrap](https://getbootstrap.com)
- [DropzoneJS](https://www.dropzonejs.com)
- [Docker](https://www.docker.com)
- [Sanjay R Kamath, PhD (Research Scientist, NLP)](https://twitter.com/sanjaykamath)
- Open-Source Community ❤️

### Citations
---

```bibtex
@article{DBLP:journals/corr/abs-1810-04805,
  author    = {Jacob Devlin and
               Ming{-}Wei Chang and
               Kenton Lee and
               Kristina Toutanova},
  title     = {{BERT:} Pre-training of Deep Bidirectional Transformers for Language
               Understanding},
  journal   = {CoRR},
  volume    = {abs/1810.04805},
  year      = {2018},
  url       = {http://arxiv.org/abs/1810.04805},
  archivePrefix = {arXiv},
  eprint    = {1810.04805},
  timestamp = {Tue, 30 Oct 2018 20:39:56 +0100},
  biburl    = {https://dblp.org/rec/journals/corr/abs-1810-04805.bib},
  bibsource = {dblp computer science bibliography, https://dblp.org}
}

```

```bibtex
@article{DBLP:journals/corr/abs-1907-11692,
  author    = {Yinhan Liu and
               Myle Ott and
               Naman Goyal and
               Jingfei Du and
               Mandar Joshi and
               Danqi Chen and
               Omer Levy and
               Mike Lewis and
               Luke Zettlemoyer and
               Veselin Stoyanov},
  title     = {RoBERTa: {A} Robustly Optimized {BERT} Pretraining Approach},
  journal   = {CoRR},
  volume    = {abs/1907.11692},
  year      = {2019},
  url       = {http://arxiv.org/abs/1907.11692},
  archivePrefix = {arXiv},
  eprint    = {1907.11692},
  timestamp = {Thu, 01 Aug 2019 08:59:33 +0200},
  biburl    = {https://dblp.org/rec/journals/corr/abs-1907-11692.bib},
  bibsource = {dblp computer science bibliography, https://dblp.org}
}
```

```bibtex
@article{DBLP:journals/corr/abs-1910-01108,
  author    = {Victor Sanh and
               Lysandre Debut and
               Julien Chaumond and
               Thomas Wolf},
  title     = {DistilBERT, a distilled version of {BERT:} smaller, faster, cheaper
               and lighter},
  journal   = {CoRR},
  volume    = {abs/1910.01108},
  year      = {2019},
  url       = {http://arxiv.org/abs/1910.01108},
  archivePrefix = {arXiv},
  eprint    = {1910.01108},
  timestamp = {Tue, 02 Jun 2020 12:48:59 +0200},
  biburl    = {https://dblp.org/rec/journals/corr/abs-1910-01108.bib},
  bibsource = {dblp computer science bibliography, https://dblp.org}
}
```

```bibtex
@article{DBLP:journals/corr/abs-1911-03894,
  author    = {Louis Martin and
               Benjamin M{\"{u}}ller and
               Pedro Javier Ortiz Su{\'{a}}rez and
               Yoann Dupont and
               Laurent Romary and
               {\'{E}}ric Villemonte de la Clergerie and
               Djam{\'{e}} Seddah and
               Beno{\^{\i}}t Sagot},
  title     = {CamemBERT: a Tasty French Language Model},
  journal   = {CoRR},
  volume    = {abs/1911.03894},
  year      = {2019},
  url       = {http://arxiv.org/abs/1911.03894},
  archivePrefix = {arXiv},
  eprint    = {1911.03894},
  timestamp = {Sun, 01 Dec 2019 20:31:34 +0100},
  biburl    = {https://dblp.org/rec/journals/corr/abs-1911-03894.bib},
  bibsource = {dblp computer science bibliography, https://dblp.org}
}
```

```bibtex
@article{dHoffschmidt2020FQuADFQ,
  title={FQuAD: French Question Answering Dataset},
  author={Martin d'Hoffschmidt and Maxime Vidal and Wacim Belblidia and Tom Brendl'e and Quentin Heinrich},
  journal={ArXiv},
  year={2020},
  volume={abs/2002.06071}
}
```



### Community Contribution
---

You are most welcome to contribute to this project. Be it a small typo correction or a feature enhancement. Currently, there is no structure to follow for contribution, but you can open an Issue under "Community contribution" or contact me to discuss it before getting started 🙂


### Contact
---

 [Karthik Bhaskar](https://www.karthikbhaskar.in/) - Feel free to contact me. 

 <a href="https://github.com/Karthik-Bhaskar" target="blank"><img align="center" src="https://cdn.jsdelivr.net/npm/simple-icons@3.0.1/icons/github.svg" alt="Karthik-Bhaskar" height="25" width="30" /></a>  <a href="https://twitter.com/karthik_bhaskar" target="blank"><img align="center" src="https://cdn.jsdelivr.net/npm/simple-icons@3.0.1/icons/twitter.svg" alt="karthik_bhaskar" height="25" width="30" /></a>  <a href="https://linkedin.com/in/contactkarthikbhaskar" target="blank"><img align="center" src="https://cdn.jsdelivr.net/npm/simple-icons@3.0.1/icons/linkedin.svg" alt="contactkarthikbhaskar" height="25" width="30" /></a>  
  
