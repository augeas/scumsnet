# scumsnet

&copy; Giles Greenway, 2020

Scumsnet is a web-crawler based on [Scrapy](https://scrapy.org/) intended for investigating
transphobia on the [Mumsnet forums](https://en.wikipedia.org/wiki/Mumsnet#Criticisms). It
annotates posts based on the [Trans Media Watch](http://www.transmediawatch.org/)
[style-guide](http://www.transmediawatch.org/Documents/Media%20Style%20Guide.pdf), and also
on the [GLAAD](https://www.glaad.org/)
[Media Reference Guide](https://www.glaad.org/reference/transgender) and the
[TGEU](https://tgeu.org/)
[Guide For Journalists](https://tgeu.org/wp-content/uploads/2016/07/TGEU_journalistGuide16LR_singlepages.pdf).
(It should be noted that some of the terms deemed inappropriate may be used by trans people about themselves.
Their inclusion in forum posts might be quotations or reported speech, so they are not *automatically* an
indication of transphobia. However, their lack of inclusion does not imply that a post is *not* transphobic.)
[Named entities](https://spacy.io/usage/linguistic-features#named-entities) (e.g. people, places, and
organizations) are extracted using the [Spacy](https://spacy.io) Natural Language Processing (NLP) library,
which is also used to identify where the word "transgender" is used as a noun by
[part of speech tagging](https://spacy.io/usage/linguistic-features#pos-tagging).

## Getting Started


## Running Crawls

By default, the crawler searches Mumsnet for the terms "trans", "transgender", and "transsexual".
If the containers are running correctly, you should see
[SrapydWeb](https://github.com/my8100/scrapydweb) running at
[http://localhost:5000](http://localhost:5000). Select "Run Spider" on the left:

![Run Spider](/img/run_spider_0.png)

Choose the local [Scrapyd server](https://scrapyd.readthedocs.io/en/stable/), the "scumsnet" project,
and the "mumsnet" spider:

![Run Spider](/img/run_spider_1.png)

Finally, click "Check CMD" to generate the [curl](https://curl.haxx.se/) command, then run it by clicking
"Run Spider". You can examine the crawls progress by clicking "Jobs" to the left, where you can see how
many pages and items have been crawled, view logs or stop the crawl.

![Run Spider](/img/run_spider_2.png)

You could also just run the [curl](https://curl.haxx.se/) command in the terminal:

```sh
curl http://localhost:6800/schedule.json -d project=scumsnet -d spider=mumsnet
```

If you don't have [curl](https://curl.haxx.se/), you can run the command in the scumsnet
[Docker container](https://docs.docker.com/engine/reference/commandline/exec/)...

```sh
docker exec -ti scumsnet curl http://localhost:6800/schedule.json -d project=scumsnet -d spider=mumsnet
```

...or just run the supplied script:

```sh
./run_crawl.sh 
```

## Querying The Database

[Neo4J](https://neo4j.com/) should be running at [http://localhost:7474](http://localhost:7474).
You should be able to connect to the graph database without any credentials:

![connecting to Neo4J](/img/neo_connect.png)

Click the "Database" icon at the top-left. If a crawl has been running, you should see that the
database contains nodes and relationships:

![database info](/img/neo_info.png)

Clicking on a node or relationship type, for instance, "MENTIONS", will automatically run
a [cypher query](https://neo4j.com/docs/cypher-refcard/current/) and display it as a force-directed
graph. You will see nodes representing posts that mention named entities.

```
MATCH p=()-[r:MENTIONS]->() RETURN p LIMIT 25
```

!["MENTIONS" relationships](/img/neo_mentions.png)

Double-clicking on nodes will expand their other relationships.
Although it can be entertaining and occaisonally instructive to play with the graph in this way,
deeper insights will be found by using the [Cypher query language](https://neo4j.com/developer/cypher-query-language/).

### The Graph Model

Users POST posts that are POSTED_IN in threads:

```
(u:user)-[:POSTED]->(p:post)-[:POSTED_IN]->(t:thread)
```

A post is FLAGGED with annotations and MENTIONS entities: 

```
(p:post)-[:FLAGGED]->(a:annotation)
(p:post)-[:MENTIONS]->(e:entity)
```

The nodes have the following properties:

| Node       | Property |
|------------|----------|
| thread     | title    |
|            | url      |
|------------|----------|
| user       | name     |
|------------|----------|
| post       | text     |
|            | posted   |
|            | post_id  |
|------------|----------|
| entity     | text     |
|            | label    |
|------------|----------|
| annotation | text     |
|            | pos      |
|            | tag      |
|            | label    |
|------------|----------|

### Example Queries

To find the most common annotations:

```
MATCH (a:annotation) RETURN a.label AS annotation, COUNT(a.label) AS count ORDER BY count DESC LIMIT 20
```

To find the threads with the most posts:

```
MATCH (t:thread)<-[:POSTED_IN]-(p:post) RETURN t.title AS thread, COUNT(p) AS posts ORDER BY posts DESC LIMIT 20
```

To find the most active users in terms of their numbers of posts:

```
MATCH (u:user)-[:POSTED]->(p:post) RETURN u.name AS user, COUNT(p) AS posts ORDER BY posts DESC LIMIT 20
```

To finds the threads with the most annotations:

```
MATCH (t:thread)<-[:POSTED_IN]-(p:post)-[:FLAGGED]->(a:annotation)
RETURN t.title AS thread, COUNT(a) AS annotations ORDER BY annotations DESC LIMIT 20
```

To find the entities that occur in the most threads:

```
MATCH (t:thread)<-[:POSTED_IN]-(p:post)-[:MENTIONS]->(e:entity)
RETURN e.text AS entity, e.label AS label, COUNT(t) AS threads
ORDER BY threads DESC LIMIT 50
```

Entities labeled "PERSON" occuring in posts that
[contain](https://neo4j.com/docs/cypher-manual/current/clauses/where/#match-string-contains)
the word "Mermaids":

```
MATCH (p:post)-[:MENTIONS]->(e:entity) WHERE p.text CONTAINS 'Mermaids' AND e.label='PERSON'
RETURN e.text AS person, COUNT(p) AS posts ORDER BY posts DESC LIMIT 25
```

Annotations associated with posts that contain the word "Guardian":

```
MATCH (p:post)-[:FLAGGED]->(a:annotation) WHERE p.text CONTAINS 'Guardian' RETURN DISTINCT a.label
```

## Jupyter Notebooks

Although built on the minimal [Alpine Linux](https://alpinelinux.org/)
[Python 3.6 Docker image](https://hub.docker.com/_/python), since the "scumsnet" image
contains the Spacy library and its language model, it was never going to be especially small.
However, it's still smaller than the standard [Python 3.6 image](https://hub.docker.com/_/python).
Because of this, the
[Pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/), and [Bokeh](https://bokeh.org/)
libraries have been thrown in too. You can use them to play with the data with a
[Jupyter Notebook](https://jupyter.org/) server running at
[http://localhost:8888](http://localhost:8888). Its use is beyond the scope of this README, but
one can obtain a connection to the database with the [Neo4J Python driver](https://neo4j.com/developer/python/)
like so:

```python
from neo4j import GraphDatabase

neo_db = GraphDatabase.driver('bolt://scumsnet_neo:7687')
```
