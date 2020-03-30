# scumsnet

&copy; Giles Greenway, 2020.
[Licensed under the Apache License Version 2.0: http://www.apache.org/licenses/LICENSE-2.0.txt](http://www.apache.org/licenses/LICENSE-2.0.txt)

Scumsnet is a web-crawler based on [Scrapy](https://scrapy.org/) intended for investigating
transphobia on the [Mumsnet forums](https://en.wikipedia.org/wiki/Mumsnet#Criticisms).

Hopefully most interested parties should be able to run it, gather data, and query it with minimal
or no use of a shell terminal, if that is found to be intimidating. Otherwise, see the 
[example queries](###Example Queries) below.

It annotates posts based on the [Trans Media Watch](http://www.transmediawatch.org/)
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
[part of speech tagging](https://spacy.io/usage/linguistic-features#pos-tagging). Spacy quotes
Named Entity Recognition accuracy of its [smallest English language model](https://spacy.io/models/en)
of around 85%. The results of the crawl are stored in a [Neo4J graph database](https://neo4j.com/).

This project is intended for personal research, none of the containerized services have any authentication,
and you are STRONGLY DISCOURAGED from deploying them to any public-facing servers. Recall that the
warranty of this software according to its License is [NONE AT ALL](http://www.apache.org/licenses/LICENSE-2.0.txt).

## Getting Started

If you are vaguely comfortable with the terminal, one can run the crawler and database with Docker.
Start by [installing Docker](https://docs.docker.com/install/) and
[docker-compose](https://docs.docker.com/compose/install/). This can be done with *relative* ease
on Linux and Macs, and is *moderately* possible on Windows. Then, clone or 
[download and extract](https://github.com/augeas/scumsnet/archive/master.zip) this repository.
Start the containers with:

```sh
cd scumsnet
docker-compose pull
docker-compose up
```

It will take a little while to download the Docker images for the first time. You can shut the servers down with
control-c. 

## Can't Docker, Won't Docker

If you can't get Docker working, or are *intimidated* by terminal windows, you might be able to get things
working with [VirtualBox](https://www.virtualbox.org/). Having installed it, download the appliance image
["scumsnet_alpine_lite.ova"](https://scumsnet.s3.eu-west-2.amazonaws.com/scumsnet_alpine_lite.ova).
Run VirtualBox, from the "file" menu select "Import Appliance", and
choose the .ova file you downloaded. Accept the default settings, then click the green "Start" arrow.
The first time the virtual machine runs, it will have to download the Docker images from
Dockerhub, which will take a while. When you see the login prompt on the virtual machine terminal,
the various services should have started. (Neo4J might take a little longer to start. It's not
very relevant, but you can log-in as "root" with the password "scumsnet" if you like.)

![export csv](/img/vbox_terminal.png)

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

| Node       | Properties            |
|------------|-----------------------|
| thread     | title, url            |
| user       | name                  |
| post       | text, posted, post_id |
| entity     | text, label           |
| annotation | text, pos, tag, label | 


### Example Queries

These results are only examples, and will, of course, depend on how frequently
and for how long the crawler is run.

To find the most common annotations:

```
MATCH (a:annotation) RETURN a.label AS annotation, COUNT(a.label) AS count ORDER BY count DESC LIMIT 20
```

It's easy to export results as a comma-separated-variable (.csv) file that can
be loaded into a spreadsheet.
![export csv](/img/export_csv.png)


| annotation                  | count |
|-----------------------------|-------|
| biologically (fe)male       |   678 |
| transgender as a noun       |   616 |
| transgenderism              |   371 |
| scare-quotes                |   328 |
| passing                     |   263 |
| post-op                     |   252 |
| sex-change                  |   223 |
| transgendered               |   157 |
| become a (wo)man            |   147 |
| biological (wo)man          |   111 |
| pre-op                      |   103 |
| gender reassignment surgery |    98 |
| born a (wom)an              |    93 |
| stealth                     |    48 |
| gender identity disorder    |    47 |
| transsexuality              |    45 |
| tranny                      |    42 |
| gender dysmorphia           |    42 |
| sex reassignment surgery    |    39 |
| genetically (fe)male        |    18 |

To find the threads with the most posts:

| thread                                                                                   | posts |
|------------------------------------------------------------------------------------------|-------|
| Mumsnet moderation of trans rights and gender critical issues                            |  1875 |
| To be fed up beyond belief with the trans activists                                      |  1108 |
| Trans Widows Escape Committee 2- The Trans Widows Strike Back..                          |  1067 |
| 'to think if you have a penis, you do not belong in a woman's prison                     |  1041 |
| Trans unpeak moment                                                                      |  1025 |
| 'wedding, hen do, transgender                                                            |  1025 |
| 'I'm a trans man and local trans activist, AMA'                                          |  1000 |
| MNHQ transphobia guidelines part 2                                                       |  1000 |
| AIBU .... to open a transgender discussion thread for respectful debate !                |  1000 |
| Trans friendly thread!                                                                   |  1000 |
| Question about gender change                                                             |  1000 |
| Lesbians removed from Accenture inclusive trans event by 7 police officers               |  1000 |
| Trans people being allowed to compete against women in the Olympics                      |  1000 |
| Am I alone in wondering where the WOMEN wanting to trans are?                            |  1000 |
| Anti-trans vandals are plastering vile ‘women don’t have penises’ stickers around London |  1000 |
| Trans Widows escape committee                                                            |   988 |
| Trans Widows Escape Committee 3: Rise of the Trans Widows                                |   923 |
| Special trans taxi services to keep them safe                                            |   850 |
| WIBU to ask MNers who think Trans Women are 'Chicks With Dicks' to ...                   |   848 |
| My DD's first boyfriend is transgender and I feel weird about it.                        |   800 |

```
MATCH (t:thread)<-[:POSTED_IN]-(p:post) RETURN t.title AS thread, COUNT(p) AS posts ORDER BY posts DESC LIMIT 20
```

To find the most active users in terms of their numbers of posts:

```
MATCH (u:user)-[:POSTED]->(p:post) RETURN u.name AS user, COUNT(p) AS posts ORDER BY posts DESC LIMIT 20
```

| user                       | posts |
|----------------------------|-------|
| R0wantrees                 |  1796 |
| Datun                      |  1597 |
| Ereshkigal                 |  1449 |
| LangCleg                   |  1026 |
| TinselAngel                |   896 |
| AngryAttackKittens         |   821 |
| Italiangreyhound           |   513 |
| thebewilderness            |   486 |
| Pratchet                   |   474 |
| OldCrone                   |   471 |
| Bowlofbabelfish            |   464 |
| PencilsInSpace             |   420 |
| LordProfFekkoThePenguinPhD |   376 |
| RatRolyPoly                |   368 |
| ItsAllGoingToBeFine        |   344 |
| heresyandwitchcraft        |   336 |
| RedToothBrush              |   325 |
| NeurotrashWarrior          |   316 |
| kim147                     |   314 |
| CaptainKirksSpookyghost    |   313 |

To find the users with the most annotations:
(Where relevant, one should make allowances for reported speech, and trans
individuals using terms considered inappropriate by others about themselves.)

```
MATCH (u:user)-[:POSTED]->(p:post)-[:FLAGGED]->(a:annotation) 
R TURN u.name AS user, COUNT(a) AS annotations
ORDER BY annotations DESC LIMIT 20
```

| user                 |annotations |
|----------------------|------------|
| R0wantrees           |        180 |
| Datun                |        118 |
| Ereshkigal           |         60 |
| Beachcomber          |         46 |
| FloraFox             |         44 |
| Werksallhourz        |         42 |
| RatRolyPoly          |         42 |
| PencilsInSpace       |         36 |
| vesuvia              |         36 |
| OldCrone             |         32 |
| thebewilderness      |         32 |
| heresyandwitchcraft  |         32 |
| CharlieParley        |         31 |
| cantgetridofthekids  |         30 |
| Popchyk              |         30 |
| CoteDAzur            |         27 |
| flowersonthepiano    |         26 |
| Prawnofthepatriarchy |         25 |
| Jayceedove           |         21 |
| AllyMcBeagle         |         21 |

To find the threads with the most annotations:

```
MATCH (t:thread)<-[:POSTED_IN]-(p:post)-[:FLAGGED]->(a:annotation)
RETURN t.title AS thread, COUNT(a) AS annotations ORDER BY annotations DESC LIMIT 20
```

| thread                                                                    | annotations |
|---------------------------------------------------------------------------|-------------|
| 'to think if you have a penis, you do not belong in a woman's prison'     |         132 |
| Mumsnet moderation of trans rights and gender critical issues II          |          87 | 
| AIBU .... to open a transgender discussion thread for respectful debate ! |          82 |
| Am I alone in wondering where the WOMEN wanting to trans are?             |          81 |
| Feminist perspectives on transgendered people                             |          80 |
| Mumsnet moderation of trans rights and gender critical issues             |          76 |
| Trans media watch are lobbying mnhq                                       |          68 |
| Question about gender change                                              |          68 |
| I'm a trans man and local trans activist, AMA                             |          66 |
| Trans unpeak moment                                                       |          66 |
| MNHQ transphobia guidelines part 2                                        |          63 |
| Trans people being allowed to compete against women in the Olympics       |          58 |
| WIBU to ask MNers who think Trans Women are 'Chicks With Dicks' to ...    |          56 |
| born in the wrong body...a question about transgenderism'                 |          51 |
| Trans friendly thread!                                                    |          49 |
| To believe that trans is not a mental health condition                    |          48 |
| Can you all just lay off trans people                                     |          45 |
| Letter in the Times - Plea To The Trans Lobby from group of transsexuals  |          39 |
| Gender Critical Reference Thread                                          |          38 |
| 'Passing' trans                                                           |          36 |

To find the entities that occur in the most threads:

```
MATCH (t:thread)<-[:POSTED_IN]-(p:post)-[:MENTIONS]->(e:entity)
RETURN e.text AS entity, e.label AS label, COUNT(t) AS threads
ORDER BY threads DESC LIMIT 50
```

(As one would expect, the labels attached to entities are not always accurate.
Part-of-speech-tagging is not fool-proof, but most of the entities seem
*relevant*.)

| entity           | label    | threads |
|------------------|----------|---------|
| MNHQ             | ORG      |    1280 |
| Trans            | NORP     |    1193 |
| UK               | GPE      |    1163 |
| MN               | ORG      |     890 |
| TRA              | ORG      |     870 |
| Talk Guidelines  | ORG      |     869 |
| trans            | NORP     |     829 |
| OP               | ORG      |     731 |
| Stonewall        | GPE      |     522 |
| BBC              | ORG      |     517 |
| GC               | ORG      |     501 |
| Guardian         | ORG      |     499 |
| NHS              | ORG      |     473 |
| FWR              | ORG      |     472 |
| TW               | ORG      |     411 |
| US               | GPE      |     383 |
| Mumsnet          | NORP     |     355 |
| misogyny         | PERSON   |     342 |
| TIM              | PERSON   |     340 |
| Mermaids         | PERSON   |     338 |
| ID               | ORG      |     329 |
| transphobia      | GPE      |     329 |
| the Equality Act | LAW      |     310 | 
| Mumsnet          | PERSON   |     308 |
| Times            | ORG      |     298 |
| FFS              | ORG      |     279 |
| Scotland         | GPE      |     247 |
| Tara             | GPE      |     244 |
| LGB              | ORG      |     230 |
| Jesus            | PERSON   |     227 |
| London           | GPE      |     227 |
| lesbian          | NORP     |     221 |
| Karen White      | PERSON   |     214 |
| GRA              | ORG      |     211 |
| MTF              | ORG      |     206 |
| Debbie           | PERSON   |     199 |
| Christian        | NORP     |     194 |
| Datun            | ORG      |     191 |
| India            | GPE      |     189 |
| Mermaids         | NORP     |     177 |
| English          | LANGUAGE |     175 |
| Scottish         | NORP     |     172 |
| British          | NORP     |     168 |
| XX               | PERSON   |     167 |
| Kim              | PERSON   |     165 |
| Ireland          | GPE      |     158 |
| Lily             | PERSON   |     158 |
| Tinsel           | GPE      |     156 |
| Canada           | GPE      |     151 |
| Twitter          | PERSON   |     150 |

Entities labeled "PERSON" occuring in posts that
[contain](https://neo4j.com/docs/cypher-manual/current/clauses/where/#match-string-contains)
the word "Mermaids":

```
MATCH (p:post)-[:MENTIONS]->(e:entity) WHERE p.text CONTAINS 'Mermaids' AND e.label='PERSON'
RETURN e.text AS person, COUNT(p) AS posts ORDER BY posts DESC LIMIT 25
```

| person           | posts |
|------------------|-------|
| Mermaids         |   370 |
| Susie Green      |    31 |
| Susie            |    10 |
| Webberley        |     7 |
| Puberty          |     7 |
| Jane Fae         |     7 |
| Mermaids et al   |     7 |
| Polly Carmichael |     7 |
| Fox              |     7 |
| Tavistock        |     6 |
| Barbie           |     6 |
| Commons          |     6 |
| Stephen Whittle  |     5 |
| puberty blockers |     5 |
| Bernadette Wren  |     5 |
| www.bbc.co.uk    |     5 |
| James Kirkup     |     5 |
| Carmichael       |     5 |
| Joe              |     5 |
| Helen Webberley  |     4 |
| Elsa             |     4 |
| Munchausen       |     4 |
| Miranda Yardley  |     4 |
| Mum              |     4 |
| Helen            |     4 |

Annotations associated with posts that contain the word "Guardian":

```
MATCH (p:post)-[:FLAGGED]->(a:annotation) WHERE p.text CONTAINS 'Guardian' RETURN DISTINCT a.label
```

| label                       |
|-----------------------------|
| scare-quotes                |
| transgendered               |
| transgender as a noun       |
| become a (wo)man            |
| biologically (fe)male       |
| gender reassignment surgery |
| transgenderism              |
| gender bender               |
| passing                     |
| stealth                     |
| sex-change                  |
| gender realignment          |
| shim                        |

Threads with at least annotated post, ordered by the most recent post:

```
MATCH (t:thread)<-[:POSTED_IN]-(p:post)-[:FLAGGED]->(a:annotation)
RETURN DISTINCT t.title AS thread, MAX(p.posted) AS timestamp
ORDER BY timestamp DESC LIMIT 20
```

| thread                                                                                                            | timestamp            |
|-------------------------------------------------------------------------------------------------------------------|----------------------|
| Julie Bindel in The Spectator                                                                                     | 2020-03-14T11:12:37Z |
| Trans actors can play cis but cis can't play trans. Why am I bothering to try and see the sense?                  | 2020-03-14T08:04:19Z |
| Trans Widows Escape Committee 3: Rise of the Trans Widows                                                         | 2020-03-12T12:31:54Z |
| Lesbian, Bisexual and Trans Women’s Health Inequalities debate HoP yesterday (Tuesday 10th March).                | 2020-03-12T11:15:21Z |
| Gender-neutral passport rules are 'unlawful', Court of Appeal hears                                               | 2020-03-12T09:08:13Z |
| Center Parcs spa changing rooms again                                                                             | 2020-03-11T18:24:15Z |
| Zoe Williams opinion piece in The Guardian                                                                        | 2020-03-11T03:24:59Z |
| Piers Morgan with Lisa Nandy on Good Morning Britain                                                              | 2020-03-11T00:59:13Z |
| Suzanne Moore Guardian - new column                                                                               | 2020-03-10T12:59:16Z |
| Transphobic DD.                                                                                                   | 2020-03-10T12:01:00Z |
| Workplace cake sale to raise money for Mermaids                                                                   | 2020-03-10T11:48:31Z |
| Wow - BBC article on detransitioners                                                                              | 2020-03-10T09:11:04Z |
| Uni lesson plan on gender and discrimination                                                                      | 2020-03-09T20:10:07Z |
| Womxn discriminates against men!                                                                                  | 2020-03-09T18:52:46Z |
| Happy International Women's Day!                                                                                  | 2020-03-09T13:44:34Z |
| Transgender brains are more like their desired gender.                                                            | 2020-03-07T11:21:55Z |
| Suzanne Moore- The Guardian on Selina Todd                                                                        | 2020-03-06T22:59:06Z |
| Freddy McConnell appeal today (Transman who wants to be registered as their child's father) *Title edited by MNHQ | 2020-03-06T03:21:40Z |
| The BBC is promoting a trans doctor who seemingly only affirms patients' dysphoria                                | 2020-02-28T16:41:32Z |
| Moral Maze - Radio 4 8pm 19 Feb - Transgender Rights                                                              | 2020-02-24T03:21:02Z |

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
