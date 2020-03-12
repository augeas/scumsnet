# scumsnet

Scumsnet is a web-crawler based on [Scrapy](https://scrapy.org/) intended for investigating
transphobia on the [Mumsnet forums](https://en.wikipedia.org/wiki/Mumsnet#Criticisms). It
annotates posts based on the [Trans Media Watch](http://www.transmediawatch.org/)
[style-guide](http://www.transmediawatch.org/Documents/Media%20Style%20Guide.pdf), and also
on the [GLAAD](https://www.glaad.org/)
[Media Reference Guide](https://www.glaad.org/reference/transgender) and the
[TGEU](https://tgeu.org/)
[Guide For Journalists](https://tgeu.org/wp-content/uploads/2016/07/TGEU_journalistGuide16LR_singlepages.pdf)

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
"Run Spider".

You could just run the [curl](https://curl.haxx.se/) command in the terminal:

```sh
curl http://localhost:6800/schedule.json -d project=scumsnet -d spider=mumsnet
```
