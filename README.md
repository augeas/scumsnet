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
[Named entities](https://spacy.io/usage/linguistic-features#named-entities) (e.g. people, places organizations)
are extracted using the [Spacy](https://spacy.io) Natural Language Processing (NLP) library.

## Getting Started


## Running Crawls

If the containers are running correctly, you should see
[SrapydWeb](https://github.com/my8100/scrapydweb) at [http://localhost:5000](http://localhost:5000).
Select "Run Spider" on the left:

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
